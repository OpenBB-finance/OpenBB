---
title: Toolkits
sidebar_position: 1
description: This page describes the toolkit extensions available for the OpenBB Platform.
keywords:
- OpenBB Platform
- Python client
- Fast API
- getting started
- extensions
- data providers
- data extensions
- toolkit extensions
- toolkits
- endpoints
- community
- technical analysis
- quantitative analysis
- charting libraries
- Plotly
- OpenBBFigure
- PyWry
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Toolkits - Extensions | OpenBB Platform Docs" />

OpenBB Toolkit Extensions expand the Platform with functions for manipulating data and preparing it for display. The Core Platform installation does not install any toolkit extensions. The table below is the current list of toolkit extensions.

| Extension Name | Description | Installation Command | Core/Community | Router Path |
|:-----------------|:-----------:|:-------------------:|:------------------:|-------------:|
| openbb-charting | Rest API charting service and Plotly library. | pip install openbb-charting | Community | N/A |
| openbb-devtools | Aggregates dependencies that facilitate a nice development experience for OpenBB. | pip install openbb-devtools | N/A |
| openbb-econometrics | Econometrics models for the Python interface only. | pip install openbb-econometrics | Community | obb.econometrics |
| openbb-quantitative | Functions for performing quantitative analysis. | pip install openbb-quantitative | Community | obb.quantitative |
| openbb-technical | Functions for performing technical analysis. | pip install openbb-technical | Community | obb.technical |

The sections below outline any specific installation considerations for the extension.

## Charting

The OpenBB Charting Extension supplies charting infrastructure and services to the OpenBB Platform. Figure objects are served via REST API or Python Client.  It utilizes [PyWry](https://github.com/OpenBB-finance/pywry) for handling the display of interactive charts and tables in a separate window, with a Plotly library. The extension framework allows developers to easily insert other Python charting libraries into the router pipeline.

Functions with charting enabled return figures to a field (`chart`) in the `OBBject` response object. They are displayed with the class method, `show()`.

> Additional Python libraries are installed with this extension: `aiohttp`, `nbformat`, `pandas-ta`, `plotly`, `pywry`, `reportlab`, `scipy`, `statsmodels`, and `svglib`.

:::tip
The `openbb-charting` is in fact an [`OBBject` extension](platform/development/how-to/add_obbject_extension.md) which means you'll have the functionality it exposes on every command result.
:::

The following packages are dependencies of the `openbb-charting` extension:

- scipy
- plotly
- statsmodels
- reportlab
- pywry
- svglib
- nbformat
- pandas-ta

### Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

> Find the latest version on [PyPI](https://pypi.org/project/openbb-charting/).

To install from source in editable mode, navigate into the folder, `~/openbb_platform/extensions/charting`, and enter:

```console
pip install -e .
```

After installation, the Python interface will automatically rebuild on initialization. This process can also be triggered manually with:

```python
import openbb
openbb.build()
```

The Python interpreter may require a restart.

### PyWry dependency in Linux

When using Linux distributions, the PyWry dependency requires certain dependencies to be installed first.

- Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.0-dev`

- Arch Linux / Manjaro:
`sudo pacman -S webkit2gtk`

- Fedora:
`sudo dnf install gtk3-devel webkit2gtk3-devel`

If Rust (Cargo) is required, install it:

```console
curl --proto '=https' --tlsv1.3 https://sh.rustup.rs -sSf | sh
```

## Devtools

Please refer to the following PyPI distributed package: https://pypi.org/project/openbb-devtools/

This Python package, `openbb-devtools`, is designed for OpenBB Platform Developers and contains a range of dependencies essential for robust and efficient software development.

These dependencies cater to various aspects like code formatting, security analysis, type checking, testing, and kernel management.

The inclusion of these packages ensures that the development process is streamlined, the code quality is maintained, and the software is secure and reliable.

Included dependencies:

- `ruff`: A fast Python linter focused on performance and simplicity.
- `pylint`: A tool that checks for errors in Python code, enforces a coding standard, and looks for code smells.
- `mypy`: A static type checker for Python, helping catch type errors during development.
- `pydocstyle`: A linter for Python docstrings to ensure they meet certain style requirements.
- `black`: An uncompromising Python code formatter, ensuring consistent code style.
- `bandit`: A tool designed to find common security issues in Python code.
- `pre-commit`: Manages and maintains pre-commit hooks that run checks before each commit, ensuring code quality.
- `nox`: A generic virtualenv management and test command line tool for running tests in isolated environments.
- `pytest`: A mature full-featured Python testing tool that helps in writing better programs.
- `pytest-cov`: A plugin for pytest that measures code coverage during testing.
- `ipykernel`: A package that provides the IPython kernel for Jupyter.
- `types-python-dateutil`: Type stubs for python-dateutil, aiding in static type checking.
- `types-toml`: Type stubs for TOML, useful for static type checking in TOML parsing.
- `poetry`: A tool for dependency management and packaging in Python.

Each dependency plays a critical role in ensuring the code is clean, efficient, and functional, ultimately leading to the development of high-quality software.

While developing code for the OpenBB Platform, one should always install the DevTools packages so that the above development tooling is available out-of-the-box.

### Installation

Install from PyPI with:

```console
pip install openbb-devtools
```

:::info
When setting up the environment using the `openbb_platform/dev_install.py` script, the DevTools will also be installed.
:::

## Econometrics

The `openbb-econometrics` extension installs a new router path (`obb.econometrics`) and additional Python libraries:

- scipy
- statsmodels
- arch
- linearmodels

:::note

Statsmodels requires a C compiler be present on the system. Follow the instructions [here](https://cython.readthedocs.io/en/latest/src/quickstart/install.html) for system-specific methods.

This extension is not accessible via REST API because `statsmodels` is not serializable.
:::

### Installation

Install from PyPI with:

```console
pip install openbb-econometrics
```

To install from source in editable mode, navigate into the folder, `~/openbb_platform/extensions/econometrics`, and enter:

```console
pip install -e .
```

After installation, the Python interface will automatically rebuild on initialization.

## Quantitative

The `openbb-quantitative` extension installs a new router path (`obb.quantitative`) and a few additional Python libraries:

- pandas-ta
- scipy
- statsmodels

### Installation

Install from PyPI with:

```console
pip install openbb-quantitative
```

To install from source in editable mode, navigate into the folder, `~/openbb_platform/extensions/quantitative`, and enter:

```console
pip install -e .
```

After installation, the Python interface will automatically rebuild on initialization.

## Technical

The `openbb-technical` extension is for performing technical analysis on time series data. It installs a new router path (`obb.technical`) and some additional Python libraries:

- pandas-ta
- scikit-learn
- scipy
- statsmodels

### Installation

Install from PyPI with:

```console
pip install openbb-technical
```

To install from source in editable mode, navigate into the folder, `~/openbb_platform/extensions/technical`, and enter:

```console
pip install -e .
```

After installation, the Python interface will automatically rebuild on initialization.
