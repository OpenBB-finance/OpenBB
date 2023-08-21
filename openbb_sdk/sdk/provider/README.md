# Table of contents

- [Table of contents](#table-of-contents)
  - [Provider](#provider)
  - [What is Data Standardization?](#what-is-data-standardization)
  - [Key Elements](#key-elements)
  - [Installation](#installation)

## Provider

The OpenBB Provider aims to give a coherent access to financial data providers by introducing standardization procedures.

## What is Data Standardization?

It's like teaching everyone to speak the same language with their data so we can understand and compare it easily.

**Think of it as a part of**:

Data normalization, a bigger way of organizing data.

**What We Do**:

- **Match Column Names and Formats**: Like making sure everyone calls a "closing price" the same thing.

- **For instance**: Some might say "Close", others might say "c". We make sure everyone uses one term.
**Unify Date and Time Styles**: Like having everyone use the same calendar format.

**Example**: Whether it's "YYYY-MM-DD" or "MM-DD-YYYY", we pick one style for everyone.

**What We Don’t Do**:

- **Cleaning Data**: We don't act like data detectives and remove mistakes from what providers give us.

- **Change & Combine Data**: Tweaking data or mixing data from different places.

## Key Elements

- **QueryParams** : The input model for a particular query. To load stock market data, we would have `StockQueryParams`, which would have fields like `symbol`, `start_date`, and `end_date`. You can find the standard query params inside the `standard_models` directory.
- **Data** : The output model of a particular query. Stock market data would be `StockPriceData` and have fields such as `Open`, `High`, `Low`, `Close`, and `Volume`. You can find the standard data models inside the `standard_models` directory.
- **Fetcher** : Class containing a set of methods to receive query parameters, extract data and transform it. This class is responsible for implementing the standardization procedures.
- **Provider** : Entry point class for each provider extension. Contains information about the provider, it's required credentials and available fetchers.
- **RegistryLoader** : Loads the registry with the installed provider extensions.
- **Registry** : Maintains a registry of provider extensions installed.
- **RegistryMap** : Stores the complete characterization of each provider. It centralizes information like required credentials, standardized and extra query parameters/data by provider.
- **QueryExecutor** : Executes a given query, routing it to the respective provider and fetcher.

## Installation

To install the provider, run the following command in this folder:

```bash
pip install .
```
