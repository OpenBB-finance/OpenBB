---
title: Introduction
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

<HeadTitle title="Introduction - Development | OpenBB Platform Docs" />

## Considerations

This section provides guidelines for contributing to the OpenBB Platform.
Throughout it, we will be differentiating between two types of contributors: Developers and Contributors.

1. **Developers**: Those who are building new features or new extensions for the OpenBB Platform or leveraging the OpenBB Platform for custom applications.
2. **Contributors**: Those who contribute to the existing codebase, by opening a Pull Request, thus giving back to the community.  This can include bug fixes, enhancements, documentation, and more.

**Why is this distinction important?**

The OpenBB Platform has been designed to be the foundation for further development of applications regarding investment research. We anticipate a wide range of creative use cases for it. Some use cases may be highly specific or detail-oriented, solving particular problems that may not necessarily fit within the OpenBB Platform Github repository. This is entirely acceptable and even encouraged. This document provides a comprehensive guide on how to build your own extensions, add new data points, and more.

The **Developer** role, as defined in this document, can be thought of as the foundational role. Developers are those who use the OpenBB Platform as is or build upon it.

The **Contributor** role refers to those who enhance the OpenBB Platform codebase (either by directly adding to the OpenBB Platform or by creating an [extension](/platform/extensions)). Contributors are willing to go the extra mile, spending additional time on quality assurance, testing, or collaborating with the OpenBB development team to ensure adherence to standards, thereby giving back to the community.

## Quick look into the OpenBB Platform

The OpenBB Platform was built by the Open-Source community and is characterized by its core and extensions. The core handles data integration and standardization, while extensions enable customization and advanced functionalities. The OpenBB Platform is designed to be used from either a REST API or from a Python package.

The REST API is built on top of FastAPI and can be started by running the following command from the root:

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

The Python interface we provide to users is the `openbb` python package.

The code you will find in this package is generated from a script, which is a wrapper around the `openbb-core` with any additional extensions that are installed.

When the user runs `import openbb`, `from openbb import obb` or other variants, the script that generates the packaged code is triggered. It detects if there are new extensions installed in the environment and rebuilds the packaged code accordingly. If new extensions are not found, it uses the current packaged version.

In the case you wish to manually trigger a rebuild of the package (see more in the contributing information), the following command can be run:

```python
python -c "import openbb; openbb.build()"
```

The Python interface can be imported with:

```python
from openbb import obb
```

The remainder of this document will take you through two types of contributions:

1. Building a custom extension
2. Contributing directly to the OpenBB Platform

Before moving forward, please take a look at the high-level view of the OpenBB Platform architecture. We will go over each bit in this document.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
  <img alt="OpenBB Platform High-Level Architecture" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
</picture>

### What is the Standardization Framework?

The Standardization Framework is a set of tools and guidelines that enable the user to query and obtain data in a consistent way across multiple providers.

Each data model should inherit from a [standard data](platform/core/provider/standard_models) model that is already defined inside the OpenBB Platform. All standard models are created and maintained by the OpenBB team.

Usage of these models will unlock a set of perks that are only available to standardized data, namely:

- Can query and output data in a standardized way.
- Can expect extensions that follow standardization to work out-of-the-box.
- Can expect transparently defined schemas for the data that is returned by the API.
- Can expect consistent data types and validation.
- Will work seamlessly with other providers that use the same standard model.

The standard models are defined under the `/OpenBBTerminal/openbb_platform/platform/core/provider/standard_models/` directory.

Each standard model defines a [`QueryParams`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/platform/provider/openbb_provider/abstract/query_params.py) and [`Data`](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/openbb_platform/platform/provider/openbb_provider/abstract/data.py) model, which are used to query and output data. Under the hood, these are just pydantic models, meaning you can leverage all the built-in pydantic features such as validators.

#### Standardization Caveats

The standardization framework is a very powerful tool, but it has some caveats that you should be aware of:

- We standardize fields that are shared between two or more providers. If there is a third provider that doesn't share the same fields, we will declare it as an `Optional` field.
- When mapping the column names from a provider-specific model to the standard model, the CamelCase to snake_case conversion is done automatically. If the column names are not the same, you'll need to manually map them. (e.g. `o` -> `open`)
- The standard models are created and maintained by the OpenBB team. If you want to add a new field to a standard model, you'll need to open a PR to the OpenBB Platform.

#### Standard QueryParams Example

An example `QueryParams` is shown here, coming from the EquityHistorical standard model:

```python
class EquityHistoricalQueryParams(QueryParams):
    """Stock end of day Query."""
    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
```

The `QueryParams` is an abstract class that defines what parameters will be needed to make a query to obtain data.  Note that not all possible parameters are defined here, and can be further refined in the provider-specific model.

The OpenBB Platform dynamically knows where the standard models begin in the inheritance tree, so you don't need to worry about it.

#### Standard Data Example

The `Data` model for the EquityHistorical standard model is shown here:

```python
class EquityHistoricalData(Data):
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

### What is an extension?

An extension adds functionality to the OpenBB Platform. It can be a new data source, a new command, a new visualization, etc.

#### Types of extensions

Extensions currently fall into 3 categories:

1. OpenBB Extensions - built and maintained by the OpenBB team (e.g. `openbb-equity`)
2. Community Extensions - built by anyone and primarily maintained by OpenBB (e.g. `openbb-yfinance`)
3. Independent Extensions - built and maintained independently by anyone

If you have built an extension and you think that it would be a good community extension, you can open a PR to the OpenBB Platform repository and we will review it.

We encourage independent extensions to be shared with the community by publishing them to PyPI.
