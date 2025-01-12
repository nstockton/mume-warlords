# Copyright (C) 2025 Nick Stockton
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""The main module."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Any, Optional

# Third-party Modules:
import fastjsonschema
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


SCHEMA_VERSION: int = 1
URL: str = "https://mume.org/news/war"
OUTPUT_PATH: str = "warlords.json"
SCHEMA_FILE: str = f"warlords_v{SCHEMA_VERSION}.json.schema"
TIME_FORMAT: str = "Generated on %a %b %d %H:%M:%S %Y"
NUM_SIDES: int = 2
NUM_HEADERS: int = 8


def get_directory_path(*args: str) -> str:
	"""
	Retrieves the path of the directory where the program is located.

	Args:
		*args: Positional arguments to be passed to Path.joinpath after the directory path.

	Returns:
		The path.
	"""
	path = Path(sys.executable if getattr(sys, "frozen", None) else __file__)
	return str(path.parent.joinpath(*args).resolve())


@cache
def get_validator(schema_path: str) -> Callable[..., None]:  # type: ignore[misc]
	"""
	Retrieves the validator function for a given schema.

	Args:
		schema_path: The path to the schema.

	Returns:
		The validator function.
	"""
	with Path(schema_path).open(mode="rb") as file_obj:
		validator: Callable[..., None] = fastjsonschema.compile(json.load(file_obj))
	return validator


def validate(database: Mapping[str, Any], schema_path: str) -> None:
	"""
	Validates a database against a schema.

	Args:
		database: The database to be validated.
		schema_path: The location of the schema.
	"""
	validator = get_validator(schema_path)
	try:
		validator(database)
	except fastjsonschema.JsonSchemaException as e:
		print(f"Database failed validation: {e}", file=sys.stderr)
		sys.exit(1)


def save(data: Mapping[str, Any], output_path: str, schema_path: str) -> None:
	"""
	Saves data to disk in json format.

	Args:
		data: The data to be saved.
		output_path: The location where the data should be saved.
		schema_path: The location of the schema.
	"""
	lf: str = "\n"
	with Path(output_path).open(mode="w", encoding="utf-8", newline=lf) as file_obj:
		validate(data, schema_path)
		json.dump(data, file_obj, sort_keys=True, indent=2)
		file_obj.write(lf)


def split_list(lst: Sequence[Any], parts: Optional[int] = None) -> list[Sequence[Any]]:
	"""
	Splits a list into multiple parts.

	Args:
		lst: The list to split.
		parts: The number of parts the resulting list should be split into.

	Returns:
		A new list containing the multiple parts as lists.

	Raises:
		ValueError: Not enough parts.
	"""
	if parts is None:
		return [list(lst)]
	if parts < 1:
		raise ValueError("Number of parts must be 1 or greater.")
	length: int = len(lst)
	return [lst[i * length // parts : (i + 1) * length // parts] for i in range(parts)]


def get_warlords() -> dict[str, Any]:
	"""
	Retrieves the warlords information.

	Returns:
		The warlords information.

	Raises:
		RuntimeError: An error occurred while retrieving warlords information.
		ValueError: Invalid length.
	"""
	page = requests.get(URL, timeout=10.0)
	page.raise_for_status()
	soup = BeautifulSoup(page.text, "html.parser")
	war_status: str
	generated: str
	tag = soup.find("h2", string="War status")
	if not isinstance(tag, Tag):
		raise RuntimeError("War status heading not found.")  # NOQA: TRY004
	tag = tag.find_next_sibling("p")
	if not isinstance(tag, Tag):  # pragma: no cover
		raise RuntimeError("War status text not found.")  # NOQA: TRY004
	war_status, generated = tag.text.strip().rsplit("\n", 1)
	generated = " ".join(generated.split())  # Replace whitespace with single spaces.
	generated_timestamp: int = int(
		datetime.strptime(generated, TIME_FORMAT).replace(tzinfo=timezone.utc).timestamp()
	)
	table = soup.find("table", attrs={"class": "msg_body warlords"})
	if not isinstance(table, Tag):
		raise RuntimeError("Warlords table not found.")  # NOQA: TRY004
	rows = table.find_all("tr")
	side_of_war: list[str]
	side_of_war = [i.text.strip() for i in rows.pop(0).find_all("th")]
	if len(side_of_war) != NUM_SIDES:
		raise ValueError(f"Length of side_of_war was {len(side_of_war)}, should be {NUM_SIDES}.")
	headers: list[str]
	headers = [i.text.strip().lower() for i in rows.pop(0).find_all("th")]
	if len(headers) != NUM_HEADERS:
		raise ValueError(f"Length of headers was {len(headers)}, should be {NUM_HEADERS}.")
	warlords: list[dict[str, Any]]
	warlords = [{"description": i, "characters": []} for i in side_of_war]
	for row in rows:
		row_data: list[str] = [i.text.strip() for i in row.find_all("td")]
		characters: list[Sequence[str]] = split_list(row_data, len(side_of_war))
		for i, _side in enumerate(side_of_war):
			warlords[i]["characters"].append(dict(zip(headers, characters[i])))
	return {
		"generated": generated,
		"generated_timestamp": generated_timestamp,
		"schema_version": SCHEMA_VERSION,
		"war_status": war_status,
		"warlords": warlords,
	}


def run() -> None:
	"""Runs the program."""
	results: dict[str, Any] = get_warlords()
	save(results, OUTPUT_PATH, get_directory_path(SCHEMA_FILE))
