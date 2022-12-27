# js-ng

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/threefoldtech/js-ng/development?filepath=docs%2Fnotebooks)
![[https://pypi.python.org/pypi/js-ng](pypi)](https://img.shields.io/pypi/v/js-ng.svg)
[![Actions Status](https://github.com/threefoldtech/js-ng/workflows/jsng-ci/badge.svg?query=branch%3Adevelopment)](https://github.com/threefoldtech/js-ng/actions?query=branch%3Adevelopment)
[![[https://codecov.io/gh/threefoldtech/js-ng]](https://codecov.io/gh/threefoldtech/js-ng/branch/development/graph/badge.svg)](https://codecov.io/gh/threefoldtech/js-ng/branch/development)

config management/automation framework

## Principles

- pip installable
- facilities exposed under `loader object`: `j`
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

## releasing & publishing

- Create a branch `development_VERSION`
- Generate documentation `make docs`
- Update js-sdk version in `pyproject.toml` to the branch version
- Create a pull request against the development branch
- Merge the pull request into development
- Create a pull request from development against the master branch
- Merge the pull request into master
- make sure to call `poetry build`
- enter your api token `poetry config pypi-token.pypi your-api-token`
- then publish to pypi using `poetry publish` (note that this requires to be on the publisher account)
- now a [release can be added](https://github.com/threefoldtech/js-ng/releases/new) with a tag on master branch.

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
