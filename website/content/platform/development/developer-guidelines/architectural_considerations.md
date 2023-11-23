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
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Architectural Considerations - Developer Guidelines - Development | OpenBB Platform Docs" />

## Important classes

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
As the OpenBB Platform has its own standardization framework and the data fetcher are a very important part of it, we need to ensure that the data is transformed and extracted in a consistent way, to help us do that, we came up with the **TET** pattern, which helps us build and ship faster as we have a clear structure on how to build the `Fetcher` classes.

1. **Transform** query

    ```python
    transform_query(params: Dict[str, Any])
    ```

    Transforms the query parameters. Given a `params` dictionary this method should return the transformed query parameters as a [`QueryParams`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/provider/abstract/query_params.py) child so that we can leverage the pydantic model schemas and validation into the next step. This might also be the place do perform some transformations on any given parameter, i.e., if you want to transform an empty date into a `datetime.now().date()`.

2. **Extract** data

    ```python
    extract_data(query: ExampleQueryParams,credentials: Optional[Dict[str, str]],**kwargs: Any,) -> Dict
    ```

    Makes the request to the API endpoint and returns the raw data. Given the transformed query parameters, the credentials and any other extra arguments, this method should return the raw data as a dictionary.

3. **Transform** data

    ```python
    transform_data(query: ExampleQueryParams, data: Dict, **kwargs: Any) -> List[ExampleHistoricalData]
    ```

    Transforms the raw data into the defined data model. Given the transformed query parameters (might be useful for some filtering), the raw data and any other extra arguments, this method should return the transformed data as a list of [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/provider/abstract/data.py) children.

## Data processing commands

The data processing commands are commands that are used to process the data that may or may not come from the OpenBB Platform.
In order to create a data processing framework general enough to be used by any extension, we've created a special abstract class called `Data`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/core/provider/abstract/data.py) which **all** standardized (and consequently its child classes) will inherit from.

Why is this important?
So that we can ensure that all `OBBject.results` will share a common ground on which we can apply out-of-the-box data processing commands, such as the `ta`, `qa` or the `econometrics` menus.

But what's really the `Data` class?
It's a pydantic model that inherits from the `BaseModel` and can contain any given number of extra fields. In practice, it looks as follows:

```python

>>> res = obb.equity.price.historical("AAPL")
>>> res.results[0]

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

>>> from openbb_core.provider.abstract.data import Data
>>> my_data_item_1 = {"open": 1, "high": 2, "low": 3, "close": 4, "volume": 5, "date": "2020-01-01"}
>>> my_data_item_1_as_data = Data.model_validate(my_data_item_1)
>>> my_data_item_1_as_data

Data(open=1, high=2, low=3, close=4, volume=5, date=2020-01-01)

```

This means that the `Data` class is cleaver enough to understand that you are passing a dictionary and it will try to validate it for you.
In other words, if you're using data that doesn't come from the OpenBBPlatform, you only need to ensure it's parsable by the `Data` class and you'll be able to use the data processing commands.
In other words, imagine you have a dataframe that you want to use with the `ta` menu. You can do the following:

```python

>>> res = obb.equity.price.historical("AAPL")
>>> my_df = res.to_dataframe() # yes, you can convert your OBBject.results into a dataframe out-of-the-box!
>>> my_records = df.to_dict(orient="records")

>>> obb.ta.ema(data=my_record)

OBBject

results: [{'close': 77.62, 'close_EMA_50': None}, {'close': 80.25, 'close_EMA_50': ... # this is a `List[Data]` yet again

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

    ...

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
    ...
]

```
