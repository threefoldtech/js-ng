# js-ng
![[https://pypi.python.org/pypi/js-ng](pypi)](https://img.shields.io/pypi/v/js-ng.svg)
![[https://travis-ci.org/threefoldtech/js-ng]](https://travis-ci.org/threefoldtech/js-ng.png)
![[https://codecov.io/gh/threefoldtech/js-ng]](https://codecov.io/gh/threefoldtech/js-ng/branch/development/graph/badge.svg)

config management/automation framework

## Principles

- pip installable
- facilities exposed under `god object`: `j`
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

### Accessing the shell

#### Outside the virtualenv
open the shell using `poetry run jsng`

#### In the virtual env
just type `jsng`.

if you have any problems related to `setuptools`, just try to upgrade it before starting `jsng`.

```bash
python3 -m pip install setuptools -U
```

## Running tests
- `make tests`

## Generating docs
- `make docs`


## building dists
- `poetry build`

## releasing & publishing
- make sure the version is bumped in `pyproject.toml` file
- make sure to call `poetry build`
- then publish to pypi using `poetry publish` (note that this requires to be on the publisher account)


## API Docs

[browsable](https://threefoldtech.github.io/js-ng/api/jumpscale/) at [https://threefoldtech.github.io/js-ng/api/jumpscale/](https://threefoldtech.github.io/js-ng/api/jumpscale/)


## Contribution

### Pre-commit
We use pre-commit to enforce certain coding style and checks while contributing to js-ng repository. Please make sure to install

#### Installation
It's as easy as `python3 -m pip install pre-commit`

#### Installing pre-commit hooks in the repository
Execute `pre-commit install`