---
title: dividends
description: Get historical dividends data for a given company with the OBB.equity.fundamental.dividends
  function. Explore parameters like symbol and provider, and understand the returned
  results, warnings, and metadata. View the data fields, including date, label, adj_dividend,
  dividend, record_date, payment_date, and declaration_date.
keywords: 
- historical dividends
- dividends data
- company dividends
- symbol
- data provider
- default provider
- results
- warnings
- chart
- metadata
- date
- label
- adj_dividend
- dividend
- record_date
- payment_date
- declaration_date
---

<!-- markdownlint-disable MD041 -->

Historical Dividends. Historical dividends data for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.DIVIDENDS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio | True |
| page_size | Number | The number of data entries to return. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| dividend | Dividend of the historical dividends.  |
| label | Label of the historical dividends. (provider: fmp) |
| adj_dividend | Adjusted dividend of the historical dividends. (provider: fmp) |
| record_date | Record date of the historical dividends. (provider: fmp) |
| payment_date | Payment date of the historical dividends. (provider: fmp) |
| declaration_date | Declaration date of the historical dividends. (provider: fmp) |
| factor | factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. (provider: intrinio) |
| dividend_currency | The currency of the dividend. (provider: intrinio) |
| split_ratio | The ratio of the stock split, if a stock split occurred. (provider: intrinio) |
