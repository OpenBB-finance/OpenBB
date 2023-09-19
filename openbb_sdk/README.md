[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBBTerminal)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
|:--:|
| ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png) |
| Check our website at [openbb.co](www.openbb.co) |


## OpenBB Platform Overview

The OpenBB Platform provides a convenient way to access raw financial data from multiple data providers. The package comes with a ready to use REST API. This allows developers from any language to easily create applications on top of OpenBB Platform.


## Installation

The command below provides access to the core functionalities behind the [OpenBB Platform](https://my.openbb.co/app/sdk).

```bash
pip install openbb
```

> Note: While we are in pre-release mode you need to specify the version, e.g. `pip install openbb==4.0.0a0`

If you wish to install extensions that expand the core functionalities, you can do so by specifying the extension name or use `all` to install all.

```bash
pip install openbb[all]==4.0.0a0
``````

## REST API

The OpenBB Platform comes with a ready to use REST API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_core.api.rest_api:app
```

Check `openbb-core` [README](https://pypi.org/project/openbb-core/) for additional info.

## API keys

To fully leverage the OpenBB Platform you need to configure some API keys. Here are the 3 options on how to do it:

1. From OpenBB Hub
2. At runtime
3. From local file

### 1. From OpenBB Hub

You can also load your the keys from the OpenBB Hub. Get your personal access token at https://my.openbb.co/app/sdk/pat.

```python
>>> from openbb import obb
>>> openbb.account.login(pat="OPENBB_PAT")
```

### 2. At runtime

```python
>>> from openbb import obb
>>> obb.user.credentials.fmp_api_key = "REPLACE_ME"
>>> obb.user.credentials.polygon_api_key = "REPLACE_ME"

>>> # Persist changes in ~/.openbb_sdk/user_settings.json
>>> obb.account.save()
```

### 3. From local file

You can specify the keys directly in the `~/.openbb_sdk/user_settings.json` file.

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
