# js-ng
![[https://pypi.python.org/pypi/js-ng](pypi)](https://img.shields.io/pypi/v/js-ng.svg)
![[https://travis-ci.org/js-next/js-ng]](https://travis-ci.org/js-next/js-ng.png)
![[https://codecov.io/gh/js-next/js-ng]](https://codecov.io/gh/js-next/js-ng/branch/development/graph/badge.svg)

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

## publishing
- `poetry publish`


## API Docs

[browsable](https://js-next.github.io/js-ng/api/jumpscale/) at [https://js-next.github.io/js-ng/api/jumpscale/](https://js-next.github.io/js-ng/api/jumpscale/)

## Wiki

We already prepared a docsify [https://js-next.github.io/js-ng/wiki](wiki) website 

## Contribution

### Pre-commit
We use pre-commit to enforce certain coding style and checks while contributing to js-ng repository. Please make sure to install

#### Installation
It's as easy as `python3 -m pip install pre-commit`

#### Installing pre-commit hooks in the repository
Execute `pre-commit install`