---
title: screener
description: Equity Screen
keywords: 
- equity
- screener
---

<!-- markdownlint-disable MD041 -->

Equity Screen. Screen for companies meeting various criteria.

## Syntax

```excel wordwrap
=OBB.EQUITY.SCREENER(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| mktcap_min | Number | Filter by market cap greater than this value. (provider: fmp) | True |
| mktcap_max | Number | Filter by market cap less than this value. (provider: fmp) | True |
| price_min | Number | Filter by price greater than this value. (provider: fmp) | True |
| price_max | Number | Filter by price less than this value. (provider: fmp) | True |
| beta_min | Number | Filter by a beta greater than this value. (provider: fmp) | True |
| beta_max | Number | Filter by a beta less than this value. (provider: fmp) | True |
| volume_min | Number | Filter by volume greater than this value. (provider: fmp) | True |
| volume_max | Number | Filter by volume less than this value. (provider: fmp) | True |
| dividend_min | Number | Filter by dividend amount greater than this value. (provider: fmp) | True |
| dividend_max | Number | Filter by dividend amount less than this value. (provider: fmp) | True |
| is_etf | Boolean | If true, returns only ETFs. (provider: fmp) | True |
| is_active | Boolean | If false, returns only inactive tickers. (provider: fmp) | True |
| sector | Text | Filter by sector. (provider: fmp) | True |
| industry | Text | Filter by industry. (provider: fmp) | True |
| country | Text | Filter by country, as a two-letter country code. (provider: fmp) | True |
| exchange | Text | Filter by exchange. (provider: fmp) | True |
| limit | Number | Limit the number of results to return. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the company.  |
| market_cap | The market cap of ticker. (provider: fmp) |
| sector | The sector the ticker belongs to. (provider: fmp) |
| industry | The industry ticker belongs to. (provider: fmp) |
| beta | The beta of the ETF. (provider: fmp) |
| price | The current price. (provider: fmp) |
| last_annual_dividend | The last annual amount dividend paid. (provider: fmp) |
| volume | The current trading volume. (provider: fmp) |
| exchange | The exchange code the asset trades on. (provider: fmp) |
| exchange_name | The full name of the primary exchange. (provider: fmp) |
| country | The two-letter country abbreviation where the head office is located. (provider: fmp) |
| is_etf | Whether the ticker is an ETF. (provider: fmp) |
| actively_trading | Whether the ETF is actively trading. (provider: fmp) |
