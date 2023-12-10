---
title: search
description: The documentation page provides information on how to perform a cryptocurrency
  search, including the search query and provider parameters, as well as the resulting
  crypto search data such as symbol, name, currency, and exchange information.
keywords: 
- cryptocurrency search
- available cryptocurrency pairs
- python obb crypto search
- search query parameter
- provider parameter
- crypto search results
- crypto search provider
- crypto search warnings
- crypto search chart
- crypto search metadata
- crypto data
- symbol
- crypto name
- crypto currency
- crypto exchange
- crypto exchange name
---

<!-- markdownlint-disable MD041 -->

Cryptocurrency Search. Search available cryptocurrency pairs.

## Syntax

```excel wordwrap
=OBB.CRYPTO.SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| query | Text | Search query. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (Crypto)  |
| name | Name of the crypto.  |
| currency | The currency the crypto trades for. (provider: fmp) |
| exchange | The exchange code the crypto trades on. (provider: fmp) |
| exchange_name | The short name of the exchange the crypto trades on. (provider: fmp) |
