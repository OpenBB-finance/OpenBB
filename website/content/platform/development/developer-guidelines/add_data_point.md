---
title: Integrating Data Sources and Points
sidebar_position: 3
description: This comprehensive guide is designed to assist developers in integrating custom data sources and adding new data points to the OpenBB Platform. It covers the creation of custom extensions, standardization of data, definition of models, and the construction of a Fetcher class. This document is essential for developers looking to enhance the platform with new data capabilities.
keywords:
- OpenBB Platform
- Data point addition
- Provider creation
- Query parameters
- Data output models
- Fetcher class
- OpenBB custom data sources
- Data standardization
- Pydantic models
- OpenBB extensions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Integrating Data Sources and Points - Developer Guidelines - Development | OpenBB Platform Docs" />

In this section, we'll be adding a new data point to the OpenBB Platform. We will add a new provider with an existing model, imported from: [openbb_core.provider.standard_models](/platform/data_models).

## Identify your data

You will get your data either from a CSV file, local database or from an API endpoint.

:::note
If you don't want or don't need to partake in the data standardization framework, you have the option to add all the logic straight inside the router file. This is usually the case when you are returning custom data from your local CSV file, or similar. Keep in mind that we also serve the REST API and that you shouldn't send non-serializable objects as a response (e.g. a pandas dataframe).
:::

We highly recommend following the standardization framework, as it will make your life easier in the long run and unlock a set of features that are only available to standardized data.

When standardizing, all data is defined using two different pydantic models:

1. Define the [query parameters](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/provider/openbb_core/provider/abstract/query_params.py) model.
2. Define the resulting [data schema](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/provider/openbb_core/provider/abstract/data.py) model.

> The models can be entirely custom, or inherit from the OpenBB standardized models.
> They enforce a safe and consistent data structure, validation and type checking.

We call this the ***Know-Your-Data*** principle.

In the following example, we'll be adding historical, end-of-day OHLC (open, high, low, close) equity data that is used by the `obb.equity.price.historical` command.

Note that if no command exists for your data, we need to add one under the right router.

Each router is categorized under the relevant extension (equity, currency, crypto, etc.).

## Check if the standard model exists

Given the fact that there's already an endpoint for historical equity data, we can check for the existing standard model.

In this case, it's `EquityHistorical` which can be found in the list of data models [here](/platform/data_models).

If the standard model doesn't exist:

- you won't need to inherit from it in the next steps.
- all your provider query parameters will be under the `**kwargs` in the python interface.
- it might not work out-of-the box with other extensions that follow standardization e.g. the `charting` extension

### Create Query Parameters model

Query Parameters are the parameters that are passed to the API endpoint in order to make the request.

For the `EquityHistorical` example, this would look like the following:

```python

class <ProviderName>EquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """<ProviderName> Equity Historical Query.

    Source: https://www.<provider_name>.co/documentation/
    """

    # provider specific query parameters if any

```

### Create Data Output model

The data output model is a data class containing Fields mapping the response of the API.

For the `StockHistorical` example, this would look like the following:

```python

class <ProviderName>EquityHistoricalData(EquityHistoricalData):
    """<ProviderName> Equity Historical Data.

    Source: https://www.<provider_name>.co/documentation/
    """

    # provider specific data output fields if any

```

> Note that, since `EquityHistoricalData` inherits from pydantic's `BaseModel`, we can leverage validators to perform additional checks on the output model. A very good example of this, would be to transform a string date into a datetime object.

### Optional vs Required fields when creating models

When creating a new model, you need to decide whether a field is required or not.

This is done by using `typing`'s `Optional` when defining the field type.

In the context of the **Standard Models**:

- Required: all the providers use that field (either to query or to present data).
- Optional: at least two providers use that field (either to query or to present data).

In the context of the **Provider Models**:

- Required: the provider uses that field:
  - Needs the field to query the API.
  - The data presented by the provider contains that field.
- Optional: the may or may not use that field:
  - If the user uses that field, the provider will also use it to query the API.
  - The data presented by the provider may or may not contain that field.

> Learn more about Pydantic's fields [here](https://docs.pydantic.dev/latest/concepts/fields/).

### Build the Fetcher

The `Fetcher` class is responsible for processing the Query and turning that into an API request and finally returning the data model. Each fetcher contains three methods that are implemented by its abstract definition:

- `transform_query`
  - Convert a standard query into a provider-specific query
- `extract_data`
  - Get the data from the API endpoint
- `transform_data`
  - Convert the API response data into a list of standard data models.

> Read more on the `TET` pattern [here](/platform/development/developer-guidelines/architectural_considerations#the-tet-pattern).

:::note
Note that the `Fetcher` should inherit from the [`Fetcher`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/provider/openbb_core/provider/abstract/fetcher.py) class, which is a generic class that receives the query parameters and the data model as type parameters.
:::

For the `EquityHistorical` example, this would look like the following:

```python
class <ProviderName>EquityHistoricalFetcher(
    Fetcher[
        <ProviderName>EquityHistoricalQueryParams,
        List[<ProviderName>EquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> <ProviderName>EquityHistoricalQueryParams:
        """Transform the query parameters."""

        return <ProviderName>EquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: <ProviderName>EquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the endpoint."""

        obtained_data = my_request(query, credentials, **kwargs)

        return obtained_data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[<ProviderName>EquityHistoricalData]:
        """Transform the data to the standard format."""

        return [<ProviderName>EquityHistoricalData.model_validate(d) for d in data]
```

## Make the provider visible

After finalizing your models, you need to make them visible to the Openbb Platform.
This is done by adding the `Fetcher` to the `__init__.py` file of the `<your_package_name>/<your_module_name>` folder as part of the [`Provider`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/provider/openbb_core/provider/abstract/provider.py).

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

Any command, that uses the `Fetcher` class you've just defined, will be calling the `transform_query`, `extract_data` and `transform_data` methods under the hood in order to get the data and output it do the end user.

If the provider does not require any credentials, you can remove that parameter. On the other hand, if it requires more than 2 items to authenticate, you can add a list of all the required items to the `credentials` list.

:::info
After running `pip install .` on `openbb_platform/providers/<provider_name>` your provider should be ready for usage, both from the Python interface and the API.
:::

If you're not sure what's a command and why is it even using the `Fetcher` class, follow along!

## OpenBB Platform Commands

The OpenBB Platform will enable you to query and output your data in a very simple way.

> Any Platform endpoint will be available both from a Python interface and the API.

The command definition on the Platform follows [FastAPI](https://fastapi.tiangolo.com/) conventions, meaning that you'll be creating **endpoints**.

The [Cookiecutter template](https://github.com/OpenBB-finance/openbb-cookiecutter) generates for you a `router.py` file with a set of examples that you can follow, namely:

- Perform a simple `GET` and `POST` request - without worrying on any custom data definition.
- Using a custom data definition so you get your data the exact way you want it.

You can expect the following endpoint structure when using a `Fetcher` to serve the data:

```python
@router.command(model="Example")
def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Example Data."""
    return OBBject(results=Query(**locals()).execute())
```

Let's break it down:

- `@router.command(...)` - this tells the OpenBB Platform that this is a command.
- `model="Example"` - this is the name of the `Fetcher` dictionary key that you've defined in the `__init__.py` file of the `<your_package_name>/<your_module_name>` folder.
- `cc: CommandContext` - this contains a set of user and system settings that is useful during the execution of the command - eg. api keys.
- `provider_choices: ProviderChoices` - all the providers that implement the `Example` `Fetcher`.
- `standard_params: StandardParams` - standardized parameters that are common to all providers that implement the `Example` `Fetcher`.
- `extra_params: ExtraParams` - it contains the provider specific arguments that are not standardized.

You only need to change the `model` parameter to the name of the `Fetcher` dictionary key and everything else will be handled by the OpenBB Platform.
