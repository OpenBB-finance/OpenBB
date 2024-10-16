# OpenBB Platform

Thanks for installing the OpenBB Platform. To get the most out of your experience, we recommend reviewing the contents of this document.

If you have never used Python before, don't worry, your first time is just a double-click away. The sections below outline everything you need to know for getting started.

## What Did I Install?

This is a kitted out development container for Pythonic, open source, financial research. It has everything you need to get started immediately.

Included, is a complete installation of the OpenBB Platform and CLI, along with Conda and Jupyter Notebook, in an isolated Python 3.12 Conda environment.

If you already have an installation of Conda or Anaconda, the version in this folder will not rely on, interfere, or share base environment paths with, existing versions.

Tools for managing, updating, and building environments allow you to take full control of your installation, as well as quickly spin up new containers within this project folder.

Follow the quick start steps below to get started using right away; or, open one of the shortcuts described below.

If you want to build your own end points, connections, and features, try installing the [example extensions](#examples)

## OpenBB Terminal Pro Quick Start

- Login to the [OpenBB Hub](https://my.openbb.co)
- Optionally, add API keys for remote authorization on the page [here](https://my.openbb.dev/app/platform/credentials).
  - If credentials have been added, from the sidebar, click on 'Personal Access Token'.
  - Generate a token and copy the value to the clipboard.
- Optionally, from the sidebar, click on 'Widgets' to filter out any provider extensions or endpoints you wish to exclude.
  - Without filtering, there will be well over 300 individual widgets. This will narrow the field and focus on only what you need.
  - After configuring, download the file ("widget_settings.json") and save it to, `~/.openbb_platform`. The "Settings" shortcut takes you there.
- Double-click on the `openbb-api` shortcut.
- If you generated a personal access token, paste the values that were copied to the clipboard and hit the return key.
  - Enter y/n to persist the downloaded credentials on the local machine for future sessions.

- By default, the server will be running on: [http://127.0.0.1:6900](http://127.0.0.1:6900)

- Login to OpenBB Terminal Pro [here](https://pro.openbb.co)
- From the sidebar, click on, "Data Connectors".
- Then click on the button, "Add Data".
- In the pop-up menu, select "Custom Backend".
- Enter a name for the connection - i.e, "OpenBB Platform"
- Enter the address the server is running on - i.e, "http://127.0.0.1:6900"
- **Ensure that "Validate Widgets" is set to "No".**
- Click on the "Test" button.
- Finally, click on the "Add" button.

The OpenBB Platform API widgets can now be added to any dashboard. For a more detailed version of these instructions, see the documentation page [here](https://docs.openbb.co/pro/custom-backend)

## Shortcuts

At the root of the installation folder (where this document is) are shortcuts for launchers and to key file locations.

- Bash (Windows: CMD): Opens a command line shell with the base Conda environment activated. Activate the OpenBB environment with:
  - Mac/Linux: `source activate obb`
  - Windows: `conda activate obb`
- Environments: Shortcut to the root "envs" folder, where the `obb` and any created environments are stored.
  - "widgets.json" is located in the "assets" subdirectory.
- openbb-api: Opens a Terminal window and launches the OpenBB API, with optional prompts to login with your OpenBB Hub PAT.
- openbb-cli: Opens a Terminal window and launches the OpenBB CLI (formerly OpenBB Terminal).
- openbb-ipython: Opens a Terminal window and starts an IPython session with the OpenBB Platform package imported.
- openbb-notebook: Opens a Terminal window, starts the Jupyter development server, and opens a browser window with the Notebook application.
- OpenBBUserData: Shortcut to the OpenBBUserData folder. Files exported from CLI are saved here.
- Settings: Shortcut to the `~/.openbb_platform` location where `.env` files and `user_settings.json` are stored.
  - If you cannot see the ".env" file, set Finder/Explorer to display hidden/system files.
- Update: Opens a Terminal window and updates the OpenBB Platform environment (obb) and packages.

## Command Line Entry Points

There are several command line entry points available when either:
- The OpenBB Platform environment (obb) is active.
- The "openbb_platform_installer" package has been installed in the active Python environment.

### OpenBB Entry Points

- openbb: Launches the OpenBB CLI.
- openbb-api: Launches the API and accepts select arguments.
  - All args/kwargs available to `uvicorn run` are exposed.
  - `--login`: True/False. Defeats the login prompt when False.
  - `--no-build`: Skips building "widgets.json"
- openbb-build: Runs the build script that generates the static assets for the OpenBB Python interface.
  - Run this after installing/uninstalling/updating OpenBB extensions
  - Automatically run when `openbb-update` is run.
- openbb-update: Updates the environment packages defined in `pyproject.toml` and `poetry.lock` and rebuilds the OpenBB Python interface.
  - Location of Poetry files: "/extensions/openbb_platform_installer"
  - Passes all args/kwargs to `poetry install`.

### Starting The OpenBB Platform API With Optional Arguments

1. Open the `Bash` (`CMD` on Windows) shortcut.
2. Activate the `obb` environment
  - Unix: `source activate obb`
  - Windows: `conda activate obb`
3. Run `openbb-api` with `--parameter value` to add any `uvicorn.run` parameter.

### OpenBB Platform API Over HTTPS

To run the API over the HTTPS protocol, you must first create a self-signed certificate and the associated key. After steps 1 & 2 above, you can generate the files by entering this to the command line:

```sh
openssl req -x509 -days 3650 -out localhost.crt -keyout localhost.key   -newkey rsa:4096 -nodes -sha256   -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```

Two files will be created, in the current working directory, that are passed as keyword arguments to the `openbb-api` entry point.

```sh
openbb-api --ssl_keyfile localhost.key --ssl_certfile localhost.crt
```

**Note**: Adjust the command to include the full path to the file if the current working directory is not where they are located.


The certificate - `localhost.crt` - will need to be added to system's trust store. The process for this will depend on the operating system and the user account privilege.

A quick solution is to visit the server's URL, show the details of the warning, and choose to continue anyways.

Contact the system administrator if you are using a work device and require additional permissions to complete the configuration.

![This Connection Is Not Private](https://in.norton.com/content/dam/blogs/images/norton/am/this_connection_not_is_private.png)

## Installed Folder Structure

At the root of the installation (where this document is), there will be three folders:

- conda (Windows: This is named after the last folder path if the default was not used)
- extensions
- notebooks

### Conda

This is the folder where Conda is installed and all environment data (site-packages, etc.) is stored. The "Environments" shortcuts takes you to the root of the "envs" folder.

### Extensions

This folder contains two subfolders:

### Notebooks

This folder contains tutorial notebooks with examples for getting started with Python and the OpenBB Platform. They can be opened by launching the `openbb-notebook` shortcut.

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

#### openbb_platform_installer

This is a meta package for installing and managing OpenBB Platform installation within any Python environment.
Poetry is used to update and resolve any dependencies that are defined in the `pyproject.toml` file.

The `poetry.lock` file is updated every time the `Update` shortcut is run.

There are several configurations available, via combinations of `--with`, `--without`, and `--only` parameters, when running `poetry install`.

Choices are:

- main
- openbb-all
- cli
- notebook

Each parameter will accept multiple items, but `--without` takes priority for solving for the environment.

## Uninstallation

Mac/Linux users can uninstall by deleting the folder, while Windows users can run the Uninstall shortcut.

The leftover artifacts will include:

- Global configuration files stored by Poetry, PIP, Conda, and Jupyter.
- Third-party Python package caches and `.env` files.
- Folders:
  - ~/.openbb_platform
  - ~/OpenBBUserData

Windows users will also need to remove the parent folder where it was originally installed, after running Uninstall.

Your OpenBB Hub account can be deleted, along with all associated data, from the Account page in [my.openbb.co](https://my.openbb.co)

## Additional Information

### Conda Install vs. PIP Install vs. Poetry Install

The three ways to install packages may appear to accomplish the same objectives - installing Python packages - but each has a distinctly different purpose.

An easy way to think about the difference is, both `pip` and `poetry` require an existing Python installation; `conda` installs Python so that you can run `pip install poetry`.

In general, you use:

- `conda`
  - When a new environment has been created. Packages here can be included in the creation command, `conda create`.
  - When the specific package is only distributed through Conda or the `conda-forge` channel.
  - When changing the version of Python used within the environment.
  - For interactions with the machine code layer of the system - e.g., compilers, and bridges to "outside of Python" land.
- `pip`
  - When installing/uninstalling packages to the activated Python environment.
  - Resort to `conda install` when packages fail to install, or wheels cannot be built, from PyPI.
- `poetry`
  - Installing a local Python package.
  - Syncing all package dependencies according to provided specs in `pyproject.toml` and `poetry.lock` files.
  - Building and distributing Python packages.

Conda is for container management and machine code level operations, Poetry resolves the project's dependencies and provides build/distribution tools within the current Python environment, while `pip` is for installing Python packages - typically from [PyPI](https://pypi.org).

### Documentation Resources

### OpenBB
- [OpenBB Pro](https://docs.openbb.co/pro)
- [OpenBB Pro Data Connectors](https://docs.openbb.co/pro/data-connector)
- [widgets.json](https://docs.openbb.co/pro/custom-backend/widgets.json)
- [OpenBB Platform](https://docs.openbb.co/platform)
- [OpenBB Platform Quckstart](https://docs.openbb.co/platform/getting_started/quickstart)
- [OpenBB CLI](https://docs.openbb.co/cli)
- [OpenBB User Settings](https://docs.openbb.co/platform/user_guides/settings_and_environment_variables)
- [API Keys and Authorization](https://docs.openbb.co/platform/getting_started/api_keys)
- [REST API Requests](https://docs.openbb.co/platform/getting_started/api_requests)
- [OpenBB Platform Architecture Overview](https://docs.openbb.co/platform/developer_guide/architecture_overview)
- [Create A New Router Extension](https://docs.openbb.co/platform/getting_started/create_new_router_extension)
- [OpenBB Charting](https://github.com/OpenBB-finance/OpenBB/tree/develop/openbb_platform/obbject_extensions/charting#readme)
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

