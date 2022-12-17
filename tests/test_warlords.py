# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import json
import os.path
import sys
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

# Third-party Modules:
import httpretty
from jsonschema.exceptions import ValidationError

# Warlords Modules:
from warlords.main import OUTPUT_PATH, SCHEMA_FILE, URL
from warlords.main import __file__ as WARLORDS_PATH
from warlords.main import get_directory_path, get_warlords, run, save, split_list, validate


with open("tests/examples/response.html", "r", encoding="utf-8") as file_obj:
	EXAMPLE_RESPONSE: str = file_obj.read()
with open("tests/examples/output.json", "r", encoding="utf-8") as file_obj:
	EXAMPLE_OUTPUT: str = file_obj.read()


class TestWarlords(TestCase):
	@patch("warlords.main.sys")
	def test_get_directory_path(self, mock_sys: Mock) -> None:
		subdirectory: tuple[str, ...] = ("level1", "level2")
		frozen_dir_name: str = os.path.dirname(sys.executable)
		frozen_output: str = os.path.realpath(os.path.join(frozen_dir_name, *subdirectory))
		mock_sys.frozen = True
		mock_sys.executable = sys.executable
		self.assertEqual(get_directory_path(*subdirectory), frozen_output)
		unfrozen_dir_name: str = os.path.dirname(WARLORDS_PATH)
		unfrozen_output: str = os.path.realpath(os.path.join(unfrozen_dir_name, *subdirectory))
		mock_sys.frozen = False
		self.assertEqual(get_directory_path(*subdirectory), unfrozen_output)

	def test_validate(self) -> None:
		schema_path: str = get_directory_path(SCHEMA_FILE)
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		validate(example_json, schema_path)
		with self.assertRaises(ValidationError):
			validate({"invalid": "invalid"}, schema_path)

	@patch("warlords.main.json.dump")
	@patch("warlords.main.validate")
	def test_save(self, mock_validate: Mock, mock_json_dump: Mock) -> None:
		schema_path: str = get_directory_path(SCHEMA_FILE)
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		with patch("warlords.main.open") as context:
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
		with httpretty.enabled(verbose=True, allow_net_connect=False):
			httpretty.register_uri(httpretty.GET, URL, status=200, body=EXAMPLE_RESPONSE)
			self.assertEqual(json.dumps(get_warlords(), sort_keys=True, indent=2), EXAMPLE_OUTPUT)
			self.assertEqual(len(httpretty.latest_requests()), 1)
			httpretty.reset()
			invalid_status_header = EXAMPLE_RESPONSE.replace("<h2>War status</h2>", "")
			httpretty.register_uri(httpretty.GET, URL, status=200, body=invalid_status_header)
			with self.assertRaises(RuntimeError):
				get_warlords()
			self.assertEqual(len(httpretty.latest_requests()), 1)
			httpretty.reset()
			invalid_table = EXAMPLE_RESPONSE.replace(
				'<table class="msg_body warlords">', '<table class="junk">'
			)
			httpretty.register_uri(httpretty.GET, URL, status=200, body=invalid_table)
			with self.assertRaises(RuntimeError):
				get_warlords()
			self.assertEqual(len(httpretty.latest_requests()), 1)
			httpretty.reset()
			invalid_sides = EXAMPLE_RESPONSE.replace("<th colspan=4>Armies of the West</th>", "")
			httpretty.register_uri(httpretty.GET, URL, status=200, body=invalid_sides)
			with self.assertRaises(ValueError):
				get_warlords()
			self.assertEqual(len(httpretty.latest_requests()), 1)
			httpretty.reset()
			invalid_headers = EXAMPLE_RESPONSE.replace("<th>Rank</th>", "")
			httpretty.register_uri(httpretty.GET, URL, status=200, body=invalid_headers)
			with self.assertRaises(ValueError):
				get_warlords()

	@patch("warlords.main.save")
	@patch("warlords.main.get_warlords")
	def test_run(self, mock_get_warlords: Mock, mock_save: Mock) -> None:
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		schema_path: str = get_directory_path(SCHEMA_FILE)
		mock_get_warlords.return_value = example_json
		run()
		mock_get_warlords.assert_called_once()
		mock_save.assert_called_once_with(example_json, OUTPUT_PATH, schema_path)
