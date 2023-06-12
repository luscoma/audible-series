# Audible Series Command

## Installation

```
pip3 install audible
pip3 install audible-cli
pip3 install audible-series
```

## Usage

The command will work on an exported library file:

```
audible library export
audible series -l $PWD/library.csv -c $PWD/config.yaml
```

The config file is optional but can be used to override book data in cases where
a book is already preordered, a series should be ignored, or if audible data is
bad.  It can also be used to manually set a case where a book was read somewhere
else but it is not in your library (though this requires manually looking up the
audible ASIN).

## Development


This project uses poetry which wraps a bunch of tools like virtualenv.  The
easiest way to run it for development is to clone this repository then run a
poetry shell.

```
poetry shell
set -x AUDIBLE_PLUGIN_DIR $PWD/audible_series
audible library export
audible series -l $PWD/library.csv -c $PWD/config.yaml
```

When developing the `--only_series` flag may be useful since it will filter the
library to a single series.

## Publishing

```
poetry build
poetry publish
```

This will require an API token to pypi.  You can create one then configure poetry via: `poetry config pypi-token.pypi your-api-token`
