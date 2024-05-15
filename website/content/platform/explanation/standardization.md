---
title: Standardization
sidebar_position: 1
description: Learn about the OpenBB Platform, an open-source solution built by the community. Understand its use via Python interface and REST API, and acquaint yourself with how to build a custom extension or contribute directly to the platform
keywords:
- OpenBB Platform
- Open source
- Python interface
- REST API
- Data integration
- Data standardization
- OpenBB extensions
- openbb-core
- Python package
- High-Level Architecture
- Custom extension
- Contribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Standardization - Development | OpenBB Platform Docs" />

## What Is The Standardization Framework?

The Standardization Framework is a set of tools and guidelines that enable the user to query and obtain data in a consistent way across multiple providers.

Each provider data model should inherit from an already defined [standard](https://docs.openbb.co/platform/data_models) model. All standard models are created and maintained by the OpenBB team. If a standard model needs to be created, please open a pull request and detail its use.

Standardizing provider query parameters and response data enhances the user experience by overcoming things like:

- Consistent query parameters across all data sources for a function, or type of function.
- Output data that has conformed types, is validated, and will be JSON serializable.
  - `NaN`, `NaT`, `"None"`, empty strings, are always returned as `NoneType` (null).
- Transparently defined schemas for the data and query parameters.
- Outputs from multiple sources are comparable with each other and easily interchanged.

The standard models are all defined in the `/OpenBBTerminal/openbb_platform/core/openbb_core/provider/standard_models/` [directory](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_platform/core/openbb_core/provider/standard_models).

### What Is A Standard Model?

Every standard model consists of two classes, with each being a Pydantic model.

- [`QueryParams`](https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/openbb_platform/core/openbb_core/provider/abstract/query_params.py)
- [`Data`](https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/openbb_platform/core/openbb_core/provider/abstract/data.py)

Any parameter or field can be assigned a custom `field_validator`, or the entire model can be passed through a `model_validator` on creation.

### Caveats

The standardization framework is a very powerful tool, but it has some caveats that you should be aware of:

- We standardize fields and parameters that are shared between multiple providers.
  - In some cases, it can be undesirable to define common items in the standard model. In this event, we still want consistent names and descriptions.
- When mapping the column names from a provider-specific model to the standard model, the CamelCase to snake_case conversion is done automatically. If the column names are not the same, you'll need to manually map them.
  - e.g., `__alias_dict__ = {"o": "open"}`
- The standard models are created and maintained by the OpenBB team. If you want to add or modify a field within a standard model, you'll need to open a PR to the OpenBB Platform.

### QueryParams

The `QueryParams` is an abstract class that defines what parameters will be needed to make a query to a data source. Below is the [EquityHistorical](https://docs.openbb.co/platform/data_models/EquityHistorical) standard model.

```python
"""Equity Historical Price Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional, Union

from dateutil import parser
from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

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
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()
```

:::info
Note that not all possible parameters are defined here, and can be further refined in the provider-specific model.

For example, `interval` is defined as a string in the standard model, but is defined again as a `Literal` with explicit choices specific to that source. Here, it would not be possible to define all valid choices in a way that is compatible with all providers.
:::

### Data

The `Data` model for the `EquityHistorical` standard model is shown below, which is a continuation of the code block above.

```python
class EquityHistoricalData(Data):
    """Equity Historical Price Data."""

    date: Union[dateType, datetime] = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
    )
    open: float = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: float = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: float = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: Optional[Union[float, int]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    vwap: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):
        """Return formatted datetime."""
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
```

The `Data` class is an abstract class that tells us the expected output data.

We can see that the `volume` and `vwap` fields are `Optional`. This is because not all providers return this field, but is common between several of them.

We can also note that `date` is a field name, but because this is a `datetime` class, we import `datetime.datetime.date` as `dateType` to avoid conflicts and linting errors.

The date validator is there to parse an ISO date string, with a caveat to only encode time values when they exist. This avoids dates from being inadvertently encoded with timezone information that can influence the actual date value via localization. Dates should always be the same date for all users globally. If a date is on a Monday, it will always be Monday.
