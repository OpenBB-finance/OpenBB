# OpenBB Platform

Thanks for installing the OpenBB Platform. To get the most out of your experience, we recommend reviewing the contents of this document.

If you have never used Python before, don't worry, your first time is just a double-click away. The sections below outline everything you need to know for getting started.

## What Did I Install?

This is a kitted out development container for Pythonic, open source, financial research. It has everything you need to get started immediately.

Included, is a complete installation of the OpenBB Platform and CLI, along with Conda and Jupyter Notebook, in an isolated Python 3.12 Conda environment.

If you already have an installation of Conda or Anaconda, the version in this folder will not rely on, interfere, or share base environment paths with, existing versions.

Tools for managing, updating, and building environments allow you to take full control of your installation, as well as quickly spin up new containers within this project folder.

To get started using right away, open one of the shortcuts described below.

## Shortcuts

At the root of the installation folder (where this document is) are shortcuts for launchers and to key file locations.

- Bash (Windows: CMD): Opens a command line shell with the base Conda environment activated. Activate the OpenBB environment with:
  - Mac/Linux: `source activate obb`
  - Windows: `conda activate obb`
- Environments: Shortcut to the root "envs" folder, where the `obb` and any created environments are stored.
  - "widgets.json" is located in the "assets" subdirectory.
- openbb-api: Opens a Terminal window and launches the OpenBB API, with optional prompts to login with your OpenBB Hub PAT.
- openbb-cli: Opens a Terminal window and launches the OpenBB CLI (formerly OpenBB Terminal).
- openbb-ipython: Opoens a Terminal window and starts an IPython session with the OpenBB Platform package imported.
- openbb-notebook: Opens a Terminal window, starts the Jupyter development server, and opens a browser window with the Notebook application.
- OpenBBUserData: Shortcut to the OpenBBUserData folder. Files exported from CLI are saved here.
- Settings: Shortcut to the `~/.openbb_platform` location where `.env` files and `user_settings.json` are stored.
  - If you cannot see the ".env" file, set Finder/Explorer to display hidden/system files.
- Update: Opens a Terminal window and updates the OpenBB Platform environment (obb) and packages.

## Command Line Entry Points

There are several command line entry points available when either:
- The OpenBB Platform environment (obb) is active.
- The "openbb_platform" package has been installed in the active Python environment, including when `--no-deps` or `--only-root` flags were used to install.

### OpenBB Entry Points

- openbb: Launches the OpenBB CLI.
- openbb-api: Launches the API and accepts select arguments.
  - All args/kwargs available to `uvicorn run` are exposed.
  - `--login`: True/False. Defeats the login prompt when False.
  - `--no-build`: Skips building "widgets.json"
  - To launch the API with no input prompts enter: `openbb-api --login False --no-build
- openbb-build: Runs the build script that generates the static assets for the OpenBB Pythobn interface.
  - Run this after installing/uninstalling/updating OpenBB extensions
  - Automatically run when `openbb-update` is run.
- openbb-update: Updates the environment packages defined in `pyproject.toml` and `poetry.lock` and rebuilds the OpenBB Python interface.
  - Location: "/extensions/openbb_platform"
  - Passes all args/kwargs to `poetry install`.

## Installed Folder Structure

At the root of the installation (where this document is), there will be two folders:

- conda (Windows: This is named after the last folder path if the default was not used)
- extensions

### Conda

This is the folder where Conda is installed and all environment data (site-packages, etc.) is stored. The "Environments" shortcuts takes you to the root of the "envs" folder.

### Extensions

This folder contains two subfolders:

#### examples

Contains empty example extensions for the three types of OpenBB Platform extensions:

- Router
- Provider
- OBBject

To install all three examples in the OpenBB Platform environment, open the Bash/CMD shortcut and enter:

```console
source activate obb  # CMD: conda activate obb
cd extensions/examples
python install_examples.py
```

- openbb_platform

## Conda Install vs. PIP Install vs. Poetry Install

The three ways to install packages may appear to accomplish the same objectives - installing Python packages - but each has a distinctly different purpose.

An easy way to think about the difference is, both `pip` and `poetry` require an existing Python installation; `conda` installs Python so that you can run `pip install poetry`.

In general, you use:

- `conda`
  - When a new environment has been created. Packages here can be included in the creation command, `conda create`.
  - When the specific package is only distributed through Conda or the `conda-forge` channel.
  - When changing the version of Python used within the environment.
- `pip`
  - When installing/uninstalling packages to the activated Python environment.
  - Resort to `conda install` only if packages fail to install or wheels cannot be built.
- `poetry`
  - Installing a local Python package.
  - Syncing all package dependencies according to provided specs in `pyproject.toml` and `poetry.lock` files.
  - Building and distributing Python packages.

Conda is for container management, Poetry resolves the project's dependencies and provides build/distribution tools, while `pip` is for installing from [PyPI](https://pypi.org)

## Documentation Resources

### OpenBB
- [Quckstart](https://docs.openbb.co/platform/getting_started/quickstart)
- [OpenBB Pro](https://docs.openbb.co/pro)
- [OpenBB Pro Data Connectors](https://docs.openbb.co/pro/data-connectors)
- [OpenBB Platform](https://docs.openbb.co/platform)
- [OpenBB CLI](https://docs.openbb.co/cli)
- [OpenBB User Settings](https://docs.openbb.co/platform/user_guides/settings_and_environment_variables)
- [API Keys and Authorization](https://docs.openbb.co/platform/getting_started/api_keys)
- [REST API Requests](https://docs.openbb.co/platform/getting_started/api_requests)
- [OpenBB Platform Architecture Overview](https://docs.openbb.co/platform/developer_guide/architecture_overview)
- [Create A New Router Extension](https://docs.openbb.co/platform/getting_started/create_new_router_extension)
- [OpenBB Charting]()
- [PyWry](https://github.com/OpenBB-finance/pywry)

### External

- [python](https://docs.python.org/3/)
- [conda create](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#managing-environments)
- [pyproject.toml](https://python-poetry.org/docs/pyproject/)
- [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
- [pip](https://pip.pypa.io/en/stable/)
- [poetry config](https://python-poetry.org/docs/configuration)
- [pydantic](https://docs.pydantic.dev/latest/)
- [uvicorn](https://www.uvicorn.org/)
- [fastapi](https://fastapi.tiangolo.com/)
- [jupyter](https://docs.jupyter.org/en/latest/)
- [pandas](https://pandas.pydata.org/docs/)
- [numpy](https://numpy.org/doc/)
- [Plotly Graph Objects](https://plotly.com/python/graph-objects/)

