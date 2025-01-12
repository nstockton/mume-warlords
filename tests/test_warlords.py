# Copyright (C) 2025 Nick Stockton
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import json
import sys
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

# Third-party Modules:
from mocket import Mocket, Mocketizer
from mocket.mockhttp import Entry

# Warlords Modules:
from warlords.main import OUTPUT_PATH, SCHEMA_FILE, URL
from warlords.main import __file__ as WARLORDS_PATH  # NOQA: N812
from warlords.main import get_directory_path, get_warlords, run, save, split_list, validate


EXAMPLES_PATH: Path = Path(__file__).parent / "examples"
with (EXAMPLES_PATH / "response.html").open(encoding="utf-8") as file_obj:
	EXAMPLE_RESPONSE: str = file_obj.read()
with (EXAMPLES_PATH / "output.json").open(encoding="utf-8") as file_obj:
	EXAMPLE_OUTPUT: str = file_obj.read()


class TestWarlords(TestCase):
	@patch("warlords.main.sys")
	def test_get_directory_path(self, mock_sys: Mock) -> None:
		subdirectory: tuple[str, ...] = ("level1", "level2")
		frozen_dir_name: Path = Path(sys.executable).parent
		frozen_output: str = str(frozen_dir_name.joinpath(*subdirectory).resolve())
		mock_sys.frozen = True
		mock_sys.executable = sys.executable
		self.assertEqual(get_directory_path(*subdirectory), frozen_output)
		unfrozen_dir_name: Path = Path(WARLORDS_PATH).parent
		unfrozen_output: str = str(unfrozen_dir_name.joinpath(*subdirectory).resolve())
		mock_sys.frozen = False
		self.assertEqual(get_directory_path(*subdirectory), unfrozen_output)

	@patch("warlords.main.sys.stderr", Mock())  # Prevent error message output.
	def test_validate(self) -> None:
		schema_path: str = get_directory_path(SCHEMA_FILE)
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		validate(example_json, schema_path)
		with self.assertRaises(SystemExit) as cm:
			validate({"invalid": "invalid"}, schema_path)
		self.assertEqual(cm.exception.code, 1)

	@patch("warlords.main.json.dump")
	@patch("warlords.main.validate")
	def test_save(self, mock_validate: Mock, mock_json_dump: Mock) -> None:
		schema_path: str = get_directory_path(SCHEMA_FILE)
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		with patch("warlords.main.Path.open") as context:
			mock_file_obj: Mock = context.return_value.__enter__.return_value
			save(example_json, "__junk__.json", schema_path)
			mock_validate.assert_called_once_with(example_json, schema_path)
			mock_json_dump.assert_called_once_with(example_json, mock_file_obj, sort_keys=True, indent=2)

	def test_split_list(self) -> None:
		lst: list[int] = list(range(10))
		with self.assertRaises(ValueError):
			split_list(lst, 0)
		self.assertEqual(split_list(lst, None), [lst])
		self.assertEqual(split_list(lst, 1), [lst])
		self.assertEqual(split_list(lst, 2), [lst[:5], lst[5:]])

	def test_get_warlords(self) -> None:
		with Mocketizer(strict_mode=True):
			valid_headers = {"content-type": "text/html; charset=UTF-8"}
			Entry.single_register(Entry.GET, URL, body=EXAMPLE_RESPONSE, status=200, headers=valid_headers)
			self.assertEqual(json.dumps(get_warlords(), sort_keys=True, indent=2) + "\n", EXAMPLE_OUTPUT)
			self.assertEqual(len(Mocket.request_list()), 1)
			Mocket.reset()
			invalid_status_heading = EXAMPLE_RESPONSE.replace("<h2>War status</h2>", "")
			Entry.single_register(
				Entry.GET, URL, body=invalid_status_heading, status=200, headers=valid_headers
			)
			with self.assertRaises(RuntimeError):
				get_warlords()
			self.assertEqual(len(Mocket.request_list()), 1)
			Mocket.reset()
			invalid_table = EXAMPLE_RESPONSE.replace(
				'<table class="msg_body warlords">', '<table class="junk">'
			)
			Entry.single_register(Entry.GET, URL, body=invalid_table, status=200, headers=valid_headers)
			with self.assertRaises(RuntimeError):
				get_warlords()
			self.assertEqual(len(Mocket.request_list()), 1)
			Mocket.reset()
			invalid_sides = EXAMPLE_RESPONSE.replace("<th colspan=4>Armies of the West</th>", "")
			Entry.single_register(Entry.GET, URL, body=invalid_sides, status=200, headers=valid_headers)
			with self.assertRaises(ValueError):
				get_warlords()
			self.assertEqual(len(Mocket.request_list()), 1)
			Mocket.reset()
			invalid_rank = EXAMPLE_RESPONSE.replace("<th>Rank</th>", "")
			Entry.single_register(Entry.GET, URL, body=invalid_rank, status=200, headers=valid_headers)
			with self.assertRaises(ValueError):
				get_warlords()
			self.assertEqual(len(Mocket.request_list()), 1)

	@patch("warlords.main.save")
	@patch("warlords.main.get_warlords")
	def test_run(self, mock_get_warlords: Mock, mock_save: Mock) -> None:
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		schema_path: str = get_directory_path(SCHEMA_FILE)
		mock_get_warlords.return_value = example_json
		run()
		mock_get_warlords.assert_called_once()
		mock_save.assert_called_once_with(example_json, OUTPUT_PATH, schema_path)
