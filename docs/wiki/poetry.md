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


## check dependency tree
Using `poetry show -t` you will see all of the installed packages and the implicit dependencies


## check poetry configuration

to list the configurations of the project you can use `poetry config --list`

Example output
```
~> poetry config --list

virtualenvs.create = true
virtualenvs.in-project = true
virtualenvs.path = "{cache-dir}/virtualenvs"  # /home/xmonader/.cache/pypoetry/virtualenvs
```


### Why not pipenv?

Pipenv doesn't help with building packages nor publishing them. you will need another workflow for building packages and maintaing `requirements.txt` too aside from `pipenv.toml`.


## Generating requirements.txt file

You can do `poetry run make requirements.txt` to generate the requirements.txt file.