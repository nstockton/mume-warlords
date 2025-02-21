# mume-warlords

Exports the [warlords list][] from [MUME][] to JSON format.
Automatically generated data in JSON format can be found [here.][current warlords json]

## License And Credits

This project was created by [Nick Stockton,][Nick Stockton Github] and is licensed under the terms of the [Mozilla Public License, version 2.0.][MPL2]

## Installation

Install the [Python interpreter,][Python] and make sure it's in your path before running this package.

### Windows-specific Instructions

Execute the following commands from the root directory of this repository to install the module dependencies.
```
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade --require-hashes --requirement requirements-uv.txt
uv sync
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

### Linux-specific Instructions

Execute the following commands from the root directory of this repository to install the module dependencies.
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade --require-hashes --requirement requirements-uv.txt
uv sync
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

## Usage

In order to generate the warlords list in JSON format, execute the following commands.

### Windows

```
.venv\Scripts\activate.bat
warlords
```

### Linux

```
source .venv/bin/activate
warlords
```

Output will be saved to `warlords.json`.

## Format

The top level object contains the following data:

| Key | Type | Description |
| --- | --- | --- |
| `generated` | string | The time when MUME last updated the warlords list. |
| `generated_timestamp` | integer | A Unix timestamp, representing the time when MUME last updated the warlords list. |
| `schema_version` | integer | The schema version, used for data verification. |
| `war_status` | string | A summery of the state of the war. |
| `warlords` | array | An array of warlord objects, each representing a side of the war **see below**.

The `warlord` objects contain the following data:

| Key | Type | Description |
| --- | --- | --- |
| `characters` | array | An array of character objects **see below**. |
| `description` | string | A description of the side of the war. |

The `character` objects contain the following data:

| Key | Type | Description |
| --- | --- | --- |
| `class` | string | The character's class. |
| `name` | string | The character's name. |
| `race` | string | The character's race. |
| `rank` | string | The character's rank. |


[warlords list]: https://mume.org/news/war (MUME Warlords Page)
[MUME]: https://mume.org (MUME Official Site)
[current warlords json]: https://raw.githubusercontent.com/nstockton/mume-warlords/current/warlords.json (Current Warlords As JSon)
[Nick Stockton Github]: https://github.com/nstockton (Nick Stockton's Github Page)
[MPL2]: https://www.mozilla.org/en-US/MPL/2.0 (MPL 2.0 Page)
[Python]: https://python.org (Python Main Page)
