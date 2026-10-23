
# Contributing to the OpenBB Platform

<!-- markdownlint-disable MD033 MD024 -->

- [Contributing to the OpenBB Platform](#contributing-to-the-openbb-platform)
  - [Introduction](#introduction)
    - [Quick look into the OpenBB Platform](#quick-look-into-the-openbb-platform)
      - [What is the Standardization Framework?](#what-is-the-standardization-framework)
        - [Standardization Caveats](#standardization-caveats)
        - [Standard QueryParams Example](#standard-queryparams-example)
        - [Standard Data Example](#standard-data-example)
      - [What is an extension?](#what-is-an-extension)
        - [Types of extensions](#types-of-extensions)
  - [Dependency Management](#dependency-management)
    - [High-Level Overview](#high-level-overview)
    - [Package Layout](#package-layout)
    - [Installation](#installation)
    - [Managing Dependencies with uv](#managing-dependencies-with-uv)
  - [Developer Guidelines](#developer-guidelines)
    - [Expectations for Developers](#expectations-for-developers)
    - [How to build OpenBB extensions?](#how-to-build-openbb-extensions)
    - [Building Extensions: Best Practices](#building-extensions-best-practices)
    - [How to add a new data point?](#how-to-add-a-new-data-point)
      - [Identify which type of data you want to add](#identify-which-type-of-data-you-want-to-add)
      - [Check if the standard model exists](#check-if-the-standard-model-exists)
        - [Create Query Parameters model](#create-query-parameters-model)
        - [Create Data Output model](#create-data-output-model)
        - [Build the Fetcher](#build-the-fetcher)
      - [Make the provider visible](#make-the-provider-visible)
    - [How to add custom data sources?](#how-to-add-custom-data-sources)
      - [OpenBB Platform commands](#openbb-platform-commands)
    - [Architectural considerations](#architectural-considerations)
      - [Important classes](#important-classes)
      - [The TET pattern](#the-tet-pattern)
      - [Errors](#errors)
      - [Data processing commands](#data-processing-commands)
        - [Python Interface](#python-interface)
        - [API Interface](#api-interface)
  - [Contributor Guidelines](#contributor-guidelines)
    - [Expectations for Contributors](#expectations-for-contributors)
    - [Quality Assurance](#quality-assurance)
      - [Linting and type checking](#linting-and-type-checking)
      - [Unit tests](#unit-tests)
      - [Integration tests](#integration-tests)
      - [Import time](#import-time)
    - [Sharing your extension](#sharing-your-extension)
      - [Publish your extension to PyPI](#publish-your-extension-to-pypi)
        - [Build](#build)
        - [Publish](#publish)
    - [Manage extensions](#manage-extensions)
      - [Add an extension as a dependency](#add-an-extension-as-a-dependency)
    - [Write code and commit](#write-code-and-commit)
      - [How to create a PR?](#how-to-create-a-pr)
        - [Branch Naming Conventions](#branch-naming-conventions)

## Introduction

This document provides guidelines for contributing to the OpenBB Platform.
Throughout this document, we will be differentiating between two types of contributors: Developers and Contributors.

1. **Developers**: Those who are building new features or extensions for the OpenBB Platform or leveraging the OpenBB Platform.
2. **Contributors**: Those who contribute to the existing codebase, by opening a [Pull Request](#how-to-create-a-pr) thus giving back to the community.

**Why is this distinction important?**

The OpenBB Platform is designed as a foundation for further development. We anticipate a wide range of creative use cases for it. Some use cases may be highly specific or detail-oriented, solving particular problems that may not necessarily fit within the OpenBB Platform Github repository. This is entirely acceptable and even encouraged. This document
provides a comprehensive guide on how to build your own extensions, add new data points, and more.

The **Developer** role, as defined in this document, can be thought of as the foundational role. Developers are those who use the OpenBB Platform as is or build upon it.

Conversely, the **Contributor** role refers to those who enhance the OpenBB Platform codebase (either by directly adding to the OpenBB Platform or by extending the [extension repository](/openbb_platform/extensions/)). Contributors are willing to go the extra mile, spending additional time on quality assurance, testing, or collaborating with the OpenBB
development team to ensure adherence to standards, thereby giving back to the community.

### Quick look into the OpenBB Platform

The OpenBB Platform is built by the Open-Source community and is characterized by its core and extensions. The core handles data integration and standardization, while the extensions enable customization and advanced functionalities. The OpenBB Platform is designed to be used both from a Python interface and a REST API.

The REST API is built on top of FastAPI. With `openbb-platform-api` installed, start it with:

```bash
openbb-api
```

The bare FastAPI app, `openbb_core.api.rest_api:app`, also runs under any ASGI server:

```bash
uvicorn openbb_core.api.rest_api:app --host 127.0.0.1 --port 8000 --reload
```

The Python interface we provide to users is the `openbb` Python package, which ships inside `openbb-core`.

The code you will find in `openbb/package` is generated from a script and it is just a wrapper around `openbb-core` and any installed extensions.

When the user runs `import openbb`, `from openbb import obb` or other variants, the script that generates the packaged code is triggered. It detects if there are new extensions installed in the environment and rebuilds the packaged code accordingly. If new extensions are not found, it just uses the current packaged version. Set `OPENBB_AUTO_BUILD=false` to disable this.

When you are developing chances are you want to manually trigger the package rebuild.

You can do that with:

```bash
openbb-build
```

The Python interface can be imported with:

```python
from openbb import obb
```

This document will take you through two types of contributions:

1. Building a custom extension
2. Contributing directly to the OpenBB Platform

Before moving forward, please take a look at the high-level view of the OpenBB Platform architecture. We will go over each bit in this document.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/OpenBB-finance/OpenBB/assets/74266147/c9a5a92a-28b6-4257-aefc-deaebe635c6a">
  <img alt="OpenBB Platform High-Level Architecture" src="https://github.com/OpenBB-finance/OpenBB/assets/74266147/c9a5a92a-28b6-4257-aefc-deaebe635c6a">
</picture>

#### What is the Standardization Framework?

The Standardization Framework is a set of tools and guidelines that enable the user to query and obtain data in a consistent way across multiple providers.

Each data model should inherit from a [standard data](core/openbb_core/provider/standard_models) model that is already defined inside the OpenBB Platform. All standard models are created and maintained by the OpenBB team.

Usage of these models will unlock a set of perks that are only available to standardized data, namely:

- Can query and output data in a standardized way.
- Can expect extensions that follow standardization to work out-of-the-box.
- Can expect transparently defined schemas for the data that is returned by the API.
- Can expect consistent data types and validation.
- Will work seamlessly with other providers that use the same standard model.

The standard models are defined under the `openbb_platform/core/openbb_core/provider/standard_models` directory.

They define the [`QueryParams`](core/openbb_core/provider/abstract/query_params.py) and [`Data`](core/openbb_core/provider/abstract/data.py) models, which are used to query and output data. They are pydantic and you can leverage all the pydantic features such as validators.

##### Standardization Caveats

The standardization framework is a very powerful tool, but it has some caveats that you should be aware of:

- We standardize fields that are shared between two or more providers. If there is a third provider that doesn't share the same fields, we will declare it as an optional field (`| None` with a `None` default).
- When mapping the column names from a provider-specific model to the standard model, the CamelCase to snake_case conversion is done automatically. If the column names are not the same, you'll need to manually map them. (e.g. `o` -> `open`)
- The standard models are created and maintained by the OpenBB team. If you want to add a new field to a standard model, you'll need to open a PR to the OpenBB Platform.

##### Standard QueryParams Example

```python
class EquityHistoricalQueryParams(QueryParams):
    """Equity Historical Price Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
```

The `QueryParams` is an abstract class that just tells us that we are dealing with query parameters.

The OpenBB Platform dynamically knows where the standard models begin in the inheritance tree, so you don't need to worry about it.

##### Standard Data Example

```python
class EquityHistoricalData(Data):
    """Equity Historical Price Data."""

    date: dateType | datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: float = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: float = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float | int | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    vwap: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
```

The `Data` class is an abstract class that tells us the expected output data. Here we can see a `vwap` field that is optional. This is because not all providers share this field while it is shared between two or more providers.

#### What is an extension?

An extension adds functionality to the OpenBB Platform. It can be a new data source, a new command, a new visualization, etc.

##### Types of extensions

We primarily have 3 types of extensions:

1. OpenBB Extensions - built and maintained by the OpenBB team (e.g. `openbb-equity`)
2. Community Extensions - built by anyone and primarily maintained by OpenBB (e.g. `openbb-tmx`)
3. Independent Extensions - built and maintained independently by anyone

If your extension is of high quality and you think that it would be a good community extension, you can open a PR to the OpenBB Platform repository and we'll review it.

We encourage independent extensions to be shared with the community by publishing them to PyPI.

## Dependency Management

### High-Level Overview

- **Core** (`openbb-core`): The runtime. It ships no data and no commands; it discovers installed extensions through entry points and assembles them into the Python interface and the REST API.
- **Routers** (`openbb_core_extension` entry point): Command namespaces such as `obb.equity` or `obb.economy`. Each router is its own package under `openbb_platform/extensions`.
- **Providers** (`openbb_provider_extension` entry point): Data sources that implement router commands. Each provider is its own package under `openbb_platform/providers`, and may also register its own router.
- **OBBject extensions** (`openbb_obbject_extension` entry point): Accessors added to every command result, such as `openbb-charting`. They live under `openbb_platform/obbject_extensions`.
- **Tooling**: `openbb-platform-api`, `openbb-mcp-server`, and `openbb-devtools`, under `openbb_platform/extensions`.

### Package Layout

Every package is a standalone project with its own `pyproject.toml` and `uv.lock`:

- `[build-system]` uses `hatchling`.
- `[project]` holds the metadata, `dependencies`, `optional-dependencies`, and entry points.
- `[dependency-groups]` holds the `dev` group used for tests and linting.
- `[tool.uv.sources]` points sibling OpenBB packages (`openbb-core`, `openbb-devtools`, ...) at their local paths as editable installs.

### Installation

For development setup, use the provided script to install every tracked, published package in editable mode, with all optional extras and `dev` dependency groups, then build the static `openbb` package. It requires [uv](https://docs.astral.sh/uv/).

- From the root of the repo call `python openbb_platform/dev_install.py --routers`
- Leave out `--routers` to skip the router extensions (`openbb-equity`, `openbb-economy`, `openbb-fixedincome`, and the rest); `openbb-news` is always installed.

> **Note**: If developing a single extension, you can install just that package with `uv pip install -e . --group dev` from its directory instead.

### Managing Dependencies with uv

Run these from the package directory, next to its `pyproject.toml`. Each one updates both `pyproject.toml` and `uv.lock`.

- **Add a Dependency**: `uv add <my-dependency>`
- **Add a Development Dependency**: `uv add --group dev <my-dependency>`
- **Remove a Dependency**: `uv remove <my-dependency>`
- **Update the Lock File**: `uv lock`
- **Upgrade a Dependency**: `uv lock --upgrade-package <my-dependency>`

## Developer Guidelines

### Expectations for Developers

1. Use Cases:
   - Ensure that your extensions or features align with the broader goals of the application.
   - Understand that the OpenBB Platform is designed to be foundational; build in a way that complements and doesn't conflict with its core functionalities.

2. Documentation:
   - Provide clear and comprehensive documentation for any new feature or extension you develop.

3. Code Quality:
   - Adhere to the coding standards and conventions of the OpenBB Platform.
   - Ensure your code is maintainable and well-organized.

4. Testing:
   - Thoroughly test any new feature or extension to ensure it works as expected.

5. Performance:
   - Ensure that your extensions or features do not adversely affect the performance of the OpenBB Platform.
   - Optimize for scalability, especially if you anticipate high demand for your feature.

6. Collaboration:
   - Engage with the OpenBB community to gather feedback on your developments.

### How to build OpenBB extensions?

We have a Cookiecutter template that will help you get started. It serves as a jumpstart for your extension development, so you can focus on the data and not on the boilerplate.

```bash
uvx openbb-cookiecutter
```

Please refer to the [Cookiecutter template](/cookiecutter/README.md) and follow the instructions there.

This document will walk you through the steps of adding a new extension to the OpenBB Platform.

The high level steps are:

- Generate the extension structure
- Install your dependencies
- Install your new package
- Use your extension (either from Python or the API interface)
- QA your extension
- Share your extension with the community

### Building Extensions: Best Practices

1. **Review Platform Dependencies**: Before adding any dependency, ensure it aligns with the Platform's existing dependencies.
2. **Use Loose Versioning**: If possible, specify a range to maintain compatibility. E.g., `>=1.4,<1.5`.
3. **Testing**: Test your extension with the Platform's core to avoid conflicts. Both unit and integration tests are recommended.
4. **Document Dependencies**: Keep `pyproject.toml` and `uv.lock` up to date, so the dependency record is clear.

### How to add a new data point?

In this section, we'll be adding a new data point to the OpenBB Platform. We will add a new provider with an existing [standard data](core/openbb_core/provider/standard_models) model.

#### Identify which type of data you want to add

In this example, we'll be adding OHLC stock data that is used by the `obb.equity.price.historical` command.

Note that, if no command exists for your data, we need to add one under the right router.
Each router is categorized under different extensions (equity, currency, crypto, etc.).

#### Check if the standard model exists

Given the fact that there's already an endpoint for OHLCV stock data, we can check if the standard exists.

In this case, it's `EquityHistorical` which can be found in `openbb_platform/core/openbb_core/provider/standard_models/equity_historical.py`.

If the standard model doesn't exist:

- you won't need to inherit from it in the next steps.
- all your provider query parameters will be under the `**kwargs` in the python interface.
- it might not work out-of-the box with other extensions that follow standardization e.g. the `charting` extension

##### Create Query Parameters model

Query Parameters are the parameters that are passed to the API endpoint in order to make the request.

For the `EquityHistorical` example, this would look like the following:

```python
class <ProviderName>EquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """<ProviderName> Equity Historical Query.

    Source: https://www.<provider_name>.co/documentation/
    """
```

Add any provider-specific query parameters as extra fields.

##### Create Data Output model

The data output is the data that is returned by the API endpoint.
For the `EquityHistorical` example, this would look like the following:

```python
class <ProviderName>EquityHistoricalData(EquityHistoricalData):
    """<ProviderName> Equity Historical Data.

    Source: https://www.<provider_name>.co/documentation/
    """
```

Add any provider-specific output fields as extra fields.

> Note that, since `EquityHistoricalData` inherits from pydantic's `BaseModel`, we can leverage validators to perform additional checks on the output model. A very good example of this, would be to transform a string date into a datetime object.

##### Build the Fetcher

The `Fetcher` class is responsible for making the request to the API endpoint and providing the output.

It will receive the query parameters, and it will return the output while leveraging the pydantic model schemas.

For the `EquityHistorical` example, this would look like the following:

```python
class <ProviderName>EquityHistoricalFetcher(
    Fetcher[
        <ProviderName>EquityHistoricalQueryParams,
        list[<ProviderName>EquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> <ProviderName>EquityHistoricalQueryParams:
        """Transform the query parameters."""
        return <ProviderName>EquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: <ProviderName>EquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the endpoint."""
        return await my_request(query, credentials, **kwargs)

    @staticmethod
    def transform_data(
        query: <ProviderName>EquityHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[<ProviderName>EquityHistoricalData]:
        """Transform the data to the standard format."""
        return [<ProviderName>EquityHistoricalData.model_validate(d) for d in data]
```

A `Fetcher` implements either the asynchronous `aextract_data` or the synchronous `extract_data`.

> Make sure that you're following the TET pattern when building a `Fetcher` - **Transform, Extract, Transform**. See more on this [here](#the-tet-pattern).

By default the credentials declared on each `Provider` are required. This means that before a query is executed, we check that all the credentials are present and if not an exception is raised. If you want to make credentials optional on a given fetcher, even though they are declared on the `Provider`, you can add `require_credentials=False` to the `Fetcher`
class. See the following example:

```python
class <ProviderName>EquityHistoricalFetcher(
    Fetcher[
        <ProviderName>EquityHistoricalQueryParams,
        list[<ProviderName>EquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data."""

    require_credentials = False
```

#### Make the provider visible

In order to make the new provider visible to the OpenBB Platform, define a `Provider` in the `__init__.py` file of the `providers/<provider_name>/openbb_<provider_name>/` folder.

```python
"""<Provider Name> Provider module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_<provider_name>.models.equity_historical import <ProviderName>EquityHistoricalFetcher

<provider_name>_provider = Provider(
    name="<provider_name>",
    website="<URL to the provider website>",
    description="Provider description goes here",
    credentials=["api_key"],
    fetcher_dict={
        "EquityHistorical": <ProviderName>EquityHistoricalFetcher,
    },
)
```

If the provider does not require any credentials, you can remove that parameter. On the other hand, if it requires more than one item to authenticate, add each of them to the `credentials` list. Users supply each one as `<provider_name>_<credential>`, e.g. `<provider_name>_api_key`.

Then register it as an entry point in the provider's `pyproject.toml`:

```toml
[project.entry-points."openbb_provider_extension"]
<provider_name> = "openbb_<provider_name>:<provider_name>_provider"
```

After running `uv pip install -e .` in `openbb_platform/providers/<provider_name>`, your provider is ready for use from both the Python interface and the API.

### How to add custom data sources?

You will get your data either from a CSV file, local database or from an API endpoint.

If you don't want or don't need to partake in the data standardization framework, you have the option to add all the logic straight inside the router file. This is usually the case when you are returning custom data from your local CSV file, or similar. Keep in mind that we also serve the REST API and that you shouldn't send non-serializable objects as a
response (e.g. a pandas dataframe).

Saying that, we highly recommend following the standardization framework, as it will make your life easier in the long run and unlock a set of features that are only available to standardized data.

When standardizing, all data is defined using two different pydantic models:

1. Define the [query parameters](core/openbb_core/provider/abstract/query_params.py) model.
2. Define the resulting [data schema](core/openbb_core/provider/abstract/data.py) model.

> The models can be entirely custom, or inherit from the OpenBB standardized models.
> They enforce a safe and consistent data structure, validation and type checking.

We call this the ***Know-Your-Data*** principle.

After you've defined both models, you'll need to define a `Fetcher` class which contains three methods:

1. `transform_query` - transforms the query parameters to the format of the API endpoint.
2. `aextract_data` or `extract_data` - makes the request to the API endpoint and returns the raw data.
3. `transform_data` - transforms the raw data into the defined data model.

> Note that the `Fetcher` should inherit from the [`Fetcher`](core/openbb_core/provider/abstract/fetcher.py) class, which is a generic class that receives the query parameters and the data model as type parameters.

After finalizing your models, you need to make them visible to the OpenBB Platform. This is done by adding the `Fetcher` to the `fetcher_dict` of the [`Provider`](core/openbb_core/provider/abstract/provider.py) defined in your package's `__init__.py`, and registering that `Provider` as an `openbb_provider_extension` entry point.

Any command that uses the `Fetcher` class you've just defined will call the `transform_query`, `aextract_data` (or `extract_data`) and `transform_data` methods under the hood in order to get the data and output it to the end user.

If you're not sure what's a command and why is it even using the `Fetcher` class, follow along!

#### OpenBB Platform commands

The OpenBB Platform will enable you to query and output your data in a very simple way.

> Any Platform endpoint will be available both from a Python interface and the API.

The command definition on the Platform follows [FastAPI](https://fastapi.tiangolo.com/) conventions, meaning that you'll be creating **endpoints**.

The Cookiecutter template generates for you a router file with a set of examples that you can follow, namely:

- Perform a simple `GET` and `POST` request - without worrying on any custom data definition.
- Using a custom data definition so you get your data the exact way you want it.

You can expect the following endpoint structure when using a `Fetcher` to serve the data:

```python
@router.command(
    model="Example",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "<provider_name>"})],
)
async def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))
```

Let's break it down:

- `@router.command(...)` - this tells the OpenBB Platform that this is a command.
- `model="Example"` - this is the name of the `Fetcher` dictionary key that you've defined in the `fetcher_dict` of your `Provider`.
- `examples=[...]` - example parameters, used in the generated docstrings and to build the integration tests.
- `cc: CommandContext` - this contains a set of user and system settings that is useful during the execution of the command - eg. api keys.
- `provider_choices: ProviderChoices` - all the providers that implement the `Example` `Fetcher`.
- `standard_params: StandardParams` - standardized parameters that are common to all providers that implement the `Example` `Fetcher`.
- `extra_params: ExtraParams` - it contains the provider specific arguments that are not standardized.

You only need to change the `model` parameter to the name of the `Fetcher` dictionary key and everything else will be handled by the OpenBB Platform.

The router itself is registered as an entry point in the extension's `pyproject.toml`:

```toml
[project.entry-points."openbb_core_extension"]
<router_name> = "openbb_<router_name>.<router_name>_router:router"
```

### Architectural considerations

#### Important classes

```python
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.abstract.query_params import QueryParams
```

#### The TET pattern

The TET pattern is a pattern that we use to build the `Fetcher` classes. It stands for **Transform, Extract, Transform**.
As the OpenBB Platform has its own standardization framework and the data fetcher are a very important part of it, we need to ensure that the data is transformed and extracted in a consistent way, to help us do that, we came up with the **TET** pattern, which helps us build and ship faster as we have a clear structure on how to build the `Fetcher` classes.

1. Transform - `transform_query(params: dict[str, Any])`: transforms the query parameters. Given a `params` dictionary this method should return the transformed query parameters as a [`QueryParams`](core/openbb_core/provider/abstract/query_params.py) child so that we can leverage the pydantic model schemas and validation into the next step. This might also
   be the place do perform some transformations on any given parameter, i.e., if you want to transform an empty date into a `datetime.now().date()`.
2. Extract - `aextract_data(query: ExampleQueryParams, credentials: dict[str, str] | None, **kwargs: Any)` (or the synchronous `extract_data`): makes the request to the API endpoint and returns the raw data. Given the transformed query parameters, the credentials and any other extra arguments, this method should return the raw data.
3. Transform - `transform_data(query: ExampleQueryParams, data: Any, **kwargs: Any) -> list[ExampleData]`: transforms the raw data into the defined data model. Given the transformed query parameters (might be useful for some filtering), the raw data and any other extra arguments, this method should return the transformed data as a list of
   [`Data`](core/openbb_core/provider/abstract/data.py) children.

#### Errors

To ensure a consistent error handling behavior our API relies on the convention below, implemented in [`exception_handlers.py`](core/openbb_core/api/exception_handlers.py).

| Status code | Exception | Detail | Description |
| -------- | ------- | ------- | ------- |
| 204 | `EmptyDataError` | No content. | Raise when the query succeeded but returned no data. |
| 400 | `OpenBBError` or a child of `OpenBBError` | Custom message. | Use this to explicitly raise custom exceptions. |
| 422 | `ValidationError`, `ValueError` | `Pydantic` errors dict message. | Raised to inform the user about query validation errors. ValidationErrors outside of the query are treated with status code 500. |
| 502 | `UnauthorizedError` | Custom message. | Raise when the upstream provider rejects the credentials. |
| 500 | Any exception not covered above, eg `ZeroDivisionError` | Unexpected error. | Unexpected exceptions, most likely a bug. |

`OpenBBError` lives in `openbb_core.app.model.abstract.error`; `EmptyDataError` and `UnauthorizedError` live in `openbb_core.provider.utils.errors`.

#### Data processing commands

The data processing commands are commands that are used to process the data that may or may not come from the OpenBB Platform.
In order to create a data processing framework general enough to be used by any extension, we've created a special abstract class called [`Data`](core/openbb_core/provider/abstract/data.py) which **all** standardized (and consequently its child classes) will inherit from.

Why is this important?
So that we can ensure that all `OBBject.results` will share a common ground on which we can apply out-of-the-box data processing commands, such as the `technical`, `quantitative` or `econometrics` routers.

But what's really the `Data` class?
It's a pydantic model that inherits from the `BaseModel` and can contain any given number of extra fields. In practice, it looks as follows:

```python
>>> res = obb.equity.price.historical("AAPL", provider="cboe")
>>> type(res.results[0]).__name__
'CboeEquityHistoricalData'
```

> The `CboeEquityHistoricalData` class is a child class of the `Data` class.

Note how we've indexed to get only the first element of the `results` list (which represents a single row, if we want to think about it as a tabular output). This simply means that we are getting a `list` of `CboeEquityHistoricalData` from the `obb.equity.price.historical` command. Or, we can also say that that's equivalent to `list[Data]`!

This is very powerful, as we can now apply any data processing command to the `results` list, without worrying about the underlying data structure.
That's why, on data processing commands (such as the `technical` router) we will find the following in the command's parameters:

```python
class EmaQueryParams(QueryParams):
    """Exponential Moving Average query."""

    data: list[Data] = Field(description="Price series.")
    target: str = "close"
    index: str = "date"
    length: PositiveInt = 50
    offset: int = 0
```

Does that mean that I can only use the data processing commands if I instantiate a class that inherits from `Data`?
Not at all! Consider the following example:

```python
>>> from openbb_core.provider.abstract.data import Data
>>> my_data_item_1 = {"open": 1, "high": 2, "low": 3, "close": 4, "volume": 5, "date": "2020-01-01"}
>>> Data.model_validate(my_data_item_1)
Data(open=1, high=2, low=3, close=4, volume=5, date=2020-01-01)
```

This means that the `Data` class is clever enough to understand that you are passing a dictionary and it will try to validate it for you.
In other words, if you're using data that doesn't come from the OpenBB Platform, you only need to ensure it's parsable by the `Data` class and you'll be able to use the data processing commands.
For example, imagine you have a dataframe that you want to use with the `technical` router. You can do the following:

```python
>>> res = obb.equity.price.historical("AAPL", provider="cboe")
>>> df = res.to_dataframe()
>>> obb.technical.ema(data=df, length=50)
```

> Note that for this example we've used the `OBBject.to_dataframe()` method to have an example dataframe, but it could be any other dataframe that you have.

##### Python Interface

When using the OpenBB Platform on a Python Interface, docstrings and type hints are your best friends as they provide plenty of context on how to use the commands.
Looking at the generated `obb.technical.ema` signature:

```python
def ema(
    self,
    data: list | dict | DataFrame | list[DataFrame] | Series | list[Series] | ndarray | Data | list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
    chart: bool = False,
) -> OBBject:
    ...
```

We can easily deduce that the `ema` command accepts records, `Data`, pandas objects, or numpy arrays. The `chart` parameter appears when `openbb-charting` is installed.

##### API Interface

When using the OpenBB Platform on a API Interface, the types are a bit more limited than on the Python one, as, for example, we can't use `pandas.DataFrame` as a type. However the same principles apply for what `Data` means, i.e., any given data processing command, which are characterized as POST endpoints on the API, will accept data as a list of records on
the **request body**, i.e.:

```json
[
    {
        "date": "2023-11-03",
        "open": 80,
        "high": 80.69,
        "low": 77.37,
        "close": 77.62,
        "volume": 2487300
    }
]
```

## Contributor Guidelines

The Contributor Guidelines are intended to be a continuation of the [Developer Guidelines](#developer-guidelines). They are not a replacement, but rather an expansion, focusing specifically on those who seek to directly enhance the OpenBB Platform's codebase. It's crucial for Contributors to be familiar with both sets of guidelines to ensure a harmonious and
productive engagement with the OpenBB Platform.

There are many ways to contribute to the OpenBB Platform. You can add a [new data point](#how-to-add-a-new-data-point), add a [new command](#openbb-platform-commands), add a [new visualization](/openbb_platform/obbject_extensions/charting/README.md), add a [new extension](#how-to-build-openbb-extensions), fix a bug, improve or create documentation, etc.

### Expectations for Contributors

1. Use Cases:
   - Ensure that your contributions directly enhance the OpenBB Platform's functionality or extension ecosystem.

2. Documentation:
   - All code contributions should come with relevant documentation, including the purpose of the contribution, how it works, and any changes it makes to existing functionalities.
   - Update any existing documentation if your contribution alters the behavior of the OpenBB Platform.

3. Code Quality:
   - Your code should adhere strictly to the OpenBB Platform's coding standards and conventions.
   - Ensure clarity, maintainability, and proper organization in your code.

4. Testing:
   - All contributions must be thoroughly tested to avoid introducing bugs to the OpenBB Platform.
   - Contributions should include relevant automated tests (unit and integration), and any new feature should come with its test cases.

5. Performance:
   - Your contributions should be optimized for performance and should not degrade the overall efficiency of the OpenBB Platform.
   - Address any potential bottlenecks and ensure scalability.

6. Collaboration:
   - Engage actively with the OpenBB development team to ensure that your contributions align with the platform's roadmap and standards.
   - Welcome feedback and be open to making revisions based on reviews and suggestions from the community.

### Quality Assurance

We are strong believers in the Quality Assurance (QA) process and we want to make sure that all the extensions that are added to the OpenBB Platform are of high quality. To ensure this, we have a set of QA tools that you can use to test your extension.

Primarily, we have tools that semi-automate the creation of unit and integration tests.

> The QA tools are still in development and we are constantly improving them.

#### Linting and type checking

Each package is linted and type checked from its own directory, the same way its CI workflow runs:

```bash
cd openbb_platform/providers/<provider_name>
ruff format --check .
ruff check .
ty check openbb_<provider_name>
```

The repository's pre-commit hooks run the same checks on staged files:

```bash
pre-commit install
```

#### Unit tests

Each `Fetcher` comes equipped with a `test` method that will ensure that it is implemented correctly and that it is returning the expected data. It also ensures that all types are correct and that the data is valid.

To create unit tests for your Fetchers, you can run the following command:

```bash
python openbb_platform/providers/tests/utils/unit_tests_generator.py
```

> Note that you should be running this file from the root of the repository.
> Note that the `tests` folder must exist in order to generate the tests.

The automatic unit test generation will add unit tests for all the fetchers available in a given provider.

To record the HTTP cassettes for the unit tests, you can run the following command:

```bash
pytest <path_to_the_unit_test_file> --record=all
```

> Note that sometimes manual intervention is needed. For example, adjusting out-of-top level imports or adding specific arguments for a given fetcher.

Run a package's unit tests from its directory:

```bash
cd openbb_platform/providers/<provider_name>
pytest tests
```

#### Integration tests

The integration tests are a bit more complex than the unit tests, as we want to test both the Python interface and the API interface. They live in the `integration` folder of each router extension, and generating them requires the routers to be installed (`python openbb_platform/dev_install.py --routers`). We have two scripts that will help you generate them.

To generate the integration tests for the Python interface, you can run the following command:

```bash
python openbb_platform/extensions/tests/utils/integration_tests_generator.py
```

To generate the integration tests for the API interface, you can run the following command:

```bash
python openbb_platform/extensions/tests/utils/integration_tests_api_generator.py
```

When testing the API interface, you'll need to run the OpenBB Platform locally on port 8000 before running the tests. To do so, you can run the following command:

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

These automated tests are a great way to reduce the amount of code you need to write, but they are not a replacement for manual testing and might require tweaking. That's why we have unit tests that test the generated integration tests to ensure they cover all providers and parameters.

Run a router's integration tests from its directory:

```bash
cd openbb_platform/extensions/<router_name>
pytest integration -m integration
```

#### Import time

We aim to have a short import time for the package. To measure that we use `tuna`.

- <https://pypi.org/project/tuna/>

To visualize the import time breakdown by module and find potential bottlenecks, run the
following commands:

```bash
pip install tuna
python -X importtime -c "import openbb" 2> import.log
tuna import.log
```

### Sharing your extension

We encourage you to share your extension with the community. You can do that by publishing it to PyPI.

#### Publish your extension to PyPI

To publish your extension to PyPI, you'll need to have a PyPI account and a PyPI API token from <https://pypi.org/manage/account/token/>.

##### Build

`cd` into the directory where your extension `pyproject.toml` lives, make sure that `pyproject.toml` specifies the version you want to release, and run:

```bash
uv build --no-sources
```

`--no-sources` builds against the published versions of your OpenBB dependencies instead of the local `[tool.uv.sources]` paths.

This will create a `dist` folder in the directory, which will contain the `.whl` and `.tar.gz` files matching the version to release.

If you want to test your package locally you can do it with:

```bash
pip install dist/openbb_[FILE_NAME].whl
```

##### Publish

To publish your package to PyPI run:

```bash
uv publish --token pypi-YYYYYYYY
```

Now, you can pip install your package from PyPI with:

```bash
pip install openbb-some_ext
```

### Manage extensions

To install an extension hosted on PyPI, use the `pip install <extension>` command.

To install an extension that is developed locally, ensure that it contains a `pyproject.toml` file and then use the `pip install <extension>` command.

> To install the extension in editable mode using pip, add the `-e` argument.

Alternatively, `dev_install.py` installs every package whose `pyproject.toml` is tracked by git under `openbb_platform/core`, `openbb_platform/extensions/*`, `openbb_platform/obbject_extensions/*`, `openbb_platform/providers/*`, or `cli`. Once the extension's `pyproject.toml` is committed there, `python openbb_platform/dev_install.py` installs it (add `--routers` for a router extension).

After installing or removing an extension, run `openbb-build` to regenerate the `openbb` package.

#### Add an extension as a dependency

To add the `openbb-technical` extension as a dependency, add it to the `dependencies` of the `[project]` table in your `pyproject.toml`:

```toml
[project]
dependencies = [
    "openbb-technical>=2.0.0",
]
```

Or run `uv add openbb-technical` from the package directory. Then you can follow the same process as above to install the extension.

### Write code and commit

#### How to create a PR?

To create a PR to the OpenBB Platform, you'll need to fork the repository and create a new branch.

1. Create your Feature Branch, e.g. `git checkout -b feature/AmazingFeature`
2. Check the files you have touched using `git status`
3. Stage the files you want to commit, e.g.
   `git add openbb_platform/core/openbb_core/app/constants.py`.
   Note: **DON'T** add any files with personal information.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
   solves an issue raised by a user, you may specify such an issue by adding #ISSUE_NUMBER to the commit message, so that
   these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
   to go back to step 3 to add these.

##### Branch Naming Conventions

The accepted branch naming conventions are:

- `feature/feature-name`
- `hotfix/hotfix-name`

These branches can only have PRs pointing to the `develop` branch.
