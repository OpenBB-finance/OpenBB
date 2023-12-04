---
title: info
description: Get an overview of ETF information using the `obb.etf.info` function.
  Learn about the available parameters, returns, and data fields like name, inception
  date, asset class, assets under management, average trading volume, CUSIP, description,
  domicile, expense ratio, ISIN, net asset value, website link, and holdings count.
keywords: 
- ETF Information Overview
- obb.etf.info
- parameters
- symbol
- provider
- returns
- data
- name
- inception date
- asset class
- assets under management
- average trading volume
- CUSIP
- description
- domicile
- expense ratio
- ISIN
- net asset value
- website link
- holdings count
---

<!-- markdownlint-disable MD041 -->

ETF Information Overview.

## Syntax

```excel wordwrap
=OBB.ETF.INFO(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. (ETF) | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (ETF)  |
| name | Name of the ETF.  |
| inception_date | Inception date of the ETF.  |
| asset_class | Asset class of the ETF. (provider: fmp) |
| aum | Assets under management. (provider: fmp) |
| avg_volume | Average trading volume of the ETF. (provider: fmp) |
| cusip | CUSIP of the ETF. (provider: fmp) |
| description | Description of the ETF. (provider: fmp) |
| domicile | Domicile of the ETF. (provider: fmp) |
| etf_company | Company of the ETF. (provider: fmp) |
| expense_ratio | Expense ratio of the ETF. (provider: fmp) |
| isin | ISIN of the ETF. (provider: fmp) |
| nav | Net asset value of the ETF. (provider: fmp) |
| nav_currency | Currency of the ETF's net asset value. (provider: fmp) |
| website | Website link of the ETF. (provider: fmp) |
| holdings_count | Number of holdings in the ETF. (provider: fmp) |
