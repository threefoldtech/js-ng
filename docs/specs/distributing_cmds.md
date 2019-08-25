# entry-points

instead of manually copying helper scripts let's use entry_point for things like jshell, synctool, etc. these can be managed using entrypoints console_script entry https://packaging.python.org/specifications/entry-points/ and utilize `tool.poetry.scripts` to ship them


# poetry.scripts section
```
[tool.poetry.scripts]
jsng = "jumpscale.entry_points.jsng:run"
jsctl = "jumpscale.entry_points.jsctl:cli"

```