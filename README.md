# Audible Series Command

Can be used to print out series that are coming up next from a poetry shell.

```
poetry shell
audible library export
audible series -l $PWD/library.csv -c $PWD/config.yaml
```

The config file is optional but can be used to override book data in cases where
a book is already preordered, a series should be ignored, or if audible data is
bad.  It can also be used to manually set a case where a book was read somewhere
else but it is not in your library (though this requires manually looking up the
audible ASIN).

Note: While the packaging of all this will automatically just work when
installed with pip the audible-cli itself is not in pypi.  You must clone the
git repo https://github.com/mkb79/audible-cli then pip install this repo for the
audible cli to be usable.
