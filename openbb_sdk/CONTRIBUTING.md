
# CONTIRBUTING

## Table of Contents

- [CONTIRBUTING](#contirbuting)
  - [Table of Contents](#table-of-contents)
  - [Adding a new data point](#adding-a-new-data-point)
    - [Identify which type of data you want to add](#identify-which-type-of-data-you-want-to-add)
    - [Check if the standard model exists](#check-if-the-standard-model-exists)
    - [Identify if it's an existing provider](#identify-if-its-an-existing-provider)
    - [Refer to the API documentation and start developing](#refer-to-the-api-documentation-and-start-developing)
      - [Data characterization](#data-characterization)
      - [How to use the standardization framework?](#how-to-use-the-standardization-framework)
        - [Query parameters](#query-parameters)
        - [Data output](#data-output)
      - [Build the Fetcher](#build-the-fetcher)
    - [Make the new provider visible to the SDK](#make-the-new-provider-visible-to-the-sdk)

## Adding a new data point

### Identify which type of data you want to add

In this example, we'll be adding OHLC stock data.
This corresponds to a very well known endpoint, `stocks/load`.

Note that, if no endpoint existed yet, we'd need to add it under the right asset type.
Each asset type is organized under a different extension (stocks, forex, crypto, etc.).

### Check if the standard model exists

Given the fact that there's already an endpoint for OHLCV stock data, we can check if the standard exists.
In this case, it's `StockEOD` which can be found inside the `./sdk/core/provider/openbb_provider/standard_models/` directory.

If the standard model doesn't exist:

- you won't need to inherit from it in the next steps
- all your provider-specific query parameters will be under the `kwargs` in the python interface
- it might not work out-of-the box with other extensions such as the `charting` extension

### Identify if it's an existing provider

TODO: MOVE THIS AND CHANGE SO IT USES THE COOKIECUTTER
If it's a new provider, you'll need to add boilerplate code.
You can easily do this by inspecting how the other providers are implemented.
The folder structure is the following:

```bash

openbb_sdk
└── providers
    └── <provider_name>
        ├── openbb_<provider_name>.py
        |       ├── __init__.py
                ├── models
                    ├── __init__.py
                    |── <model_name>.py
        ├── pyproject.toml
        └── README.md
        └── tests

```

For the example above, and being the case that we'll be adding an extension to the `StockEOD` data model, our `<model_name>.py` file will be called `stock_eod.py`.

### Refer to the API documentation and start developing

#### Data characterization

All data models should have a standard model from which they inherit.
And then each provider should have its own additional parameters, both for the query and the output.

#### How to use the standardization framework?

##### Query parameters

Query parameters are the parameters that are passed to the API endpoint in order to make the request.
For the `StockEOD` example, this would look like the following:

```python

class <ProviderName>StockEODQueryParams(StockEODQueryParams):
    """<ProviderName> Stock End of Day Query.

    Source: https://www.<provider_name>.co/documentation/
    """

    # provider specific query parameters

```

> Note that, since `StockEODQueryParams` inherits from pydantic's `BaseModel`, so we can leverage validators to perform additional checks on the query parameters.

##### Data output

The data output is the data that is returned by the API endpoint.
For the `StockEOD` example, this would look like the following:

```python

class <ProviderName>StockEODData(StockEODData):
    """<ProviderName> Stock End of Day Data.

    Source: https://www.<provider_name>.co/documentation/
    """

    # provider specific data output

```

> Note that, since `StockEODData` inherits from pydantic's `BaseModel`, so we can leverage validators to perform additional checks on the output model. A very good example of this, would be to transform a string date into a datetime object.

#### Build the Fetcher

The fetcher is the class that will be in charge of making the request to the API endpoint.
It will receive the query parameters, and it will return the data output while leveraging the data model, both for the query parameters and the data output.

For the `StockEOD` example, this would look like the following:

```python

class <ProviderName>EODFetcher(
    Fetcher[
        <ProviderName>EODQueryParams,
        List[<ProviderName>EODData],
    ]
):
    """Transform the query, extract and transform the data."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> <ProviderName>EODQueryParams:
        """Transform the query parameters."""

        return <ProviderName>EODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: <ProviderName>EODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the endpoint."""

        obtained_data = my_request(query, credentials, **kwargs)

        return obtained_data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[<ProviderName>EODData]:
        """Transform the data to the standard format."""

        return [<ProviderName>EODData.parse_obj(**d) for d in data]

```

> Make sure that you're following the TET pattern when building a fetcher: Transform, Extract, Transform.

### Make the new provider visible to the SDK

In order to make the new provider visible to the SDK, you'll need to add it to the `__init__.py` file of the `providers/<provider_name>/openbb_<provider_name>/` folder.

```python

"""Alpha Vantage Provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_<provider_name>.models.stock_eod import <ProviderName>StockEODFetcher

<provider_name>_provider = Provider(
    name="<provider_name>",
    website="https://www.<providerName>.co/documentation/",
    description="Provider description goes here",
    required_credentials=["api_key"],
    fetcher_dict={
        "StockEOD": <ProviderName>StockEODFetcher,
    },
)

```

After running `pip install .` on `openbb_sdk/providers/<provider_name>` your provider should be ready for usage, both from a Python interface or the API.
