# js-ext-template

Using [cookiecutter](https://cookiecutter.readthedocs.io) we can quickly bootstrap js-ng extensions


project variables will be asked while generation

```bash
~> cookiecutter js-ext-template
full_name [xmonader]: 
email [xmonader@gmail.com]: 
github_username [xmonader]: 
app_title [js-extension]: 
repo_name [js-extension]: 
short_description [js-ng extension]: aaaa
version [0.1.0]: 
year [2019]: 
```

e.g of the generated structure

```text
└── {{cookiecutter.repo_name}}
    ├── docs
    ├── __init__.py
    ├── jumpscale
    │   ├── clients
    │   ├── sals
    │   └── tools
    ├── LICENSE
    ├── pyproject.toml
    ├── README.md
    ├── scripts
    └── tests
```

# usage


## using github url

```bash
cookiecutter https://github.com/threefoldtech/js-ext-template-cookiecutter

```

## locally

1- clone the template `git clone https://github.com/threefoldtech/js-ext-template-cookiecutter`

2- generate
```
cookiecutter js-ext-template-cookiecutter
```
