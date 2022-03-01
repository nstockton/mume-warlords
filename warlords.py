# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Optional

# Third-party Modules:
import jsonschema
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


URL: str = "https://mume.org/news/war"
OUTPUT_PATH: str = "warlords.json"
SCHEMA_PATH: str = "warlords.json.schema"
TIME_FORMAT: str = "Generated on %a %b %d %H:%M:%S %Y"


def validate(data: Mapping[str, Any], schema_path: str) -> None:
	"""
	Validates data against a schema.

	Args:
		data: The data to be validated.
		schema_path: The location of the schema.
	"""
	with open(schema_path, "r", encoding="utf-8") as file_obj:
		schema: dict[str, Any] = json.load(file_obj)
	jsonschema.validate(data, schema)


def save(data: Mapping[str, Any], output_path: str, schema_path: str) -> None:
	"""
	Saves data to disk in json format.

	Args:
		data: The data to be saved.
		output_path: The location where the data should be saved.
		schema_path: The location of the schema.
	"""
	with open(output_path, "w", encoding="utf-8", newline="\r\n") as file_obj:
		validate(data, schema_path)
		json.dump(data, file_obj, sort_keys=True, indent=2)


def split_list(lst: Sequence[Any], parts: Optional[int] = None) -> list[Sequence[Any]]:
	"""
	Splits a list into multiple parts.

	Args:
		lst: The list to split.
		parts: The number of parts the resulting list should be split into.

	Returns:
		A new list containing the multiple parts as lists.
	"""
	if parts is None:
		return [list(lst)]
	elif parts < 1:
		raise ValueError("Number of parts must be 1 or greater.")
	length: int = len(lst)
	return [lst[i * length // parts : (i + 1) * length // parts] for i in range(parts)]


def get_warlords() -> dict[str, Any]:
	page = requests.get(URL)
	page.raise_for_status()
	soup = BeautifulSoup(page.text, "html.parser")
	war_status: str
	generated: str
	tag = soup.find("h2", text="War status")
	if not isinstance(tag, Tag):
		raise RuntimeError("War status heading not found.")
	tag = tag.find_next_sibling("p")
	if not isinstance(tag, Tag):  # pragma: no cover
		raise RuntimeError("War status text not found.")
	war_status, generated = tag.text.strip().rsplit("\n", 1)
	generated = " ".join(generated.split())  # Replace whitespace with single spaces.
	generated_timestamp: int = int(
		datetime.strptime(generated, TIME_FORMAT).replace(tzinfo=timezone.utc).timestamp()
	)
	table = soup.find("table", attrs={"class": "msg_body warlords"})
	if not isinstance(table, Tag):
		raise RuntimeError("Warlords table not found.")
	rows = table.find_all("tr")
	side_of_war: list[str]
	side_of_war = [i.text.strip() for i in rows.pop(0).find_all("th")]
	if len(side_of_war) != 2:
		raise ValueError(f"Length of side_of_war was {len(side_of_war)}, should be 2.")
	headers: list[str]
	headers = [i.text.strip().lower() for i in rows.pop(0).find_all("th")]
	if len(headers) != 8:
		raise ValueError(f"Length of headers was {len(headers)}, should be 8.")
	warlords: list[dict[str, Any]]
	warlords = [{"description": i, "characters": []} for i in side_of_war]
	for row in rows:
		row_data: list[str] = [i.text.strip() for i in row.find_all("td")]
		characters: list[Sequence[str]] = split_list(row_data, len(side_of_war))
		for i, side in enumerate(side_of_war):
			warlords[i]["characters"].append(dict(zip(headers, characters[i])))
	return {
		"war_status": war_status,
		"generated": generated,
		"generated_timestamp": generated_timestamp,
		"warlords": warlords,
	}


if __name__ == "__main__":
	save(get_warlords(), OUTPUT_PATH, SCHEMA_PATH)
