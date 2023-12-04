---
title: holdings
description: Learn how to get the holdings data for an individual ETF using the `obb.etf.holdings`
  method. Understand the parameters like symbol, provider, date, and CIK. Explore
  the returns, results, warnings, chart, and metadata. Dive into the data fields like
  symbol, name, LEI, title, CUSIP, ISIN, balance, units, currency, value, weight,
  payoff profile, asset category, issuer category, country, and more.
keywords: 
- ETF holdings
- individual ETF holdings
- holdings data for ETF
- symbol
- provider
- date
- CIK
- returns
- results
- warnings
- chart
- metadata
- data
- name
- LEI
- title
- CUSIP
- ISIN
- balance
- units
- currency
- value
- weight
- payoff profile
- asset category
- issuer category
- country
- is restricted
- fair value level
- is cash collateral
- is non-cash collateral
- is loan by fund
- acceptance datetime
---

<!-- markdownlint-disable MD041 -->

Get the holdings for an individual ETF.

## Syntax

```excel wordwrap
=OBB.ETF.HOLDINGS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. (ETF) | False |
| provider | Text | Options: fmp | True |
| date | Text | A specific date to get data for. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp) | True |
| cik | Text | The CIK of the filing entity. Overrides symbol. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (ETF)  |
| name | Name of the ETF holding.  |
| lei | The LEI of the holding. (provider: fmp) |
| title | The title of the holding. (provider: fmp) |
| cusip | The CUSIP of the holding. (provider: fmp) |
| isin | The ISIN of the holding. (provider: fmp) |
| balance | The balance of the holding. (provider: fmp) |
| units | The units of the holding. (provider: fmp) |
| currency | The currency of the holding. (provider: fmp) |
| value | The value of the holding in USD. (provider: fmp) |
| weight | The weight of the holding in ETF in %. (provider: fmp) |
| payoff_profile | The payoff profile of the holding. (provider: fmp) |
| asset_category | The asset category of the holding. (provider: fmp) |
| issuer_category | The issuer category of the holding. (provider: fmp) |
| country | The country of the holding. (provider: fmp) |
| is_restricted | Whether the holding is restricted. (provider: fmp) |
| fair_value_level | The fair value level of the holding. (provider: fmp) |
| is_cash_collateral | Whether the holding is cash collateral. (provider: fmp) |
| is_non_cash_collateral | Whether the holding is non-cash collateral. (provider: fmp) |
| is_loan_by_fund | Whether the holding is loan by fund. (provider: fmp) |
| cik | The CIK of the filing. (provider: fmp) |
| acceptance_datetime | The acceptance datetime of the filing. (provider: fmp) |
