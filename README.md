# mume-warlords

Exports the [warlords list](https://mume.org/news/war "MUME Warlords Page") from [MUME](https://mume.org "MUME Official Site") to JSON format.

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
| `generated` | string | Textual representation of when the MUME server last generated the warlords list. |
| `generated_timestamp` | integer | The Unix timestamp when the MUME server last generated the warlords list. |
| `war_status` | string | A summery of the state of the war. |
| `warlords` | array | The list of warlords objects **see below**.

The `warlords` objects contain the following data:

| Key | Type | Description |
| --- | --- | --- |
| `characters` | array | The array of character objects for that side of the war **see below**. |
| `description` | string | Textual description of which side of the war the `characters` array represents. |

The `characters` objects contain the following data:

| Key | Type | Description |
| --- | --- | --- |
| `class` | string | The character's class. |
| `name` | string | The character's name. |
| `race` | string | The character's race. |
| `rank` | string | The character's rank. |
