---
title: Considerations
sidebar_position: 1
description: Learn about the OpenBB Platform, an open-source solution built by the
  community. Understand its use via Python interface and REST API, and acquaint yourself
  with how to build a custom extension or contribute directly to the platform
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

<HeadTitle title="Considerations - Development | OpenBB Platform Docs" />

These sections provide guidelines for developing with, and contributing to, the OpenBB Platform.
There are comprehensive guides on how to build extensions, add new data points, contribute to the code base, and more.

We generalize between two distinct types of users:

1. **Developers**: Those who are building on top of, and extending, the OpenBB Platform for their own purposes and have no intention of contributing the code directly to the GitHub repository. This includes those independently publishing extensions to PyPI or other package managers.
2. **Contributors**: Those who contribute to the existing codebase, by opening a Pull Request, thus giving back to the community.  This can include bug fixes, enhancements, documentation, and more.

**Why Is This Distinction Important?**

The OpenBB Platform has been designed as a foundation for further development of investment research applications. We anticipate a wide range of creative use cases.

Some of them may be highly specific, or detail-oriented, solving particular problems that may not necessarily fit within the OpenBB Platform Github repository. This is entirely acceptable, even encouraged. Regardless of intention, OpenBB is a proponent of building in public and sharing. We love seeing what people are building, so don't be shy about it!


## Before Beginning

- Familiarize yourself with the codebase, architecture, and components.
- Set clear goals with defined outcomes - i.e, I want to create a technical indicator that uses multiple data points and sources where the output is a chart.

Below is a high-level overview of the OpenBB Platform architecture.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
  <img alt="OpenBB Platform High-Level Architecture" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
</picture>

Cloning the [GitHub repo](https://github.com/OpenBB-finance/OpenBBTerminal) will be the best way to inspect and play around with the code.

## What Is The Standardization Framework?

The Standardization Framework is a set of tools and guidelines that enable the user to query and obtain data in a consistent way across multiple providers.

Each provider data model should inherit from an already defined [standard](/platform/data_models) model. All standard models are created and maintained by the OpenBB team. If a standard model needs to be created, please open a pull request and detail its use.

Standardizing provider query parameters and response data enhances the user experience by overcoming things like:

- Consistent query parameters across all data sources for a function, or type of function.
- Output data that has conformed types, is validated, and will be JSON serializable.
  - `NaN`, `NaT`, `"None"`, empty strings, are always returned as `NoneType` (null).
- Transparently defined schemas for the data and query parameters.
- Outputs from multiple sources are comparable with each other and easily interchanged.

The standard models are all defined in the `/OpenBBTerminal/openbb_platform/platform/core/provider/standard_models/` [directory](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_platform/core/openbb_core/provider/standard_models).

### What Is A Standard Model?

Every standard model consists of two classes, with each being a Pydantic model.

- [`QueryParams`](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_platform/core/openbb_core/provider/abstract/query_params.py)
- [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/tree/develop/openbb_platform/core/openbb_core/provider/abstract/data.py)

Any parameter or field can be assigned a custom `field_validator`, or the entire model can be passed through a `model_validator` on creation.

### Caveats

The standardization framework is a very powerful tool, but it has some caveats that you should be aware of:

- We standardize fields and parameters that are shared between multiple providers.
  - In some cases, it can be undesirable to define common items in the standard model. In this event, we still want consistent names and descriptions.
- When mapping the column names from a provider-specific model to the standard model, the CamelCase to snake_case conversion is done automatically. If the column names are not the same, you'll need to manually map them.
  - e.g., `__alias_dict__ = {"o": "open"}`
- The standard models are created and maintained by the OpenBB team. If you want to add or modify a field within a standard model, you'll need to open a PR to the OpenBB Platform.


### QueryParams

The `QueryParams` is an abstract class that defines what parameters will be needed to make a query to a data source. Below is the [EquityHistorical](data_models/EquityHistorical) standard model.

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

## What Is An Extension?

An extension is an installable component adding functionality to the OpenBB Platform. It can be a new data source, a new command, a new visualization, or anything imaginable. They can generally be classified as one of:

- Data Provider
  - The individual sources of data.
- Toolkit
  - Data processing, router modules, visualizations.
- OBBject
  - Extending the OBBject class itself.

The extensions within the OpenBB GitHub repository are maintained by the OpenBB Team. We welcome contributions, and anyone is also able to publish their own OpenBB extension to PyPI, or elsewhere. If you do, please name the package beginning with, "openbb-". We love seeing what you build!
