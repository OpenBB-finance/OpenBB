# Table of contents

- [Table of contents](#table-of-contents)
- [Temporary glossary](#temporary-glossary)
- [openbb-provider](#openbb-provider)
  - [Functional Requirements](#functional-requirements)
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
- [Package extension : Adding a new Provider extension](#package-extension--adding-a-new-provider-extension)
  - [1. Build a Python package](#1-build-a-python-package)
  - [2. Entrypoint](#2-entrypoint)
  - [3. Install the extension](#3-install-the-extension)

# Temporary glossary

- **Provider** : A Provider is a Financial Data Provider such as FMP, Polygon, Benzinga, etc.
- **QueryParams** : A set of parameters that define a request to a Provider. It is defined by the user.
- **Provider QueryParams** : A set of parameters which are defined by the Provider.
- **Data** : A standardized set of data that is returned by a Provider and then standardized.
- **Provider Data** : Provider Data is a raw set of data that is returned by a Provider as is.

# openbb-provider

This library aim to give a coherent access to Financial Data Providers.

It provides coherence on:

- QueryParams : one can define QueryParams and use them on multiple Financial Data Providers.
- Data : one can process the data provided by multiple Financial Data Providers as if there were from the same one.

## Functional Requirements

Functional requirements are the following:

- Provide a standardized access to similar Data from multiple Data Providers.
- Use the same QueryParams to query similar Data from multiple Providers.
- Get similar Data from multiple Provider and process it as if there were from the same Provider.

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

This will primarily be used for integration tests so that we can notice Provider API changes in time and adjust the mapping accordingly.

```python
provider_registry.simple(provider_name="fmp", query=provider_query)
```

# Data Mapping

The data mapping is done in the following [file](https://docs.google.com/spreadsheets/d/1AhmQWGRDqORk8nlcNclcnCuPpWsdMuaHwxujMMdzcsk/edit#gid=152728452
).

# Package extension : Adding a new Provider extension

## 1. Build a Python package

```bash
poetry new opebb-provider-your_extension
```

## 2. Entrypoint

Add an entrypoint for the extension inside your `pyproject.toml` file

```toml
# File pyproject.toml
...
[tool.poetry.extensions."openbb_provider_extension"]
extension_name_space = "my_extension.provider:provider_module"
```

## 3. Install the extension

```bash
poetry install
```
