---
title: search
description: Learn how to search for available currency pairs using the `obb.currency.search`
  function, and retrieve a list of results, including provider name, warnings, chart,
  and metadata. Explore the various parameters such as provider, symbol, date, search
  terms, active tickers, order data, sort field, and limit. Dive into the details
  of the returned data, including name, symbol, currency, stock exchange, exchange
  short name, code, base currency, quote currency, market, locale, currency symbol,
  currency name, base currency symbol, base currency name, last updated timestamp
  in UTC, and delisted timestamp in UTC.
keywords: 
- currency search
- available currency pairs
- obb.currency.search
- provider
- symbol
- date
- search terms
- active tickers
- order data
- sort field
- limit
- results
- warnings
- chart
- metadata
- name
- symbol
- currency
- stock exchange
- exchange short name
- code
- base currency
- quote currency
- market
- locale
- currency symbol
- currency name
- base currency symbol
- base currency name
- last updated utc
- delisted utc
---

<!-- markdownlint-disable MD041 -->

Currency Search. Search available currency pairs.

## Syntax

```excel wordwrap
=OBB.CURRENCY.SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, intrinio, polygon | True |
| symbol | Text | Symbol of the pair to search. (provider: polygon) | True |
| date | Text | A specific date to get data for. (provider: polygon) | True |
| search | Text | Search for terms within the ticker and/or company name. (provider: polygon) | True |
| active | Boolean | Specify if the tickers returned should be actively traded on the queried date. (provider: polygon) | True |
| order | Text | Order data by ascending or descending. (provider: polygon) | True |
| sort | Text | Sort field used for ordering. (provider: polygon) | True |
| limit | Number | The number of data entries to return. (provider: polygon) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| name | Name of the currency pair.  |
| symbol | Symbol of the currency pair. (provider: fmp) |
| currency | Base currency of the currency pair. (provider: fmp) |
| stock_exchange | Stock exchange of the currency pair. (provider: fmp) |
| exchange_short_name | Short name of the stock exchange of the currency pair. (provider: fmp) |
| code | Code of the currency pair. (provider: intrinio) |
| base_currency | ISO 4217 currency code of the base currency. (provider: intrinio) |
| quote_currency | ISO 4217 currency code of the quote currency. (provider: intrinio) |
| market | Name of the trading market. Always 'fx'. (provider: polygon) |
| locale | Locale of the currency pair. (provider: polygon) |
| currency_symbol | The symbol of the quote currency. (provider: polygon) |
| currency_name | Name of the quote currency. (provider: polygon) |
| base_currency_symbol | The symbol of the base currency. (provider: polygon) |
| base_currency_name | Name of the base currency. (provider: polygon) |
| last_updated_utc | The last updated timestamp in UTC. (provider: polygon) |
| delisted_utc | The delisted timestamp in UTC. (provider: polygon) |
