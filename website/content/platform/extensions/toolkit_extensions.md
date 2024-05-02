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

The OpenBB Charting Extension supplies charting infrastructure and services to the OpenBB Platform. Figure objects are served via REST API or Python Client.  It utilizes [PyWry](https://github.com/OpenBB-finance/pywry) for handling the display of interactive charts and tables in a separate window, with a Plotly library.

Functions with dedicated views return figures to the `chart` attribute of the `OBBject` response object. They are displayed with the class method, `show()`.

:::tip
The `openbb-charting` is an [`OBBject` extension](platform/development/how-to/add_obbject_extension.md), which means the general functionality is exposed in every command result.
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

See the [charting](charting) section for more details and [installation](charting/installation) instructions.

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
