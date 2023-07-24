# THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE


- [THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE](#this-readme-is-a-work-in-progress-and-can-be-very-much-out-of-date-refresh-the-page-until-this-banner-is-gone)
  - [1. Introduction](#1-introduction)
  - [2. How to install?](#2-how-to-install)
  - [3. How to add an extension?](#3-how-to-add-an-extension)
  - [4. Usage](#4-usage)
    - [4.1. Static version](#41-static-version)
        - [4.1.1. Command output](#411-command-output)
        - [4.1.2. Utilities](#412-utilities)
        - [4.1.3. OpenBB Hub account](#413-openbb-hub-account)
  - [5. REST API](#5-rest-api)
    - [5.1. Test users](#51-test-users)
  - [6. Front-end typing](#6-front-end-typing)

## 1. Introduction

This is a collection of functions that allow extracting, transforming and exporting financial data.

These functions are special:

- They provide configuration
- They will be automatically turned into REST API endpoint
- They allow sharing data between commands


## 2. How to install?

**GIT CLONE**

Git clone the repository:

```bash
git clone git@github.com:OpenBB-finance/OpenBBTerminal.git
```

**INSTALL**

Go to `openbb_sdk` folder and install the package.

```bash
cd openbb_sdk
poetry install
```


## 3. How to add an extension?

**PROJECT**

Build a Python package:

```bash
poetry new openbb-sdk-my_extension
```

**COMMAND**

Add a router and a command.

```python
# File my_extension/extension_router.py

from openbb_core.app.router import Router

router = Router(prefix="/router_name")

@router.command
def some_command(
    some_param: some_param_type,
) -> CommandOutput[Item]:
    pass
```

If your command only makes use of a `openbb-provider` model, there is no need to repeat its structure in the parameters. Just pass the model name as an argument. This is an example how we do it for `stocks.load` which only depends on `StockEOD` model defined in `openbb-provider`.
```python
@router.command(model="StockEOD")
def load(
    cc: CommandContext,                 # user settings inside
    provider_choices: ProviderChoices,  # available providers
    standard_params: StandardParams,    # symbol, start_date, etc.
    extra_params: ExtraParams,          # provider specific parameters
) -> CommandOutput[BaseModel]:
    """Load stock data for a specific ticker."""
    return CommandOutput(results=Query(**locals()).execute())
```

**ENTRYPOINT**

Add an entrypoint for the extension inside your `pyproject.toml` file.

```toml
# File pyproject.toml
packages = [{include = "openbb_sdk_my_extension"}]
...
[tool.poetry.extensions."openbb_extensions"]
extension_name_space = "my_extension.extension_router:router"
```

**INSTALL**

Install your extension.

```bash
cd openbb_sdk_my_extension
poetry install
```

# 4. Usage

Update the settings

```
# FILE <your_home_directory>/.openbb_sdk/user_settings.json
{
    "credentials": {
        "benzinga_api_key": null,
        "fmp_api_key": null,
        "polygon_api_key": null
    },
    "defaults": {
        "routes": {
            "/stocks/fa/balance": {
                "provider": "polygon"
            },
            "/stocks/load": {
                "provider": "fmp"
            },
            "/stocks/news": {
                "provider": "benzinga"
            }
        }
    }
}
```

```
# FILE <your_home_directory>/.openbb_sdk/system_settings.json
{
    "run_in_isolation": null,
    "dbms_uri": null
}
```

## 4.1 Static version

Run your command:

```python
from openbb import sdk

output = sdk.stocks.load(
    symbol="TSLA",
    start_date="2023-01-01",
    provider="fmp",
    chart=True
    )
```

### 4.1.1. Command output

Each command will always return a  `CommandOutput`. There you will find:

- `results`: the data returned by the command, if any
- `provider`: the chart data and format, if any, if any
- `warnings`: a list of warnings caught during the command execution, if any
- `error`: an `Error` with any exception that occurred during the command execution, if any
- `chart`: a `Chart` with chart data and format, if any

**HELPERS**

To help you manipulate or visualize the data we make some helpers available.

- `to_dataframe`: transforms `results` into a pandas DataFrame
```python
>>> output.to_dataframe()
              open    high       low   close   adj_close    ...
date
2023-07-21  268.00  268.00  255.8000  260.02  260.019989    ...
2023-07-20  279.56  280.93  261.2000  262.90  262.899994    ...
2023-07-19  296.04  299.29  289.5201  291.26  291.260010    ...
```

- `to_dict`: transforms `results` into a dict of lists
```python
>>> output.to_dict()
{
    'open': [268.0, 279.56, 296.04],
    'high': [268.0, 280.93, 299.29],
    'low': [255.8, 261.2, 289.5201],
    'close': [260.02, 262.9, 291.26],
    'adj_close': [260.019989, 262.899994, 291.26001],
    ...
}
```

- `show`: displays `chart.content` to a chart
```python
>>> output.show()
# Jupyter Notebook: inline chart
# Python Interpreter: opens a PyWry window with the chart
```

- `to_plotly_json`: proxy to `chart.content`
```python
>>> output.to_plotly_json()
{'data':
    [
        {
            'close': [260.02, 262.9, 291.26],
            'decreasing': {'line': {'width': 1.1}},
            'high': [268.0, 280.93, 299.29],
            'increasing': {'line': {'width': 1.1}},
            ...
        }
    ...
    ]
}
```

### 4.1.2. Utilities

**SETTINGS**

These are your user settings, you can change them at anytime and they will be applied. Don't forget to `sdk.account.save()` if you want these changes to persist.

```python
from openbb import sdk

sdk.settings.profile
sdk.settings.credentials
sdk.settings.preferences
sdk.settings.defaults
```

**SYSTEM**

Check your system settings. Most of the properties are read-only during runtime, so any changes there will be void.

- `debug_mode`: here if you set `debug_mode = True` any exception that occurs during execution will be raised immediatly.

```python
from openbb import sdk

sdk.system
```

**COVERAGE**
```python
from openbb import sdk

# Commands
>>> sdk.coverage.commands
{
    '/crypto/load': ['fmp', 'polygon'],
    '/economy/const': ['fmp'],
    '/economy/cpi': ['fred'],
    ...
}

# Providers
sdk.coverage.providers
{
    'fmp':
    [
        '/crypto/load',
        '/economy/const',
        '/economy/index',
        ...
    ],
    'fred': ['/economy/cpi'],
    ...
}
```

### 4.1.3. OpenBB Hub account

```python
from openbb import sdk

# Login with email, password or SDK token
sdk.account.login(email="your_email", password="your_password", remember_me=True)  # pragma: allowlist secret

# Change a credential
sdk.account.settings.credentials.polygon_api_key = "new_key"  # pragma: allowlist secret

# Save account changes
sdk.account.save()

# Refresh account with latest changes
sdk.account.refresh()

# Logout
sdk.account.logout()
```

## 5. REST API

OpenBB SDK comes with a ready to use Rest API built with FastAPI.

```
# FILE <your_home_directory>/.openbb_sdk/user_settings.json
{
    "credentials": {
        "benzinga_api_key": null,
        "fmp_api_key": null,
        "polygon_api_key": null
    },
    "defaults": {
        "routes": {
            "/stocks/fa/balance": {
                "provider": "polygon"
            },
            "/stocks/load": {
                "provider": "fmp"
            },
            "/stocks/news": {
                "provider": "benzinga"
            }
        }
    }
}
```

```
# FILE <your_home_directory>/.openbb_sdk/system_settings.json
{
    "run_in_isolation": null,
    "dbms_uri": null
}
```

Start the application:

```bash
uvicorn openbb_core.api.rest_api:app --reload
```

## 5.1 Test users

There are 2 default users for testing purpose:

User "openbb"
- username : openbb
- password : openbb


User "finance"
- username : finance
- password : finance

## 6. Front-end typing

Here are libraries to get frontend typing.

openapi-typescript + openapi-fetch
- https://github.com/drwpow/openapi-typescript


openapi-generator
- https://fastapi.tiangolo.com/advanced/generate-clients/
