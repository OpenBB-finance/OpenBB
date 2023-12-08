---
title: search
description: Learn how to perform an equity search to find a company or stock ticker.
  Understand the query parameters, such as search by ticker symbol and search provider.
  Explore the various filters available, including market cap, price, beta, volume,
  dividend, ETF, sector, industry, country, and exchange. Limit and structure the
  results accordingly. Get access to the returned data, provider information, warnings,
  chart, and metadata.
keywords: 
- equity search
- company search
- stock ticker search
- query parameter
- search by ticker symbol
- search provider
- market cap filter
- price filter
- beta filter
- volume filter
- dividend filter
- ETF filter
- sector filter
- industry filter
- country filter
- exchange filter
- limit results
- data structure
- results
- provider
- warnings
- chart
- metadata
- symbol
- name
- dpm_name
- post_station
- market cap
- sector
- industry
- beta
- price
- last annual dividend
- volume
- exchange
- exchange_name
- country
- is_etf
- actively trading
- cik
---

<!-- markdownlint-disable MD041 -->

Equity Search. Search for a company or stock ticker.

## Syntax

```excel wordwrap
=OBB.EQUITY.SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: sec | True |
| query | Text | Search query. | True |
| is_symbol | Boolean | Whether to search by ticker symbol. | True |
| is_fund | Boolean | Whether to direct the search to the list of mutual funds and ETFs. (provider: sec) | True |
| use_cache | Boolean | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. (provider: sec) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the company.  |
| cik | Central Index Key (provider: sec) |
