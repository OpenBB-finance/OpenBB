---
title: search
description: Learn how to search for ETFs with parameters like query, provider, exchange
  code, and more. Retrieve key details about ETFs, including market cap, industry,
  sector, beta, current price, annual dividend, trading volume, exchange, and country.
  Find actively trading ETFs and their symbol representation.
keywords: 
- search for ETFs
- ETF search query
- ETF provider
- ETF exchange code
- ETF trading volume
- ETF market cap
- ETF sector
- ETF industry
- ETF beta
- ETF current price
- ETF annual dividend
- ETF exchange
- ETF country
- actively trading ETF
---

<!-- markdownlint-disable MD041 -->

Search for ETFs.  An empty query returns the full list of ETFs from the provider.

## Syntax

```excel wordwrap
=OBB.ETF.SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| query | Text | Search query. | True |
| exchange | Text | The exchange code the ETF trades on. (provider: fmp) | True |
| is_active | Boolean | Whether the ETF is actively trading. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.(ETF)  |
| name | Name of the ETF.  |
| market_cap | The market cap of the ETF. (provider: fmp) |
| sector | The sector of the ETF. (provider: fmp) |
| industry | The industry of the ETF. (provider: fmp) |
| beta | The beta of the ETF. (provider: fmp) |
| price | The current price of the ETF. (provider: fmp) |
| last_annual_dividend | The last annual dividend paid. (provider: fmp) |
| volume | The current trading volume of the ETF. (provider: fmp) |
| exchange | The exchange code the ETF trades on. (provider: fmp) |
| exchange_name | The full name of the exchange the ETF trades on. (provider: fmp) |
| country | The country the ETF is registered in. (provider: fmp) |
| actively_trading | Whether the ETF is actively trading. (provider: fmp) |
