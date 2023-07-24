# Table of contents

- [Table of contents](#table-of-contents)
  - [provider](#provider)
  - [What is Data Standardization?](#what-is-data-standardization)
  - [Key Elements](#key-elements)
  - [Installation](#installation)

## provider

The OpenBB Provider aims to give a coherent access to financial data providers by introducing standardization procedures.

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

## Key Elements

- **QueryParams** : Are input parameters that are used for obtaining data. To load stock market data, we would have StockQueryParams, which would have fields like symbol, start date, and end date. You can find the standard query params inside the `./models` folder.
- **Data** : Are outputs. Stock market data would be StockPriceData and have fields such as Open, High, Low, Close, and Volume. You can find the standard data models inside the `./models` folder.
- **Fetcher** : A provider-specific object (FMPStockPriceFetcher) that holds executable logic that performs the standardization procedure going from QueryParams to the Data.
- **Provider** : An object that is specific to a data provider (i.e. PolygonProvider) which holds Provider attributes and unites all of the provider's fetchers into a list.
- **Provider Registry** : An aggregation of all the Provider objects and their API keys. It is the main point of usage and is responsible for dynamically serving the data by finding the correct Provider and Fetcher based on the given QueryParams.

## Installation

To install the provider, run the following command in this folder:

```bash
pip install .
```
