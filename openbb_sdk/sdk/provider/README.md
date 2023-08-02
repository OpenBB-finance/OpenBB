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

- **QueryParams** : The input model for a particular query. To load stock market data, we would have StockQueryParams, which would have fields like symbol, start date, and end date. You can find the standard query params inside the `./models` folder.
- **Data** : The output model of a particular query. Stock market data would be StockPriceData and have fields such as Open, High, Low, Close, and Volume. You can find the standard data models inside the `./models` folder.
- **Fetcher** : Class containing a set of methods to receive query parameters, extract data and transform it, if necessary.
- **Provider** : Entry point class for each provider extension. Contains information about the provider, it's required credentials and available fetchers.
- **RegistryLoader** : Loads the registry with the provider extensions installed.
- **Registry** : Maintains a registry of provider extensions installed.
- **RegistryMap** : Stores the complete characterization of each provider. It centralizes information like required credentials, standardised and extra query parameteres/data by provider.
- **QueryExecutor** : Executes a given query, routing it to the respective provider and fetcher.

## Installation

To install the provider, run the following command in this folder:

```bash
pip install .
```
