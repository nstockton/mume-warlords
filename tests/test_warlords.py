# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import httpretty
import json
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

# Third-party Modules:
from jsonschema.exceptions import ValidationError

# Warlords Modules:
from warlords import SCHEMA_PATH, URL, get_warlords, save, split_list, validate


with open("tests/examples/response.html", "r", encoding="utf-8") as file_obj:
	EXAMPLE_RESPONSE: str = file_obj.read()
with open("tests/examples/output.json", "r", encoding="utf-8") as file_obj:
	EXAMPLE_OUTPUT: str = file_obj.read()


class TestWarlords(TestCase):
	def test_validate(self) -> None:
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		validate(example_json, SCHEMA_PATH)
		with self.assertRaises(ValidationError):
			validate({"invalid": "invalid"}, SCHEMA_PATH)

	@patch("warlords.json.dump")
	@patch("warlords.validate")
	def test_save(self, mock_validate: Mock, mock_json_dump: Mock) -> None:
		example_json: dict[str, Any] = json.loads(EXAMPLE_OUTPUT)
		with patch("warlords.open") as context:
			mock_file_obj: Mock = context.return_value.__enter__.return_value
			save(example_json, "__junk__.json", SCHEMA_PATH)
			mock_validate.assert_called_once_with(example_json, SCHEMA_PATH)
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
