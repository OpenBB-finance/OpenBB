---
title: Architectural Considerations
sidebar_position: 6
description: This guide provides insights into the architectural considerations of the OpenBB Platform. It covers the key classes, import statements, and the TET pattern used in building the Fetcher classes.
keywords:
- OpenBB Platform Architecture
- Key Classes
- Import Statements
- TET Pattern
- Fetcher Classes
- Core Dependencies
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Architectural Considerations - Developer Guidelines - Development | OpenBB Platform Docs" />

## Important classes

### The `Data` class

The OpenBB Standardized Data Model.

The `Data` class is a flexible Pydantic model designed to accommodate various data structures
for OpenBB's data processing pipeline as it's structured to support dynamic field definitions.

The model leverages Pydantic's powerful validation features to ensure data integrity while
providing the flexibility to handle extra fields that are not explicitly defined in the model's
schema. This makes the `Data` class ideal for working with datasets that may have varying
structures or come from heterogeneous sources.

Key Features:

- Dynamic field support: Can dynamically handle fields that are not pre-defined in the model,
    allowing for great flexibility in dealing with different data shapes.
- Alias handling: Utilizes an aliasing mechanism to maintain compatibility with different naming
    conventions across various data formats.

Usage:

The `Data` class can be instantiated with keyword arguments corresponding to the fields of the
expected data. It can also parse and validate data from JSON or other serializable formats, and
convert them to a `Data` instance for easy manipulation and access.

Example:

```python
from openbb_core.provider.abstract.data import Data

# Direct instantiation
data_record = Data(name="OpenBB", value=42)

# Conversion from a dictionary
data_dict = {"name": "OpenBB", "value": 42}
data_record = Data(**data_dict)
```

The class is highly extensible and can be subclassed to create more specific models tailored to
particular datasets or domains, while still benefiting from the base functionality provided by the
`Data` class.

### The `QueryParams` class

The QueryParams class is a standardized model for handling query input parameters in the OpenBB platform. It extends the BaseModel from the Pydantic library, which provides runtime data validation and serialization.

The class includes a dictionary, `__alias_dict__`, which can be used to map the original parameter names to aliases. This can be useful when dealing with different data providers that may use different naming conventions for similar parameters.

The `__repr__` method provides a string representation of the QueryParams object, which includes the class name and a list of the model's parameters and their values.

The `model_config` attribute is a `ConfigDict` instance that allows extra fields not defined in the model and populates the model by name.

The `model_dump` method is used to serialize the model into a dictionary. If the `__alias_dict__` is not empty, it will use the aliases defined in it for the keys in the returned dictionary. If the `__alias_dict__` is empty, it will return the original serialized model.

### The `Fetcher` class

The `Fetcher` class is an abstract base class designed to provide a structured way to fetch data from various providers. It uses generics to allow for flexibility in the types of queries, data, and return values it handles.

The class defines a series of methods that must be implemented by any subclass: `transform_query`, `extract_data`, and `transform_data`. These methods represent the core steps of fetching data: transforming input parameters into a provider-specific query, extracting data from the provider using the query, and then transforming the provider-specific data into a desired format.

The `fetch_data` method orchestrates these steps, taking in parameters and optional credentials, and returning the transformed data.

The class also includes a test method for validating the functionality of a fetcher, performing assertions on each stage of the fetch process.

Additionally, the `Fetcher` class uses a custom `classproperty` decorator to define class-level properties that return the types of the query parameters, return value, and data.

The `require_credentials` class variable indicates whether credentials are needed to fetch data from the provider. This can be overridden by subclasses as needed.

:::info
The `Fetcher` class implementation is based on the [TET pattern](/platform/development/developer-guidelines/architectural_considerations#the-tet-pattern). This pattern imposes a standardized structure, namely:

- Transform the query: the output of this method should be `QueryParams` child.
- Extract the data: the output of this method can be `Any` but it's recommended to be a `Dict` (will facilitate the next step of the fetcher's action, the data transformation).
- Transform the data: the output of this method should be a `List[Data]` or `Data` (or a child of it).
:::

### The `OBBject` class

The OBBject class is a generic class in the OpenBB platform that represents a standardized object for handling and manipulating data fetched from various providers. It extends the `Tagged` class and uses Python's generics to allow flexibility in the type of results it can handle.

The class includes several fields such as results, provider, warnings, chart, and extra, which respectively represent the fetched data, the data provider, any warnings generated during data fetching, an optional chart object for visualizing the data, and a dictionary for any additional information.

The class provides several methods for converting the fetched data into different formats, including `to_df` (or `to_dataframe`) for converting to a pandas DataFrame, `to_polars` for converting to a Polars DataFrame, `to_numpy` for converting to a numpy array, and `to_dict` for converting to a dictionary.

The `to_chart` method allows for creating or updating a chart based on the fetched data, and the show method is used to display the chart.

The class also includes a `__repr__` method for a human-readable representation of the object, and a `model_parametrized_name method` for returning the model name with its parameters.

### The `Router` class

The `Router` class in the OpenBB platform is responsible for managing and routing API requests. It uses the `APIRouter` from the FastAPI library to handle routing.

The class includes a command method that allows for the registration of callable functions as API endpoints. This method takes care of setting up the API route, including defining the HTTP methods, response models, operation IDs, and other necessary parameters for the API endpoint.

The `include_router` method allows for the inclusion of another router, effectively merging the routes from the included router into the current one.

The `Router` class also interacts with the `SignatureInspector` class to validate and complete function signatures, ensuring that the functions registered as API endpoints have the correct parameters and return types.

The `api_router` property provides access to the underlying APIRouter instance, allowing for direct interaction with the FastAPI routing system if needed.

:::info
The `Router` class exposes a `command` decorator that allows for the registration of callable functions as API endpoints. This method takes care of setting up the API route, including defining the HTTP methods, response models, operation IDs, and other necessary parameters for the API endpoint.

This decorator enforces that the decorated function (of type `Callable`) returns an `OBBject` instance. I.e., the signature of a decorated function should translate to `Callable[P, OBBject]` (a callable object (like a function) that takes arguments of type `P` and returns an object of type `OBBject`).
:::

## Import statements

```python

# The `Data` class
from openbb_core.provider.abstract.data import Data

# The `QueryParams` class
from openbb_core.provider.abstract.query_params import QueryParams

# The `Fetcher` class
from openbb_core.provider.abstract.fetcher import Fetcher

# The `OBBject` class
from openbb_core.app.model.obbject import OBBject

# The `Router` class
from openbb_core.app.router import Router

```

## The TET pattern

The TET pattern is a pattern that we use to build the `Fetcher` classes. It stands for **Transform, Extract, Transform**.

![Diagram](https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/ae9908be-00c0-40af-8acb-afeeb9629f2b)

As the OpenBB Platform has its own standardization framework and the data fetcher are a very important part of it, we need to ensure that the data is transformed and extracted in a consistent way, to help us do that, we came up with the **TET** pattern, which helps us build and ship faster as we have a clear structure on how to build the `Fetcher` classes.

1. **Transform** query

    ```python
    transform_query(params: Dict[str, Any])
    ```

    Transforms the query parameters. Given a `params` dictionary this method should return the transformed query parameters as a [`QueryParams`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/openbb_core/provider/abstract/query_params.py) child so that we can leverage the pydantic model schemas and validation into the next step. This might also be the place do perform some transformations on any given parameter, i.e., if you want to transform an empty date into a `datetime.now().date()`.

2. **Extract** data

    ```python
    extract_data(query: ExampleQueryParams,credentials: Optional[Dict[str, str]],**kwargs: Any,) -> Dict
    ```

    Makes the request to the API endpoint and returns the raw data. Given the transformed query parameters, the credentials and any other extra arguments, this method should return the raw data as a dictionary.

3. **Transform** data

    ```python
    transform_data(query: ExampleQueryParams, data: Dict, **kwargs: Any) -> List[ExampleHistoricalData]
    ```

    Transforms the raw data into the defined data model. Given the transformed query parameters (might be useful for some filtering), the raw data and any other extra arguments, this method should return the transformed data as a list of [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/openbb_core/provider/abstract/data.py) children.

## Data processing commands

The data processing commands are commands that are used to process the data that may or may not come from the OpenBB Platform.

In order to create a data processing framework general enough to be used by any extension, we've created a special abstract class called [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/openbb_core/provider/abstract/data.py) which **all** standardized (and consequently its child classes) will inherit from.

**Why is this important?**

We ensure that all `OBBject.results` will share a common ground on which we can apply out-of-the-box data processing commands, such as the `ta`, `qa`, or the `econometrics` menus.

**But what's really the `Data` class?**

It's a pydantic model that inherits from the `BaseModel` and can contain any given number of extra fields. In practice, it looks as follows:

```python
from openbb import obb

res = obb.equity.price.historical("AAPL")
res.results[0]
```

```python
AVEquityHistoricalData(date=2023-11-03 00:00:00, open=174.24, high=176.82, low=173.35, close=176.65, volume=79829246.0, vwap=None, adj_close=None, dividend_amount=None, split_coefficient=None)
```

> The `AVEquityHistoricalData` class, is a child class of the `Data` class.

Note how we've indexed to get only the first element of the `results` list (which represents a single row, if we want to think about it as a tabular output). This simply means that we are getting a `List` of `AVEquityHistoricalData` from the `obb.equity.price.historical` command. Or, we can also say that that's equivalent to `List[Data]`!

This is very powerful, as we can now apply any data processing command to the `results` list, without worrying about the underlying data structure.

That's why, on data processing commands (such as the `ta` menu) we will find on its function signature the following:

```python

def ema(
        self,
        data: Union[List[Data], pandas.DataFrame],
        target: str = "close",
        index: str = "date",
        length: int = 50,
        offset: int = 0,
        chart: bool = False,
    ) -> OBBject[List[Data]]:

    ...

```

> Note that `data` can actually be a different type, but we'll focus on the `List[Data]` case for now.

Does that mean that I can only use the data processing commands if I instantiate a class that inherits from `Data`?
Not at all! Consider the following example:

```python

from openbb_core.provider.abstract.data import Data
my_data_item_1 = {"open": 1, "high": 2, "low": 3, "close": 4, "volume": 5, "date": "2020-01-01"}
my_data_item_1_as_data = Data.model_validate(my_data_item_1)
my_data_item_1_as_data
```

```python
Data(open=1, high=2, low=3, close=4, volume=5, date="2020-01-01")
```

This means that the `Data` class is cleaver enough to understand that you are passing a dictionary and it will try to validate it for you.

In other words, if you're using data that doesn't come from the OpenBB Platform, you only need to ensure it's parsable by the `Data` class and you'll be able to use the data processing commands.

In other words, imagine you have a dataframe that you want to use with the `ta` menu. You can do the following:

```python

res = obb.equity.price.historical("AAPL")
my_df = res.to_dataframe() # yes, you can convert your OBBject.results into a dataframe out-of-the-box!
my_records = df.to_dict(orient="records")

obb.ta.ema(data=my_record)
```

```console
OBBject

results: [{'close': 77.62, 'close_EMA_50': None}, {'close': 80.25, 'close_EMA_50': ...}] # this is a `List[Data]` yet again
```

> Note that that for this example we've used the `OBBject.to_dataframe()` method to have an example dataframe, but it could be any other dataframe that you have.

## Python Interface

When using the OpenBB Platform on a Python Interface, docstrings and type hints are your best friends as it provides plenty of context on how to use the commands.

Looking at an example on the `ta` menu:

```python
def ema(
        self,
        data: Union[List[Data], pandas.DataFrame],
        target: str = "close",
        index: str = "date",
        length: int = 50,
        offset: int = 0,
        chart: bool = False,
    ) -> OBBject[List[Data]]:
```

We can easily deduct that the `ema` command accept data in the formats of `List[Data]` or `pandas.DataFrame`.

> Note that other types might be added in the future.

## API Interface

When using the OpenBB Platform on a API Interface, the types are a bit more limited than on the Python one, as, for example, we can't use `pandas.DataFrame` as a type. However the same principles apply for what `Data` means, i.e., any given data processing command, which are characterized as POST endpoints on the API, will accept data as a list of records on the **request body**, i.e.:

```json
[
    {
        "open": 80,
        "high": 80.69,
        "low": 77.37,
        "close": 77.62,
        "volume": 2487300
    }
]
```

## Core Dependencies

The OpenBB Platform core relies on a set of carefully selected Python libraries to provide its functionality. These dependencies include:

> Note that, in this context by core we mean the `openbb-core` package.

- FastAPI for building the API.
- Uvicorn as the ASGI server.
- Pandas for data manipulation and analysis.
- Pydantic for data validation and serialization using Python type annotations.
- Requests for making HTTP requests.
- Websockets for handling WebSocket connections.

These dependencies are specified in the `pyproject.toml` files.

### Importance of a Lean Core

Keeping the OpenBB Platform core as lean as possible is crucial for maintaining the platform's performance, ease of use, and flexibility. A lean core means faster installation times, less memory usage, and overall better performance. It also reduces the risk of conflicts between dependencies and makes the platform easier to maintain and update.

Moreover, a lean core allows for greater flexibility. Users of the platform can add additional functionality through extensions without being burdened by unnecessary core dependencies. This makes the OpenBB Platform adaptable to a wide range of use cases and requirements.
