# poetry

poetry is the long waited solution for dependency management and packaging that checks lots of boxes


## virtual env
- virtual env as easy as `poetry shell`

## deps and locking

- add `poetry add pkgname` 
- remove `poetry remove pkgname`

## building packages
`poetry build` to build packages (tarball/wheels)

## publishing packages
`poetry publish` to publish your package to pypi



### Why not pipenv?

Pipenv doesn't help with building packages nor publishing them. you will need another workflow for building packages and maintaing `requirements.txt` too aside from `pipenv.toml`.

