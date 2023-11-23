# THIS README IS A WORK IN PROGRESS

- [THIS README IS A WORK IN PROGRESS](#this-readme-is-a-work-in-progress)
  - [1. Introduction](#1-introduction)
    - [1.1 Data Providers](#11-data-providers)
    - [1.2 Data Standardization](#12-data-standardization)
    - [1.3 Key Elements](#13-key-elements)
  - [2. How to install?](#2-how-to-install)
    - [Git clone](#git-clone)
    - [Install](#install)
  - [3. How to add an extension?](#3-how-to-add-an-extension)
    - [Project](#project)
    - [Command](#command)
    - [Entrypoint](#entrypoint)
    - [Install extension](#install-extension)
  - [4. Usage](#4-usage)
  - [4.1 Static version](#41-static-version)
    - [4.1.1. OBBject](#411-obbject)
      - [Helpers](#helpers)
      - [Extensions](#extensions)
    - [4.1.2. Utilities](#412-utilities)
      - [User settings](#user-settings)
      - [Preferences](#preferences)
      - [**Notes on preferences**](#notes-on-preferences)
      - [System settings](#system-settings)
      - [Coverage](#coverage)
    - [4.1.3. OpenBB Hub Account](#413-openbb-hub-account)
    - [4.1.4. Command execution](#414-command-execution)
    - [4.1.5. Environment variables](#415-environment-variables)
  - [4.2 Dynamic version](#42-dynamic-version)
  - [5. REST API](#5-rest-api)
    - [5.1 HTTPS](#51-https)
    - [5.2 Docker](#52-docker)
    - [5.3 Authentication](#53-authentication)
      - [5.3.1 HTTP Basic Auth](#531-http-basic-auth)
      - [5.3.2 Custom authentication](#532-custom-authentication)
  - [6. Front-end typing](#6-front-end-typing)

## 1. Introduction

This directory contains the OpenBB Platform's core functionality. It allows you to create an [extension](../../extensions/README.md) or a [provider](../../providers/README.md) that will be automatically turned into REST API endpoint and allow sharing data between commands.

### 1.1 Data Providers

OpenBB aims to give a coherent access to financial data providers by introducing standardization procedures.

### 1.2 Data Standardization

It's like teaching everyone to speak the same language with their data so we can understand and compare it easily.

**Think of it as a part of**:

Data normalization, a bigger way of organizing data.

**What We Do**:

- **Match Column Names and Formats**: Like making sure everyone calls a "closing price" the same thing.

- **For instance**: Some might say "Close", others might say "c". We make sure everyone uses one term.
**Unify Date and Time Styles**: Like having everyone use the same calendar format.

**Example**: Whether it's "YYYY-MM-DD" or "MM-DD-YYYY", we pick one style for everyone.

**What We Don’t Do**:

- **Cleaning Data**: We don't act like data detectives and remove mistakes from what providers give us.

- **Change & Combine Data**: Tweaking data or mixing data from different places.

### 1.3 Key Elements

- **QueryParams** : The input model for a particular query. To load equity market data, we would have `EquityPriceQueryParams`, which would have fields like `symbol`, `start_date`, and `end_date`. You can find the standard query params inside the `standard_models` directory.
- **Data** : The output model of a particular query. Equity market data would be `EquityPriceData` and have fields such as `Open`, `High`, `Low`, `Close`, and `Volume`. You can find the standard data models inside the `standard_models` directory.
- **Fetcher** : Class containing a set of methods to receive query parameters, extract data and transform it. This class is responsible for implementing the standardization procedures.
- **Provider** : Entry point class for each provider extension. Contains information about the provider, it's required credentials and available fetchers.
- **RegistryLoader** : Loads the registry with the installed provider extensions.
- **Registry** : Maintains a registry of provider extensions installed.
- **RegistryMap** : Stores the complete characterization of each provider. It centralizes information like required credentials, standardized and extra query parameters/data by provider.
- **QueryExecutor** : Executes a given query, routing it to the respective provider and fetcher.

## 2. How to install?

### Git clone

Git clone the repository:

```bash
git clone git@github.com:OpenBB-finance/OpenBBTerminal.git
```

### Install

Go to `openbb_platform` folder and install the package.

```bash
cd openbb_platform
poetry install
```

## 3. How to add an extension?

### Project

Build a Python package:

```bash
poetry new openbb-platform-my_extension
```

### Command

Add a router and a command in the `openbb_platform/extensions/<my_extension_folder>/<openbb_my_extension>/<my_extension>_router.py`

```python
from openbb_core.app.router import Router

router = Router(prefix="/router_name")

@router.command
async def some_command(                # create an async function
    some_param: some_param_type,
) -> OBBject[Item]:
    pass
```

If your command only makes use of a standard model defined inside `openbb_core/provider/standard_models` directory, there is no need to repeat its structure in the parameters. Just pass the model name as an argument.

This is an example how we do it for `equity.price.historical` which only depends on `EquityHistorical` model defined in `openbb-core.provider.standard_models`:

```python
@router.command(model="EquityHistorical")
async def historical(                   # create an async function
    cc: CommandContext,                 # user settings inside
    provider_choices: ProviderChoices,  # available providers
    standard_params: StandardParams,    # symbol, start_date, etc.
    extra_params: ExtraParams,          # provider specific parameters
) -> OBBject[BaseModel]:
    """Load equity data for a specific ticker."""
    return await OBBject.from_query(Query(**locals()))
```

### Entrypoint

Add an entrypoint for the extension inside your `pyproject.toml` file.

```toml
packages = [{include = "openbb_platform_my_extension"}]
...
[tool.poetry.extensions."openbb_extensions"]
extension_name_space = "my_extension.extension_router:router"
```

### Install extension

Install your extension.

```bash
cd openbb_platform_my_extension
poetry install
```

## 4. Usage

Update your credentials and default providers by modifying the `.openbb_platform/user_settings.json` inside your home directory:

```{json}
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
            "/news/company": {
                "provider": "benzinga"
            }
        }
    }
}
```

Update your system settings by modifying the `.openbb_platform/system_settings.json` file inside your home directory:


```{json}
{
    "test_mode": true
}
```

## 4.1 Static version

Run your command:

```python
from openbb import obb

output = obb.equity.price.historical(
    symbol="TSLA",
    start_date="2023-01-01",
    provider="fmp",
    chart=True
)
```

### 4.1.1. OBBject

Each command will always return a  `OBBject`. There you will find:

- `results`: the data returned by the command `None`
- `provider`: the provider name (only available provider names allowed) used to get the data or `None`
- `warnings`: `List[Warning_]` with warnings caught during the command execution or `None`
- `error`: an `Error` with any exception that occurred during the command execution or `None`
- `chart`: a `Chart` with chart data and format or `None`

#### Helpers

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

- `show`: displays the figure

```python
>>> output.show()
# Jupyter Notebook: inline chart
# Python Interpreter: opens a PyWry window with the chart
```

- `to_chart`: create or update the chart and returns the figure

```python
>>> fig = output.to_chart()
>>> fig = type(fig)

openbb_charting.core.openbb_figure.OpenBBFigure
```

#### Extensions

Steps to create an `OBBject` extension:

1. Set the following as entry point in your extension .toml file and install it:

    ```toml
    ...
    [tool.poetry.plugins."openbb_obbject_extension"]
    example = "openbb_example:ext"
    ```

2. Extension code:

    ```python
    from openbb_core.app.model.extension import Extension
    ext = Extension(name="example", credentials=["some_api_key"])
    ```

3. Optionally declare an `OBBject` accessor, it will use the extension name:

    ```python
    @ext.obbject_accessor
    class Example:
        def __init__(self, obbject):
            self._obbject = obbject

        def hello(self):
            api_key = self._obbject._credentials.some_api_key
            print(f"Hello, this is my credential: {api_key}!")
    ```

    Usage:

    ```shell
    >>> from openbb import obb
    >>> obbject = obb.equity.price.historical("AAPL")
    >>> obbject.example.hello()
    Hello, this is my credential: None!
    ```

### 4.1.2. Utilities

#### User settings

These are your user settings, you can change them anytime and they will be applied. Don't forget to `obb.account.save()` if you want these changes to persist.

```python
from openbb import obb

obb.user.profile
obb.user.credentials
obb.user.preferences
obb.user.defaults
```

#### Preferences

Check your preferences by adjusting the `user_settings.json` file inside your **home** directory.
If you want to proceed with the default settings, you don't have to touch this file.

Here is an example of how your `user_settings.json` file can look like:

```json
{
    "chart_style": "light",
    "table_style": "light",
    "plot_enable_pywry": true,
    "plot_pywry_width": 800,
    "plot_pywry_height": 800,
    "request_timeout": 30,
    "metadata": false,
    "output_type": "dataframe"
}
```

> Note that the user preferences shouldn't be confused with environment variables.

These are the available preferences and respective descriptions:

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

:::note

#### **Notes on preferences**

- If you don't have a `OpenBBUserData` folder in your home directory, the application will create one for you the first time you run it. The user preferences related with paths all default to this folder, be it exports, styles or data - this can be changed at any time to fit your needs.
- The `OpenBBUserData` will still be created even if you don't have your preferences pointing to it, this is because the application needs a place to store logs and other artifacts.
- One way of exporting files or images on the OpenBB Platform is to leverage that functionality on the OpenBB Charting Extension. The `export_directory` preference is the location where the extension will attempt to save such exports.

:::

#### System settings

Check your system settings.

```python
from openbb import obb

obb.system
```

#### Coverage

Obtain the coverage of providers and commands.

```python
>>> obb.coverage.commands
{
    '.crypto.load': ['fmp', 'polygon'],
    '.economy.const': ['fmp'],
    '.economy.cpi': ['fred'],
    ...
}
```

```python
>>> obb.coverage.providers
{
    'fmp':
    [
        '.crypto.load',
        '.economy.const',
        '.economy.index',
        ...
    ],
    'fred': ['.economy.cpi'],
    ...
}
```

### 4.1.3. OpenBB Hub Account

You can login to your OpenBB Hub account and save your credentials there to access them from any device.

```python
from openbb import obb

# Login with personal access token
obb.account.login(pat="your_pat", remember_me=True)  # pragma: allowlist secret

# Login with email, password or Platform token
obb.account.login(email="your_email", password="your_password", remember_me=True)  # pragma: allowlist secret

# Change a credential
obb.user.credentials.polygon_api_key = "new_key"  # pragma: allowlist secret

# Save account changes
obb.account.save()

# Refresh account with latest changes
obb.account.refresh()

# Logout
obb.account.logout()
```

> Note: credentials are stored as Pydantic `SecretStr` objects. This means that they will be masked when printed or displayed in a Jupyter Notebook. To get the actual value, use `obb.user.credentials.polygon_api_key.get_secret_value()`.

### 4.1.4. Command execution

How do we execute commands?

OpenBB Platform core is a REST API powered by FastAPI. We use this feature to run commands both in a web server setting and also in the `openbb` python package.

If you are using the `openbb` package, running the command below triggers a "request" to the `CommandRunner` class. The "request" will be similar to the one found in [4.2 Dynamic version](#42-dynamic-version). This will hit the endpoint matching the command and return the result.

```python
from openbb import obb

obb.equity.price.historical(
    symbol="TSLA",
    start_date="2023-07-01",
    end_date="2023-07-25",
    provider="fmp",
    chart=True
    )
```

### 4.1.5. Environment variables

The OS environment is only read once before the program starts, so make sure you change the variable before importing the Platform. We use the prefix "OPENBB_" to avoid polluting the environment (no pun intended).

To apply an environment variable use one of the following:

1. Temporary: use this snippet

    ```python
    import os
    os.environ["OPENBB_DEBUG_MODE"] = "True"
    from openbb import obb
    ```

2. Persistent: create a `.env` file in `/.openbb_platform` folder inside your home directory with

    ```text
    OPENBB_DEBUG_MODE="False"
    ```

The variables we use are:

- `OPENBB_API_AUTH`: enables API endpoint authentication
- `OPENBB_API_USERNAME`: sets API username
- `OPENBB_API_PASSWORD`: sets API password
- `OPENBB_API_AUTH_EXTENSION`: specifies which authentication extension to use
- `OPENBB_AUTO_BUILD`: enables automatic package build on import
- `OPENBB_CHARTING_EXTENSION`: specifies which charting extension to use
- `OPENBB_DEBUG_MODE`: enables debug mode
- `OPENBB_DEV_MODE`: enables development mode
- `OPENBB_HUB_BACKEND`: sets the backend for the OpenBB Hub

## 4.2 Dynamic version

You can also use the dynamic version to consume the API endpoints from Python itself.

In fact, the static version makes use of this feature to run each command. Take a look at the example below:

```python
>>> from openbb_core.app.command_runner import CommandRunner
>>> runner = CommandRunner()
>>> output = runner.run(
    "/equity/price/historical",
    provider_choices={
        "provider": "fmp",
    },
    standard_params={
        "symbol": "TSLA",
        "start_date": "2023-07-01",
        "end_date": "2023-07-25",
    },
    extra_params={},
    chart=True,
)
>>> output
OBBject

id: ...                 # UUID Tag
results: ...            # Serializable results.
provider: ...           # Provider name.
warnings: ...           # List of warnings.
chart: ...              # Chart object.
extra: ...              # Extra info.
```

## 5. REST API

OpenBB Platform comes with a ready to use Rest API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_core.api.rest_api:app --reload
```

### 5.1 HTTPS

If you want to run your FastAPI app over HTTPS locally you can use [mkcert](https://github.com/FiloSottile/mkcert) and pass the certificate and key to `uvicorn`.

0. Install `mkcert` (see instructions [here](https://github.com/FiloSottile/mkcert))
1. cd into "openbb_platform/platform/core/openbb_core/api"
2. Run the following commands:

    ```shell
    mkcert -install
    mkcert localhost 127.0.0.1 ::1
    ```

    You will see two files created in the current directory.
    - Certificate: "localhost+2.pem"
    - Key: "localhost+2-key.pem"

3. Change the code to start the server inside "rest_api.py" to:

    ```python
    if __name__ == "__main__":
        import uvicorn

        uvicorn.run(
            "openbb_core.api.rest_api:app",
            reload=True,
            ssl_keyfile="./localhost+2-key.pem",
            ssl_certfile="./localhost+2.pem",
        )
    ```

4. Run the server from the terminal with:

    ```shell
    python rest_api.py
    ```

    Your app will be available at https://127.0.0.1:8000/

### 5.2 Docker

You can use the API through Docker.

We provide a `.dockerfile`` in OpenBB [repo](https://github.com/OpenBB-finance/OpenBBTerminal).

To build the image, you can run the following command from the repo root:

```bash
docker build -f build/docker/api.dockerfile -t openbb-platform:latest .
```

To run this newly-built image:

```bash
docker run --rm -p 8000:8000 -v ~/.openbb_platform:/root/.openbb_platform openbb-platform:latest
```

This will mount the local `~/.openbb_platform` directory into the Docker container so you can use the API keys from there and it will expose the API on port `8000`.

### 5.3 Authentication

By default the API launches with no authentication.

This means that if you deploy it on some network, any client will be served.

#### 5.3.1 HTTP Basic Auth

> This method is not recommended for production environments.

If you are in a rush and still want some layer of security you can use the FastAPI HTTP Basic Auth we included in the API. To enable this feature, set the following environment variables (more info on environment variables here [4.1.5. Environment variables](#415-environment-variables)) and replace the username and password with your preferred values:

```.env
OPENBB_API_AUTH="True"
OPENBB_API_USERNAME="some_user"
OPENBB_API_PASSWORD="some_pass"
```

The application will expect a header that contains username and password in the form of `Basic <username:password>`, where "username:password" is encoded in Base64. Pass this in every request you make to the API inside the headers "Authorization" field.

Here is an example using `base64` and `requests` libraries:

```python
import base64
import requests

msg = "some_user:some_pass"
msg_bytes = msg.encode('ascii')
base64_bytes = base64.b64encode(msg_bytes)
base64_msg = base64_bytes.decode('ascii')

requests.get(
    url="http://127.0.0.1:8000/api/v1/equity/price/historical?provider=fmp&symbol=AAPL",
    headers={"Authorization": f"Basic {base64_msg}"}
)
``````


#### 5.3.2 Custom authentication

For custom authentication methods you can plug an authentication extension into the API. To do so, set the environment variable `OPENBB_API_AUTH_EXTENSION` with the name of the extension you want to use.

The extension entry point defined in the respective "pyproject.toml should be similar to

```toml
[tool.poetry.plugins."openbb_core_extension"]
auth = "openbb_auth.auth_router:router"
```

In this case, the `auth_router.py` module should define:

- `router`: `fastapi.APIRouter` with relevant user authentication endpoints (e.g. /token)
- `auth_hook`: awaitable function that checks if given authorization credentials are valid and raises an `HTTP_401_UNAUTHORIZED` exception if not.
- `user_settings_hook`: awaitable function that returns a `UserSettings` object. This will be called by every command endpoint to obtain the user settings for a given user and should depend on `auth_hook` to be executed first.

## 6. Front-end typing

Here are libraries to get frontend typing.

openapi-typescript + openapi-fetch

- <https://github.com/drwpow/openapi-typescript>

openapi-generator

- <https://fastapi.tiangolo.com/advanced/generate-clients/>
