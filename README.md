# js-ng
![[https://pypi.python.org/pypi/js-ng](pypi)](https://img.shields.io/pypi/v/js-ng.svg)
![[https://travis-ci.org/js-next/js-ng]](https://travis-ci.org/js-next/js-ng.png)
![[https://codecov.io/gh/js-next/js-ng]](https://codecov.io/gh/js-next/js-ng/branch/master/graph/badge.svg)

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
- intall [poetry](https://poetry.eustace.io)
- clone this repository, then
    - `poetry install`

- make sure to generate a private key to be used by configuration manager:
    - `poetry shell`
    - `hush_keygen --name /path/to/your/key`
    - `jsctl config update --name=private_key_path --value=/path/to/your/key`

- now you can open the shell
    - `jsng`

## Running tests
- `make tests`

## Generating docs
- `make docs`


## building dists
- `poetry build`

## publishing
- `poetry publish`


## API Docs

[browsable](https://js-next.github.io/js-ng/api/jumpscale/) at https://js-next.github.io/js-ng/api/jumpscale/
