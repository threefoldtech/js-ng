# Installation

## Using pip

Installation is as easy as `pip install js-ng`

## Manual installation

For manual installation from source, poetry is required. This method is recommended for development to work with upstream changes

### Install required packages
```
apt-get update
apt-get install git python3-venv python3-pip
pip3 install poetry
```
### Clone
```
git clone https://github.com/js-next/js-ng.git
cd js-ng
```
### User Installation
```
poetry install --no-dev
```
### Developer Installation
```
poetry install
```
### Running jsng shell
```
poetry run jsng
```
### Switch to the virtual environment
```
poetry shell
```
