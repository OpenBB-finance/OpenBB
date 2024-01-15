---
title: SCREENER
description: Equity Screen
keywords: 
- equity
- screener
---

<!-- markdownlint-disable MD041 -->

Equity Screen. Screen for companies meeting various criteria.

## Syntax

```excel wordwrap
=OBB.EQUITY.SCREENER([provider];[mktcap_min];[mktcap_max];[price_min];[price_max];[beta_min];[beta_max];[volume_min];[volume_max];[dividend_min];[dividend_max];[is_etf];[is_active];[sector];[industry];[country];[exchange];[limit])
```

### Example

```excel wordwrap
=OBB.EQUITY.SCREENER()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, defaults to fmp. | False |
| mktcap_min | Number | Filter by market cap greater than this value. (provider: fmp) | False |
| mktcap_max | Number | Filter by market cap less than this value. (provider: fmp) | False |
| price_min | Number | Filter by price greater than this value. (provider: fmp) | False |
| price_max | Number | Filter by price less than this value. (provider: fmp) | False |
| beta_min | Number | Filter by a beta greater than this value. (provider: fmp) | False |
| beta_max | Number | Filter by a beta less than this value. (provider: fmp) | False |
| volume_min | Number | Filter by volume greater than this value. (provider: fmp) | False |
| volume_max | Number | Filter by volume less than this value. (provider: fmp) | False |
| dividend_min | Number | Filter by dividend amount greater than this value. (provider: fmp) | False |
| dividend_max | Number | Filter by dividend amount less than this value. (provider: fmp) | False |
| is_etf | Boolean | If true, returns only ETFs. (provider: fmp) | False |
| is_active | Boolean | If false, returns only inactive tickers. (provider: fmp) | False |
| sector | Text | Filter by sector. (provider: fmp) | False |
| industry | Text | Filter by industry. (provider: fmp) | False |
| country | Text | Filter by country, as a two-letter country code. (provider: fmp) | False |
| exchange | Text | Filter by exchange. (provider: fmp) | False |
| limit | Number | Limit the number of results to return. (provider: fmp) | False |

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
