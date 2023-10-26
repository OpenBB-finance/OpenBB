---
title: Data Standardization
sidebar_position: 2
description: Learn what is data standardization and how does it work inside the OpenBB Platform.
keywords: [openbb platform, introduction, data standardization, contributing, documentation]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data Standardization - Platform | OpenBB Docs" />

The Standardization Framework is a set of tools and guidelines that enable the user to query and obtain data in a consistent way across multiple providers.

Each data model should inherit from a [standard data](https://github.com/OpenBB-finance/OpenBBTerminal/tree/feature/openbb-sdk-v4/openbb_platform/platform/provider/openbb_provider/standard_models) model that is already defined inside the OpenBB Platform. All standard models are created and maintained by the OpenBB team.

Usage of these models will unlock a set of perks that are only available to standardized data, namely:

- Can query and output data in a standardized way.
- Can expect extensions that follow standardization to work out-of-the-box.
- Can expect transparently defined schemas for the data that is returned by the API.
- Can expect consistent data types and validation.
- Will work seamlessly with other providers that use the same standard model.

The standard models are defined under the `./platform/core/provider/openbb_provider/standard_models/` directory.

They define the [`QueryParams`](https://github.com/OpenBB-finance/OpenBBTerminal/tree/feature/openbb-sdk-v4/openbb_platform/platform/provider/openbb_provider/abstract/query_params.py) and [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/tree/feature/openbb-sdk-v4/openbb_platform/platform/provider/openbb_provider/abstract/data.py) models, which are used to query and output data. They are pydantic and you can leverage all the pydantic features such as validators.

## Standardization Caveats

The standardization framework is a very powerful tool, but it has some caveats that you should be aware of:

- We standardize fields that are shared between two or more providers. If there is a third provider that doesn't share the same fields, we will declare it as an `Optional` field.
- When mapping the column names from a provider-specific model to the standard model, the CamelCase to snake_case conversion is done automatically. If the column names are not the same, you'll need to manually map them. (e.g. `o` -> `open`)
- The standard models are created and maintained by the OpenBB team. If you want to add a new field to a standard model, you'll need to open a PR to the OpenBB Platform.

## Standard QueryParams Example

```python
class StockHistoricalQueryParams(QueryParams):
    """Stock end of day Query."""
    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
```

The `QueryParams` is an abstract class that just tells us that we are dealing with query parameters

The OpenBB Platform dynamically knows where the standard models begin in the inheritance tree, so you don't need to worry about it.

## Standard Data Example

```python
class StockHistoricalData(Data):
    """Stock end of day price Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
    vwap: Optional[PositiveFloat] = Field(description=DATA_DESCRIPTIONS.get("vwap", ""), default=None)
```

The `Data` class is an abstract class that tells us the expected output data. Here we can see a `vwap` field that is `Optional`. This is because not all providers share this field while it is shared between two or more providers.
