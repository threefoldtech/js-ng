# js-ng

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threefoldtech/js-ng/development?filepath=docs%2Fnotebooks)
![[https://pypi.python.org/pypi/js-ng](pypi)](https://img.shields.io/pypi/v/js-ng.svg)
[![Actions Status](https://github.com/threefoldtech/js-ng/workflows/jsng-ci/badge.svg?query=branch%3Adevelopment)](https://github.com/threefoldtech/js-ng/actions?query=branch%3Adevelopment)
[![[https://codecov.io/gh/threefoldtech/js-ng]](https://codecov.io/gh/threefoldtech/js-ng/branch/development/graph/badge.svg)](https://codecov.io/gh/threefoldtech/js-ng/branch/development)

config management/automation framework

## Principles

- pip installable
- facilities exposed under a [global loader](docs/wiki/loader.md): `j`
- pluggable
- docs and tests are as important as code

## Contribution

- Clean code (pep-8)
- Documentation
- Tests

## Development environment

- install [poetry](https://poetry.eustace.io)
- clone this repository, then
  - `poetry install`

- some modules are [optional (extras)](https://python-poetry.org/docs/pyproject/#extras), you can install all or any of them like:
  - `poetry install -E whoosh`: for whoosh store backend only
  - `poetry install -E all`: with all optional modules


### Accessing the virtualenv

To access the virtual env `poetry shell`

## Interacting with js-ng Environment

if you are out of the virtualenv shell, make sure to prefix all of your commands with `poetry run`

## Accessing jsng (custom shell)

just type `jsng`.

if you have any problems related to `setuptools`, just try to upgrade it before starting `jsng`.

```bash
python3 -m pip install setuptools -U
```

## Running tests

- `make tests`

## Generating docs

- `make docs`

## Generate tests docs

- `make testdocs`

## building dists

- `poetry build`

## publishing

- `poetry publish`

## API Docs

[browsable](https://threefoldtech.github.io/js-ng/api/jumpscale/) at [https://threefoldtech.github.io/js-ng/api/jumpscale/](https://threefoldtech.github.io/js-ng/api/jumpscale/)

## Wiki

We already prepared a docsify [wiki](https://threefoldtech.github.io/js-ng/wiki) website

## Contribution

### Pre-commit

We use pre-commit to enforce certain coding style and checks while contributing to js-ng repository. Please make sure to install

#### Installation

It's as easy as `python3 -m pip install pre-commit`

#### Installing pre-commit hooks in the repository

Execute `pre-commit install`
