---
title: Add a Data Point
sidebar_position: 3
description: This guide provides detailed instructions on how to add a new data point to the OpenBB Platform. It covers the process of creating a new provider, defining query parameters and data output models, and building a Fetcher class.
keywords:
- OpenBB Platform
- Data point addition
- Provider creation
- Query parameters
- Data output models
- Fetcher class
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Add a Data Point - Developer Guidelines - Development | OpenBB Platform Docs" />

In this section, we'll be adding a new data point to the OpenBB Platform. We will add a new provider with an existing [standard data](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_platform/platform/provider/openbb_provider/standard_models) model.

## Identify which type of data you want to add

In this example, we'll be adding OHLC stock data that is used by the `obb.equity.price.historical` command.

Note that, if no command exists for your data, we need to add one under the right router.
Each router is categorized under different extensions (stocks, currency, crypto, etc.).

## Check if the standard model exists

Given the fact that there's already an endpoint for OHLCV stock data, we can check if the standard exists.

In this case, it's `EquityHistorical` which can be found in `/OpenBBTerminal/openbb_platform/platform/core/provider/openbb_provider/standard_models/equity_historical`.

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

The data output is the data that is returned by the API endpoint.
For the `StockHistorical` example, this would look like the following:

```python

class <ProviderName>EquityHistoricalData(EquityHistoricalData):
    """<ProviderName> Equity Historical Data.

    Source: https://www.<provider_name>.co/documentation/
    """

    # provider specific data output fields if any

```

> Note that, since `EquityHistoricalData` inherits from pydantic's `BaseModel`, we can leverage validators to perform additional checks on the output model. A very good example of this, would be to transform a string date into a datetime object.

### Build the Fetcher

The `Fetcher` class is responsible for making the request to the API endpoint and providing the output.

It will receive the Query Parameters, and it will return the output while leveraging the pydantic model schemas.

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

> Make sure that you're following the TET pattern when building a `Fetcher` - **Transform, Extract, Transform**. See more on this [here](/platform/contributing/developer-guidelines/architectural_considerations#the-tet-pattern).

## Make the provider visible

In order to make the new provider visible to the OpenBB Platform, you'll need to add it to the `__init__.py` file of the `providers/<provider_name>/openbb_<provider_name>/` folder.

```python
"""<Provider Name> Provider module."""
from openbb_provider.abstract.provider import Provider

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

If the provider does not require any credentials, you can remove that parameter. On the other hand, if it requires more than 2 items to authenticate, you can add a list of all the required items to the `credentials` list.

After running `pip install .` on `openbb_platform/providers/<provider_name>` your provider should be ready for usage, both from the Python interface and the API.
