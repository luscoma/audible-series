# Audible Series Command

Can be used to print out series that are coming up next from a poetry shell.

```
poetry shell
set -x AUDIBLE_PLUGIN_DIR $PWD/audible_series
audible library export
audible series -l $PWD/library.csv -c $PWD/config.yaml
```

TODO:
- Expand Readme
- Expand docs
- Add simple tests
