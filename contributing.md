# Contributing

* Follow PEP8 as much as you can (use [pylint](https://pypi.org/project/pylint/), default in [vscode](https://code.visualstudio.com/docs/python/linting))
* Use [google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings.

### Naming conventions:

* PascalCase: for class names
* UPPER_SNAKE_CASE: for constants
* snake_case: for everything else

### Formatting

* Use [black](https://black.readthedocs.io/en/stable/installation_and_usage.html#installation)
* Max line width of 120 characters, vscode settings:

```json
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length=120",
        "--target-version=py37",
    ],
    "editor.formatOnSave": true,
```

### Submitting code

* Make sure the code is tested, documented, then create a draft pull request from your feature branch.
