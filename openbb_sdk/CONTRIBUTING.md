# CONTRIBUTING

- [CONTRIBUTING](#contributing)
  - [Get started contributing with a template](#get-started-contributing-with-a-template)
    - [Cookiecuter, a closer look](#cookiecuter-a-closer-look)
      - [Get your data](#get-your-data)
      - [SDK commands: query and output your data](#sdk-commands-query-and-output-your-data)
  - [Adding a new data point](#adding-a-new-data-point)
    - [Identify which type of data you want to add](#identify-which-type-of-data-you-want-to-add)
    - [Check which is the Model in place](#check-which-is-the-model-in-place)
    - [Identify if it's an existing provider](#identify-if-its-an-existing-provider)
    - [Refer to the API documentation and start developing](#refer-to-the-api-documentation-and-start-developing)
      - [Data characterization](#data-characterization)
        - [Query parameters](#query-parameters)
        - [Data output](#data-output)
      - [Build the Fetcher](#build-the-fetcher)
    - [Make the new provider visible to the SDK](#make-the-new-provider-visible-to-the-sdk)

## Get started contributing with a template

In order to get started contributing faster, the OpenBB team setup a Cookiecutter template that will help you get started with the boilerplate code.
Please refer to the [Cookiecutter template](https://github.com/OpenBB-finance/openbb-cookiecutter) and follow the instructions there.

This will walk you through the process of adding a new custom extension to the SDK. The high level steps are:

- Generating the project structure
- Install your dependencies
- Install your new package
- Use your extension (either from Python or the API)

### Cookiecuter, a closer look

The Cookiecutter template will generate a set of files in which we can find a detailed set of instructions and explanations.

> Note that the generated template code will vary according to a set of questions during template generation.
> Also, the code is functional, so you can just run it and start playing with it.

#### Get your data

Either from a CSV file or from an API endpoint, you'll need to get your data.
This can be done through the following way:

All the data you'll be getting should be model defined, i.e., you'll be defining two different data models:

1. Define the request/query parameters model.
2. Define the resulting data schema model.

> Models are [pydantic](https://docs.pydantic.dev/latest/) models that can be entirely custom, or inherit from the OpenBB standardized models.
> Those enforce a safe and consistent data structure, validation and type checking.

After you've defined both models, you'll need to define a fetcher.
The fetcher should contain three methods:

1. `transform_query`: transform the query parameters into the format that the API endpoint expects.
2. `extract_data`: make the request to the API endpoint and return the raw data.
3. `transform_data`: transform the raw data into the standardized data model.

> Note that the fetcher should inherit from the `Fetcher` class, which is a generic class that receives the query parameters and the data model as type parameters.

Afterwards, and considering your extension might need to be reinstalled if any changes are made, you'll need to make it visible to the SDK.
This is done by adding the fetcher to the `__init__.py` file of the `<your_package_name>/<your_module_name>` folder.

Any command using the fetcher you've just defined, will be calling the `transform_query`, `extract_data` and `transform_data` methods under the hood in order to get the data and output it do the end user.

If you're not sure what's a command and why is it even using the fetcher, follow along!

#### SDK commands: query and output your data

The SDK will enable you to query and output your data in a very simple way - with the caveat that you'll need to have your data model defined before doing so.

> Any SDK endpoint will be available both from a Python interface and the API.

The command definition on the SDK follows [FastAPI](https://fastapi.tiangolo.com/) conventions, meaning that you'll be defining "endpoints" pretty much the same way you would do it with FastAPI.

The Cookiecutter template generates for you a `router.py` file with a set of examples that you can follow, namely:

- Perform a simple `GET` and `POST` request - without worrying on any custom data definition.
- Using a custom data definition so you get your own data.

In the later, you can expect something like the following:

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

- `@router.command(model="Example")`: this is a decorator that will tell the SDK that this is a command that can be called from the API.
- `model="Example"`: this is the name of the data model that will be used to validate the data.
- `cc: CommandContext`: this is a parameter that will be passed to the command and that will contain the context of the command - this contains a set of user and system settings that might (or not) be useful during the execution of the command - eg. api keys.
- `provider_choices: ProviderChoices`: all the providers that implement the `Example` fetcher.
- `standard_params: StandardParams`: standardized parameters that are common to all providers that implement the `Example` fetcher.
- `extra_params: ExtraParams`: this is a parameter that will be passed to the command and that will contain the provider specific arguments - take into consideration that a single SDK command can consume any amount of provider you wish.

## Adding a new data point

### Identify which type of data you want to add

In this example, we'll be adding OHLC stock data.
This corresponds to a very well known endpoint, `stocks/load`.

Note that, if no endpoint existed yet, we'd need to add it under the right asset type.
Each asset type is organized under a different extension (stocks, forex, crypto, etc.).

### Check which is the Model in place

Given the fact that there's already an endpoint for OHLC stock data, we can check which is the model in place. In this case, it's `StockEOD`.

### Identify if it's an existing provider

If it's a new provider, you'll need to add some boilerplate code.
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