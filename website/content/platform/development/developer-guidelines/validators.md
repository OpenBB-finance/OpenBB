---
title: Validators
sidebar_position: 4
description: This guide provides detailed instructions on how and where validators should be used.
keywords:
- OpenBB Platform
- Data point addition
- Provider creation
- Query parameters
- Data output models
- Fetcher class
- validator
- field
- param
- Fast API
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Validators - Developer Guidelines - Development | OpenBB Platform Docs" />

Both QueryParams and Data models can benefit from the tactical use of Pydantic validators. This page will outline some of the key scenarios where they are deployed. Overall, they assist with enforcing Fast API compliance for both inputs and outputs.

## Why Use Validators?

Some situations where they are used include:

- A query  parameter accepts a List.
- A query parameter is a date.
- A query parameter requires a dynamic default state.
- A data field is a date.
- A data field is a number but the source values contain string elements.

## Examples

### String or List of Strings

To enforce compliance with Fast API, a list needs to be converted to a comma-separated string.  This type of validator works on the **input** of the model, and it ensures that both the Python interface and the Rest API are able to accept a list of symbols, or just one.

```python
from typing import List, Optional, Set, Union
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from dateutil import parser
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator, model_validator

class EquityHistoricalQueryParams(QueryParams):
    """Equity Historical Price Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    interval: Optional[str] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])

symbols = ["AAPL", "MSFT", "GOOG"]
params = EquityHistoricalQueryParams(symbol=symbols)

params.model_dump()
```

```python
{'symbol': 'AAPL,MSFT,GOOG',
 'interval': '1d',
 'start_date': None,
 'end_date': None}
```

The list of symbols can also be entered as a comma-separated string:

```python
symbols = "AAPL,MSFT,GOOG"
params = EquityHistoricalQueryParams(symbol=symbols)
params.model_dump()
```

```python
{'symbol': 'AAPL,MSFT,GOOG',
 'interval': '1d',
 'start_date': None,
 'end_date': None}
```

### Dynamic Default Date

It might be desirable to have a default date parameter that is not static.  To allow this, we must set the default as `None`, and use the `model_validator`.  The block below is added to the class defined above.

```python
    @model_validator(mode="before")
    @classmethod
    def validate_dates(cls, values) -> dict:
        """Validate the query parameters."""
        if values.get("start_date") is None:
            values["start_date"] = (datetime.now() - timedelta(days=90)).strftime(
                "%Y-%m-%d"
            )
        if values.get("end_date") is None:
            values["end_date"] = datetime.now().strftime("%Y-%m-%d")
        return values
```

```python
params = EquityHistoricalQueryParams(symbol=symbols)
params.model_dump()
```

```python
{'symbol': 'AAPL,MSFT,GOOG',
 'interval': '1d',
 'start_date': datetime.date(2023, 8, 30),
 'end_date': datetime.date(2023, 11, 28)}
```

### Formatting Dates

Providers will format dates in a number of ways.  OpenBB uses YYYY-MM-DD as the standard convention.  Validators are setup to parse the date from the source format to the desired one.  The validator below is used in some data models to convert date values to a datetime object.

```python
    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        return parser.isoparse(str(v))
```
