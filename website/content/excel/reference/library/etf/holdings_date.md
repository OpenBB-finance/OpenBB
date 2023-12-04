---
title: holdings_date
description: Learn how to retrieve the holdings filing date for an individual ETF
  using the OBB.etf.holdings_date API. Explore the available parameters, such as symbol
  and provider, and understand the returned results like results list, chart object,
  and metadata info.
keywords: 
- ETF holdings filing date
- get ETF holdings filing date
- ETF holdings date API
- symbol parameter
- provider parameter
- fmp provider
- cik parameter
- returns
- results
- warnings
- chart object
- metadata info
- data parameter
- date field
---

<!-- markdownlint-disable MD041 -->

Get the holdings filing date for an individual ETF.

## Syntax

```excel wordwrap
=OBB.ETF.HOLDINGS_DATE(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. (ETF) | False |
| provider | Text | Options: fmp | True |
| cik | Text | The CIK of the filing entity. Overrides symbol. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
