---
title: Overview
sidebar_position: 1
description: An overview for getting started with the OpenBB Platform Python client and Fast API, details on authorization, data providers, settings, responses, commands, logging, and features such as dynamic command execution.
keywords:
- OpenBB Platform
- Python client
- Fast API
- getting started
- authorization
- data providers
- OpenBB Hub
- local environment
- environment variables
- user settings
- command execution
- API response
- logging
- proxy networks
- data cleaning
- technical analysis
- quantitative analysis
- charting libraries
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Overview - Usage | OpenBB Platform Docs" />

At its base, the OpenBB Platform supplies core architecture and services for connecting data providers and extensions, consumable as a Python client and Fast API. The extension framework provides interoperability between as many, or few, services required.  Optional extras are not included with the base installation, and these include:

- Charting libraries and views
- Data cleaning
- Technical/Quantitative Analysis
- Community data providers
- CLI Terminal

## Authorization

By default, authorization is not required to initialize and use the core services. Most data providers, however,  require an API key to access their data. They can be stored locally, or securely on the OpenBB Hub for convenient remote access. Refer to our Developer Guidelines for best practices within a production environment.

### OpenBB Hub

Data provider credentials and user preferences can be securely stored on the OpenBB Hub and accessed via a revokable Personal Access Token (PAT). Login to the [Hub](https://my.openbb.co/) to manage this method of remote authorization.

#### Python Client

The OpenBB Hub is a convenient solution for accessing data in temporary environments, like Google Colab. Login using the Python client with:

```jupyterpython
from openbb import obb

# Login with personal access token
obb.account.login(pat="your_pat", remember_me=True)

# Login with email and password
obb.account.login(email="your_email", password="your_password", remember_me=True)

# Change a credential
obb.user.credentials.polygon_api_key = "new_key"

# Save account changes
obb.account.save()

# Refresh account with latest changes
obb.account.refresh()

# Logout
obb.account.logout()
```

Set `remember_me` as `False` to discard all credentials at the end of the session.

### Fast API

Activate the Python environment and then start the server from a Terminal command line with:

```console
uvicorn openbb_core.api.rest_api:app
```

To use the Fast API documentation page, navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).  By default, no authorization is required.  Basic authorization can be enabled with environment variables. In the home folder, along with `user_settings.json`, create a new file, `.env`, if it does not yet exist.

```.env
OPENBB_API_AUTH="True"
OPENBB_API_USERNAME="some_user"
OPENBB_API_PASSWORD="some_pass"
```

The application will expect a header that contains username and password in the form of `Basic <username:password>`, where "username:password" is encoded in Base64. Pass this in every request to the API inside the headers "Authorization" field.

```python
import base64
import requests

msg = "some_user:some_pass"
msg_bytes = msg.encode('ascii')
base64_bytes = base64.b64encode(msg_bytes)
base64_msg = base64_bytes.decode('ascii')


symbol="SPY"
url = f"http://127.0.0.1:8000/api/v1/equity/price/quote?provider=intrinio&symbol={symbol}&source=intrinio_mx"
headers = {"accept": "application/json", "Authorization": f"Basic {base64_msg}"}

response = requests.get(url=url, headers=headers)

response.json()
```

Refer to the Developer Guidelines for custom authorization procedures.

### Local Environment

Credentials and user preferences  are stored locally, `~/.openbb_platform/`, as a JSON file, `user_settings.json`.  It is read upon initializing the Python client, or when the Fast API is authorized. If the file does not exist, create it with any text editor. The schema below can be copy/pasted if required, providers not listed here are added using the same format:

```json
{
  "credentials": {
    "fmp_api_key": "REPLACE",
    "polygon_api_key": "REPLACE",
    "benzinga_api_key": "REPLACE",
    "fred_api_key": "REPLACE",
    "nasdaq_api_key": "REPLACE",
    "intrinio_api_key": "REPLACE",
    "alpha_vantage_api_key": "REPLACE",
    }
}
```

To set keys from the Python client for the current session only, access the Credentials class:

```python
obb.user.credentials.intrinio_api_key = "REPLACE_WITH_KEY"
```

## Environment Variables

Environment variables are defined in a `.env` file. If this file does not exist, create it inside the same folder `user_settings.json` is located.

- `OPENBB_DEBUG_MODE`: enables verbosity while running the program
- `OPENBB_DEVELOP_MODE`: points hub service to .co or .dev
- `OPENBB_AUTO_BUILD`: enables automatic SDK package build on import
- `OPENBB_CHARTING_EXTENSION`: specifies which charting extension to use
- `OPENBB_API_AUTH_EXTENSION`: specifies which authentication extension to use
- `OPENBB_API_AUTH`: enables API authentication for command endpoints
- `OPENBB_API_USERNAME`: sets API username
- `OPENBB_API_PASSWORD`: sets API password

Variables can be defined for current session only.

```python
import os
os.environ["OPENBB_DEBUG_MODE"] = "True"
from openbb import obb
```

### Proxy Networks

An environment variable can be set, in the `.env` file, to direct the Requests library to a specific address and port.

```env
HTTP_PROXY="<ADDRESS>" or HTTPS_PROXY="<ADDRESS>”
```

For example:

```env
HTTP_PROXY="http://10.10.10.10:8000"
```

## User Settings

| **Preference**        | **Default**                      | **Options**            | **Description** |
|-----------------------|----------------------------------|------------------------|---------------|
| data_directory        | /home/OpenBBUserData             | Any path.              | When launching the application for the first time  this directory will be created. It serves as the default location where the application stores usage artifacts  such as logs and exports. |
| export_directory      | /home/OpenBBUserData/exports     | Any path.              | The OpenBB Charting Extension provides the capability to export images in various formats. This is the directory where it attempts to save such exports.  |
| cache_directory | /home/OpenBBUserData/cache | Any path.              | The directory where http requests and database caches are stored, for functions with caching. |
| user_styles_directory | /home/OpenBBUserData/styles/user | Any path.              | The OpenBB Charting Extension supports custom stylization. This directory is the location where it looks for user-defined styles. If no user styles are found in this directory  the application will proceed with the default styles.  |
| charting_extension    | openbb_charting                  | ["openbb_charting"] | Name of the charting extension to be used with the application.  |
| chart_style           | dark                             | ["dark", "light"]    | The default color style to use with the OpenBB Charting Extension plots. Options include "dark" and "light".  |
| plot_enable_pywry     | True                             | [True, False]        | Whether the application should enable PyWry. If PyWry is disabled  the image will open in your default browser  otherwise  it will be displayed within your editor or in a separate PyWry window.  |
| plot_pywry_width      | 1400                             | Any positive integer.  | PyWry window width.  |
| plot_pywry_height     | 762                              | Any positive integer.  | PyWry window height. |
| plot_open_export      | False                            | [True, False]        | Controls whether the "Save As" window should pop up as soon as the image is displayed."  |
| table_style           | dark                             | ["dark", "light"]         | "The default color style to use with the OpenBB Charting Extension tables. Options are "dark" and "light""   |
| request_timeout       | 15                               | Any positive integer.  | Specifies the timeout duration for HTTP requests.  |
| metadata              | True                             | [True, False]        | Enables or disables the collection of metadata  which provides information about operations  including arguments  duration  route  and timestamp. Disabling this feature may improve performance in cases where contextual information is not needed or when the additional computation time and storage space are a concern.  |
| output_type           | OBBject                          | ["OBBject", "dataframe", "numpy", "dict", "chart", "polars"] | Specifies the type of data the application will output when a command or endpoint is accessed. Note that choosing data formats only available in Python  such as `dataframe` | `numpy` or `polars` will render the application's API non-functional. |

User settings can be set from the Python interface directly.

```python
from openbb import obb

obb.user.profile
obb.user.credentials
obb.user.preferences
obb.user.defaults
```

Notably, `obb.user.defaults`, defines default providers for any command. They are stored in the `user_settings.json` file, under `routes`. Below is an example of what it might look like.

```json
{
    "credentials": {
        "benzinga_api_key": null,
        "fmp_api_key": null,
        "polygon_api_key": null,
        "fred_api_key": null
    },
    "defaults": {
        "routes": {
            "/equity/fundamental/balance": {
                "provider": "polygon"
            },
            "/equity/price/historical": {
                "provider": "fmp"
            },
            "/equity/news": {
                "provider": "benzinga"
            }
        }
    },
    {
        "preferences": {
          "data_directory": "~/OpenBBUserData", // Where to store data
          "export_directory": "~/OpenBBUserData/exports", // Where to store exports
          "cache_directory": "~/OpenBBUserData/cache", // Where to store the cache
          "user_styles_directory": "~/OpenBBUserData/styles/user", // Where to store user styles
          "charting_extension": "openbb_charting", // Charting extension to use
          "chart_style": "dark", // Chart style to use (dark or light)
          "plot_enable_pywry": true, // Whether to enable PyWry
          "plot_pywry_width": 1400, // PyWry width
          "plot_pywry_height": 762, // PyWry height
          "plot_open_export": false, // Whether to open plot image exports after they are created
          "table_style": "dark", // Table style to use (dark or light)
          "request_timeout": 15, // Request timeout
          "metadata": true, // Whether to include metadata in the output
          "output_type": "OBBject" // Our default output type (OBBject, dataframe, polars, numpy, dict, chart)
        }
    }
}
```

:::note

### **Notes on Preferences**

- If a `OpenBBUserData` folder in not in the home directory, the application will create one on first run. The user preferences with paths all default to this folder, be it exports, styles or data - this can be changed at any time to suit.
- The `OpenBBUserData` will still be created even if preferences are not pointing to it, this is because the application needs a place to store logs and other artifacts.
- One way of exporting files or images on the OpenBB Platform is to leverage that functionality from the OpenBB Charting Extension. The `export_directory` preference is the location where the extension will attempt to save such exports.

:::

## Basic Response

The output of every command is an object which contains the results of the request, along with additional information. It is a custom class, `OBBject`, and always returns with the fields listed below:

```console
id: ...                 # UUID Tag
results: ...            # Serializable results.
provider: ...           # Provider name.
warnings: ...           # List of warnings.
chart: ...              # Chart object.
extra: ...              # Extra info.
```

```python
from openbb import obb

data = obb.equity.price.historical("SPY", provider="polygon")

data
```

```console
OBBject

id: 06520558-d54a-7e53-8000-7aafc8a42694
results: [{'date': datetime.datetime(2022, 10, 5, 0, 0), 'open': 375.62, 'high': 37...
provider: polygon
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {'provider': 'polygon'}, 'st...
```

Additional class methods are helpers for converting the results to a variety of formats.

- `to_dict()`: converts to a dictionary, accepting all standard "orientation" parameters, i.e., "records"
- `to_df()` / `to_dataframe()`: converts to a Pandas DataFrame.
- `to_numpy()`: converts to a Numpy array.
- `to_polars()`: converts to a Polars table.

The output from the Fast API is a serialized version of this object, and these methods are lost on conversion.  OBBject can be reconstructed to recover the helpers by importing the model and validating the data.

```python
import requests
from openbb_core.app.model.obbject import OBBject

data = []
symbol="SPY"
url = f"http://127.0.0.1:8000/api/v1/equity/price/historical?provider=polygon&symbol={symbol}"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers, timeout=3)

if response.status_code == 200:
  data = OBBject.model_validate(response.json())

data.to_df()
```

:::info
The preferred output type can be set with a user preference.

```python
obb.user.preferences.output_type="dataframe"
```

:::

## Dynamic Command Execution

Dynamic execution provides an alternate entry point to functions. This method requires formatting the query as demonstrated below.

```python
from openbb_core.app.command_runner import CommandRunner
runner = CommandRunner()
output = runner.run(
    "/equity/fundamental/ratios",
    provider_choices={
        "provider": "fmp",
    },
    standard_params={
        "symbol" : "TSLA",
        "period" : "quarter",
    },
    extra_params={}
)
```

```console
>>> output
OBBject

id: 065241b7-bd9d-7313-8000-9406d8afab75
results: [{'symbol': 'TSLA', 'date': '2023-06-30', 'period': 'Q2', 'current_ratio':...
provider: fmp
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {'provider': 'fmp'}, 'standa...
```

## Commands and Provider Coverage

The installed commands and data providers are found under, `obb.coverage`.

```python
obb.coverage
```

```console
/coverage
    providers
    commands
```

`obb.coverage.providers` is a dictionary of the installed provider extensions, each with its own list of available commands.

`obb.coverage.commands` is a dictionary of commands, each with its own list of available providers for the data.

## Logging Out

Logging out and saving changes to preferences is done in the account module.

```python
obb.account.save()
obb.account.logout()
```

Any saved changes will be pulled to a new session after logging in.  Ending the Python session will be an equivalent to logging out, if `remember_me=False`.
