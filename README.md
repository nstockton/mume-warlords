# mume-warlords

Exports the [warlords list](https://mume.org/news/war "MUME Warlords Page") from [MUME](https://mume.org "MUME Official Site") to JSON format.
Automatically generated data in JSON format can be found [here.](https://raw.githubusercontent.com/nstockton/mume-warlords/current/warlords.json "Current Warlords Information As JSON")

## License And Credits

This project is licensed under the terms of the [Mozilla Public License, version 2.0.](https://www.mozilla.org/en-US/MPL/2.0 "License Page")

This project created and maintained by [Nick Stockton.](https://github.com/nstockton)

## Installation

Install the [Python interpreter,](https://python.org "Python Home Page") and make sure it's in your path before running this package.

After Python is installed, execute the following commands from the top level directory of this repository to install the dependencies.
```
python -m venv venv
venv\Scripts\activate.bat
pip install -Ur requirements.txt
```

If you wish to contribute to this project, install the development dependencies with the following commands.
```
venv\Scripts\activate.bat
pip install -Ur requirements-dev.txt
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

## Usage

In order to generate the warlords list in JSON format, execute the following commands.
```
venv\Scripts\activate.bat
python warlords.py
```
Output will be saved to `warlords.json`.

## Format

The top level object contains the following data:

| Key | Type | Description |
| --- | --- | --- |
| `generated` | string | The time when MUME last updated the warlords list. |
| `generated_timestamp` | integer | A Unix timestamp, representing the time when MUME last updated the warlords list. |
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
