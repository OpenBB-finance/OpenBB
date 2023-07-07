# THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE

# Table of contents

- [THIS README IS A WORK IN PROGRESS AND CAN BE VERY MUCH OUT OF DATE. REFRESH THE PAGE UNTIL THIS BANNER IS GONE](#this-readme-is-a-work-in-progress-and-can-be-very-much-out-of-date-refresh-the-page-until-this-banner-is-gone)
- [Table of contents](#table-of-contents)
- [openbb-provider](#openbb-provider)
  - [What is Data Standardization?](#what-is-data-standardization)
- [Key Elements](#key-elements)
- [How to use it?](#how-to-use-it)
    - [Prerequisites](#prerequisites)
    - [1. Defining : OpenBB QueryParams](#1-defining--openbb-queryparams)
    - [2. Querying the Provider Table : OpenBB QueryParams -\> OpenBB Data](#2-querying-the-provider-table--openbb-queryparams---openbb-data)
- [Different ways of usage](#different-ways-of-usage)
    - [1. OpenBB QueryParams -\> OpenBB Data](#1-openbb-queryparams---openbb-data)
    - [2. OpenBB QueryParams -\> Provider Data](#2-openbb-queryparams---provider-data)
    - [3. Provider QueryParams -\> OpenBB Data](#3-provider-queryparams---openbb-data)
    - [4. Provider QueryParams -\> Provider Data](#4-provider-queryparams---provider-data)
- [Data Mapping](#data-mapping)
- [Package extension : Adding a new Data Provider extension](#package-extension--adding-a-new-data-provider-extension)
  - [1. Build a Python package](#1-build-a-python-package)
  - [2. Entrypoint](#2-entrypoint)
  - [3. Install the extension](#3-install-the-extension)

# openbb-provider

The openbb_providers aim to give a coherent access to Financial Data Providers by introducing standardization procedures.

## What is Data Standardization?
OpenBB Data Standardization is a process of transforming data into a common format to allow for efficient and accurate information processing, comparison, and analysis.

Our data standardization can be considered as a sub-process of more general data normalization. There are some things that we do and don’t do when we apply OpenBB Data Standardization.

**We do**:
**Consistent Column Name Coding and Formats**: we ensure that data are consistently coded on a column name and column type level.

**Examples**:
Close for closing price column name in data from one provider might be coded as c in data from another provider Date and time can come in formats like YYYY-MM-DD, MM-DD-YYYY, and Unix timestamps in data from different providers. Standardization would bring these to a common format.

**We don’t do**:
**Data Cleaning**: we don’t remove errors and inconsistencies from data provider outputs.
**Data Transformation & Data Integration**: both transforming data by processing it and integrating data from multiple providers together to harmonize datasets are functions of the SDK and are not handled on a provider level.

# Key Elements

- **QueryParams** : Are input parameters that are used for obtaining data. To load stock market data, we would have StockQueryParams, which would have fields like symbol, start date, and end date.
- **Data** : Are outputs. Stock market data would be StockPriceData and have fields such as Open, High, Low, Close, and Volume.
- **Fetcher** : A provider-specific object (FMPStockPriceFetcher) that holds executable logic that performs the standardization procedure going from QueryParams to the Data.
- **Provider** : An object that is specific to a data provider (i.e. PolygonProvider) which holds Provider attributes and unites all of the provider's fetchers into a list.
- **Provider Registry** : An aggregation of all the Provider objects and their API keys. It is the main point of usage and is responsible for dynamically serving the data by finding the correct Provider and Fetcher based on the given QueryParams.

# How to use it?

### Prerequisites

- Python 3.9 or higher
- .env file with the following variables:
  - FMP_API_KEY
  - POLYGON_API_KEY
  - BENZINGA_API_KEY
- Install the dependencies:
  - `pip install poetry==1.4.1`
  - `poetry install`

### 1. Defining : OpenBB QueryParams

```python
from openbb_provider.model.data.stock_eod import StockEODQueryParams

query = StockEODQueryParams(
  symbol="AAPL",
  start_date="2022-01-01",
)
```

### 2. Querying the Provider Table : OpenBB QueryParams -> OpenBB Data

```python
from openbb_provider.provider.provider_registry import provider_registry

data = provider_registry.fetch(provider_name="fmp", query=query)
print(data)
```

# Different ways of usage

### 1. OpenBB QueryParams -> OpenBB Data

This is the most common way of usage that the SDK v4 users will use.

```python
provider_registry.fetch(provider_name="fmp", query=query)
```

### 2. OpenBB QueryParams -> Provider Data

This way uses the standardized query to obtain the raw data from the Provider. This is useful when the user wants specific data that is not available in the standardized data.

```python
provider_registry.fetch_provider_data(provider_name="fmp", query=query)
```

### 3. Provider QueryParams -> OpenBB Data

This way uses the Provider QueryParams to obtain the standardized data. This is useful when the user wants to use a specific query field that is not available in the standardized query.

```python
provider_registry.standardized(provider_name="fmp", query=provider_query)
```

### 4. Provider QueryParams -> Provider Data

This way uses the Provider QueryParams to obtain the raw data from the Provider. This is useful when the user wants specific data that is not available in the standardized data and wants to use a specific query field that is not available in the standardized query. It is the same a using the Provider directly.

```python
provider_registry.simple(provider_name="fmp", query=provider_query)
```

# Data Mapping

The data mapping is done in the following [file](https://docs.google.com/spreadsheets/d/1AhmQWGRDqORk8nlcNclcnCuPpWsdMuaHwxujMMdzcsk/edit#gid=152728452
).

# Package extension : Adding a new Data Provider extension

## 1. Build a Python package

```bash
poetry new opebb-provider-your_extension
```

## 2. Entrypoint

Add an entrypoint for the extension inside your `pyproject.toml` file

```toml
# File openbb_providers/pyproject.toml
...
[tool.poetry.plugins."openbb_provider_extension"]
extension_name_space = "my_extension.provider:provider_module"
```

## 3. Install the extension

```bash
poetry install
```
