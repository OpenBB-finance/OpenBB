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
=OBB.EQUITY.SEARCH([query];[is_symbol];[provider];[active];[limit];[is_fund];[use_cache])
```

### Example

```excel wordwrap
=OBB.EQUITY.SEARCH()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| query | Text | Search query. | False |
| is_symbol | Boolean | Whether to search by ticker symbol. | False |
| provider | Text | Options: intrinio, sec, defaults to intrinio. | False |
| active | Boolean | When true, return companies that are actively traded (having stock prices within the past 14 days). When false, return companies that are not actively traded or never have been traded. (provider: intrinio) | False |
| limit | Number | The number of data entries to return. (provider: intrinio) | False |
| is_fund | Boolean | Whether to direct the search to the list of mutual funds and ETFs. (provider: sec) | False |
| use_cache | Boolean | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. (provider: sec) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the company.  |
| cik | ;     Central Index Key (provider: sec) |
| lei | The Legal Entity Identifier (LEI) of the company. (provider: intrinio) |
| intrinio_id | The Intrinio ID of the company. (provider: intrinio) |
