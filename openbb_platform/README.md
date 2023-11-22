# OpenBB Platform

[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBBTerminal)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
|:--:|
| ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png) |
| Check our website at [openbb.co](www.openbb.co) |

## Overview

The OpenBB Platform provides a convenient way to access raw financial data from multiple data providers. The package comes with a ready to use REST API - this allows developers from any language to easily create applications on top of OpenBB Platform.

## Installation

The command below provides access to the core functionalities behind the OpenBB Platform.

```bash
pip install openbb --pre
```

To install extensions that expand the core functionalities specify the extension name or use `all` to install all.

```bash
# Install single extension, e.g. openbb-charting
pip install openbb[charting] --pre

# Install all available extensions
pip install openbb[all] --pre
``````

> The `--pre` flag is required to install the latest alpha version.
> Note: These instruction are specific to v4. For installation instructions and documentation for v3 go to our [website](https://docs.openbb.co/sdk).

## Python

```python
>>> from openbb import obb
>>> output = obb.equity.price.historical("AAPL")
>>> df = output.to_dataframe()
>>> df.head()
              open    high     low  ...  change_percent             label  change_over_time
date                                ...
2022-09-19  149.31  154.56  149.10  ...         3.46000  September 19, 22          0.034600
2022-09-20  153.40  158.08  153.08  ...         2.28000  September 20, 22          0.022800
2022-09-21  157.34  158.74  153.60  ...        -2.30000  September 21, 22         -0.023000
2022-09-22  152.38  154.47  150.91  ...         0.23625  September 22, 22          0.002363
2022-09-23  151.19  151.47  148.56  ...        -0.50268  September 23, 22         -0.005027

[5 rows x 12 columns]
```

## API keys

To fully leverage the OpenBB Platform you need to get some API keys to connect with data providers. Here are the 3 options on where to set them:

1. OpenBB Hub
2. Runtime
3. Local file

### 1. OpenBB Hub

Set your keys at [OpenBB Hub](https://my.openbb.co/app/sdk/api-keys) and get your personal access token from https://my.openbb.co/app/sdk/pat to connect with your account.

```python
>>> from openbb import obb
>>> openbb.account.login(pat="OPENBB_PAT")

>>> # Persist changes in OpenBB Hub
>>> obb.account.save()
```

### 2. Runtime

```python
>>> from openbb import obb
>>> obb.user.credentials.fmp_api_key = "REPLACE_ME"
>>> obb.user.credentials.polygon_api_key = "REPLACE_ME"

>>> # Persist changes in ~/.openbb_platform/user_settings.json
>>> obb.account.save()
```

### 3. Local file

You can specify the keys directly in the `~/.openbb_platform/user_settings.json` file.

Populate this file with the following template and replace the values with your keys:

```json
{
  "credentials": {
    "fmp_api_key": "REPLACE_ME",
    "polygon_api_key": "REPLACE_ME",
    "benzinga_api_key": "REPLACE_ME",
    "fred_api_key": "REPLACE_ME"
  }
}
```

## REST API

The OpenBB Platform comes with a ready to use REST API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_platform.platform.core.openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

Check `openbb-core` [README](https://pypi.org/project/openbb-core/) for additional info.

## Install for development

To develop the OpenBB Platform you need to have the following:

- Git
- Python 3.8 or higher
- Virtual Environment with `poetry` and `toml` packages installed
  - To install these packages activate your virtual environment and run `pip install poetry toml`

How to install the platform in editable mode?

  1. Activate your virtual environment
  1. Navigate into the `openbb_platform` folder
  1. Run `python dev_install.py` to install the packages in editable mode
