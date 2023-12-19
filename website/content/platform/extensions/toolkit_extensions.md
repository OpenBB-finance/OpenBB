---
title: Toolkits
sidebar_position: 1
description: This page describes the toolkit extensios  available for the OpenBB Platform.
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

Functions with charting enabled return figures to a field (`chart`) in the `OBBject` response object. They are displayed with the class method, `show()`. Additional Python libraries are installed with this extension:

- aiohttp
- nbformat
- pandas-ta
- plotly
- pywry
- reportlab
- scipy
- statsmodels
- svglib

### Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

To install from source in editable mode, navigate into the folder, `~/openbb_platform/extensions/charting`, and enter:

```console
pip install -e .
```

After installation, the Python interface will automatically rebuild on initialization.  This process can also be triggered manually with:

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

## Devtools

This extension aggregates the dependencies that facilitate a nice development experience
for OpenBB. It does not contain any code itself, but rather pulls in the following dependencies:

- bandit
- black
- ipykernel
- mypy
- poetry
- pre-commit
- pydocstyle
- pylint
- pytest
- pytest-cov
- ruff
- tox
- types-python-dateutil
- types-toml

### Installation

The extension is included in the `dev_install.py` script.

Standalone installation:

```console
pip install openbb-devtools
```

## Econometrics

The `openbb-econometrics` extension installs a new router path (`obb.econometrics`) and additional Python libraries:

- scipy
- statsmodels
- arch
- linearmodels

:::note
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

The `openbb-technical` extension is for performing technical analysis on time series data. It installs a new router path (`obb.techincal`) and some additional Python libraries:

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
