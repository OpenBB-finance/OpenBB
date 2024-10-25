# OpenBB Platform Installer Package

This package is for installing the OpenBB Platform packages into any Python environment. Versions between 3.9 and 3.12, inclusively, are supported.

The `obb` virtual environment that came with the installation is pre-loaded, and this configuration can be duplicated by creating a new environment and running, `poetry install`, from this location.

## Installation

Assuming the current working directory is the location of this document, the code block below will create a new environment, activate it, update the dependencies, and then install the OpenBB Platform.

Open the Terminal command line with the Bash/CMD shortcut.

```sh
conda create -n my_env python=3.10 -y
conda activate my_env
pip install poetry
poetry lock
poetry install
openbb-build
```

## Updating Packages

Update the environment dependencies with:

```sh
poetry lock
poetry install
```

## Installation Groups

The package can be installed in different configurations, using Poetry groups as `--with`, `--without`, or `--only` keyword arguments.

- main
- openbb-all
- cli
- notebook

To install, in a fresh environment, only the `openbb-core` package and the base dependencies:

```sh
poetry install --only main --sync
```

The `--sync` flag with sync the environment to the `poetry.lock` file for the flagged group(s). All items are installed when no arguments are supplied. Use this as a way to restore corrupted environments.

Do not use the `--sync` flag if you wish to keep installed packages that are not defined in the `pyproject.toml` and `poetry.lock` files.
