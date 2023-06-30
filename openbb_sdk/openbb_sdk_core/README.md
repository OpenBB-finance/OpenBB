# THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE


## 1. Introduction

This is a collection of functions that allow extracting, transforming and exporting financial data.

These functions are special:

- They provide configuration
- They will be automatically turned into REST API endpoint
- They allow sharing data between commands

### 1.1. Table of contents
- [THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE](#this-readme-is-a-work-in-progress-and-can-be-very-much-out-of-date-refresh-the-page-until-this-banner-is-gone)
  - [1. Introduction](#1-introduction)
    - [1.1. Table of contents](#11-table-of-contents)
  - [2. How to install?](#2-how-to-install)
  - [3. How to add a plugin?](#3-how-to-add-a-plugin)
  - [5. Usage](#5-usage)
    - [5.1. Update the settings](#51-update-the-settings)
    - [5.2. Define the CommandRunnerSession](#52-define-the-commandrunnersession)
      - [5.2.1. Use your OpenBB Hub account](#521-use-your-openbb-hub-account)
    - [5.3. Define the Command parameters](#53-define-the-command-parameters)
    - [5.4. Run the command](#54-run-the-command)
    - [5.5 Run the static version (LEAST STABLE ON DEVELOP)](#55-run-the-static-version-least-stable-on-develop)
      - [5.5.1. App settings and system](#551-app-settings-and-system)
      - [5.5.2. Use your OpenBB Hub account](#552-use-your-openbb-hub-account)
  - [6. See routes](#6-see-routes)
  - [7. Using the REST API](#7-using-the-rest-api)
  - [8. Static version (BEING REFACTORED)](#8-static-version-being-refactored)
  - [9. Front-end typing](#9-front-end-typing)
  - [10. Default User](#10-default-user)

## 2. How to install?

**GIT CLONE**

Git clone the repository:

```bash
git clone git@github.com:OpenBB-finance/openbb-sdk-core.git
```

**INSTALL**

Install the package.

```bash
poetry install
```


## 3. How to add a plugin?

**PROJECT**

Build a Python package:

```bash
poetry new openbb-sdk-my_plugin
```

**COMMAND**

Add a router and a command.

```python
# File my_plugin/plugin_router.py

from openbb_sdk_core.app.router import Router

router = Router(prefix="/my_name")

@router.command
def some_command(
    cc: CommandContext,
    query: StockQueryParams,
    provider: ProviderName,
) -> CommandOutput[Item]:
    pass
```

**ENTRYPOINT**

Add an entrypoint for the plugin inside your `pyproject.toml` file.

```toml
# File pyproject.toml
packages = [{include = "openbb_sdk_my_plugin"}]
...
[tool.poetry.plugins."openbb_plugins"]
plugin_name_space = "my_plugin.plugin_router:router"
```

**INSTALL**

Install your plugin.

```bash
poetry install
```

## 5. Usage

### 5.1. Update the settings

```
# FILE settings/user_settings.json
{
  "credentials": {
      "benzinga_api_key": null,
      "fmp_api_key": null,
      "polygon_api_key": null
  }
}
```

### 5.2. Define the CommandRunnerSession

```python
from datetime import datetime
from openbb_sdk_core.app.command_runner import CommandRunner, CommandRunnerSession

app = CommandRunnerSession()
```

#### 5.2.1. Use your OpenBB Hub account
```python

# Create Hub manager
hm = HubManager()

# Connect with email, password or SDK token
hm.connect(email="your_email", password="your_password")  # pragma: allowlist secret

# Pull your settings
user_settings = hm.pull()

# Make the app aware
app = CommandRunnerSession(user_settings=user_settings)

# Change a credential
user_settings.credentials.polygon_api_key = "new_key"  # pragma: allowlist secret

# Send change back to Hub
hm.push(user_settings)

# Disconnect
hm.disconnect()
```

### 5.3. Define the Command parameters

```python
from datetime import datetime
from openbb_provider.model.query.stock_query import StockQueryParams
from openbb_provider.provider.provider_registry import ProviderName

stock_query = StockQueryParams(
    symbol="TSLA",
    start_date=datetime.fromisoformat("2023-05-01"),
    end_date=datetime.fromisoformat("2023-05-04"),
)
provider = ProviderName.fmp
```


### 5.4. Run the command

```python
command_result = app.run(
    "/openbb/stocks/fetch",
    query=stock_query,
    provider=provider,
).output

# Access the StockData
command_result.item
```

### 5.5 Run the static version (LEAST STABLE ON DEVELOP)

You also have the static version.

First update the cache:

```python
from openbb_sdk_core.app.static.cache_builder import CacheBuilder

CacheBuilder.build()
```

Then run your command:

```python
from openbb_sdk_core import openbb

stock_data = openbb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
stock_data.dataframe()
```

#### 5.5.1. App settings and system
```python
from openbb_sdk_core.app.static import app
app.settings
app.settings.profile
app.settings.credentials
app.settings.preferences

app.system
```

#### 5.5.2. Use your OpenBB Hub account
```python
from openbb_sdk_core.app.static import app

# Login with email, password or SDK token
app.account.login(email="your_email", password="your_password", remember_me=True)  # pragma: allowlist secret

# Change a credential
app.account.settings.credentials.polygon_api_key = "new_key"  # pragma: allowlist secret

# Save account changes
app.account.save()

# Refresh account with latest changes
app.account.refresh()

# Logout
app.account.logout()
```

## 6. See routes

```python
from openbb_sdk_core.app.router import CommandMap

command_map = CommandMap()
command_map.map
```

```
"{
'/ff/qa/load_random': <function ff_plugin.router.qa.qa_router.load_random(name: str) -> ff_plugin.router.qa.qa_router.CommandOutput[RandData]>,
'/ff/qa/calc_ret': <function ff_plugin.router.qa.qa_router.calc_ret(column: str, rand_data: ff_plugin.router.qa.qa_router.RandData) -> ff_plugin.router.qa.qa_router.CommandOutput[ReturnSeries]>,
'/ff/qa/garch': <function ff_plugin.router.qa.qa_router.garch(return_series: ff_plugin.router.qa.qa_router.ReturnSeries, p: int = 1, o: int = 0, q: int = 1, mean: str = 'constant', horizon: int = 100) -> ff_plugin.router.qa.qa_router.CommandOutput[GARCH]>,
'/ff/qa/summary': <function ff_plugin.router.qa.qa_router.summary(rand_data: ff_plugin.router.qa.qa_router.RandData) -> ff_plugin.router.qa.qa_router.CommandOutput[Dataset]>,
...
}
```

## 7. Using the REST API

Setup `settings/user_settings.json`:

```
# FILE settings/user_settings.json
{
  "credentials": {
      "benzinga_api_key": null,
      "fmp_api_key": null,
      "polygon_api_key": null
  }
}
```

Start the application:

```bash
uvicorn openbb_sdk_core.api.rest_api:app --reload
```


## 8. Static version (BEING REFACTORED)

Usage

```python


from openbb_sdk_core.app.static.cache_builder import CacheBuilder

CacheBuilder.build()

from openbb_sdk_core import openbb

openbb.stocks.load(...)
```



## 9. Front-end typing

Here are libraries to get frontend typing.

openapi-typescript + openapi-fetch
- https://github.com/drwpow/openapi-typescript


openapi-generator
- https://fastapi.tiangolo.com/advanced/generate-clients/


## 10. Default User

There are 2 default users for testing purpose:

User "openbb"
- username : openbb
- password : openbb


User "finance"
- username : finance
- password : finance
