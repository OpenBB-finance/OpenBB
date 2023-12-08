---
title: holdings_performance
description: Get the ETF holdings performance using the `obb.etf.holdings_performance`
  function in Python. This function returns a variety of performance metrics for ETF
  holdings, including one-day return, week-to-date return, one-week return, month-to-date
  return, and more. Analyze and chart the performance of ETF holdings with this comprehensive
  function.
keywords: 
- ETF holdings performance
- etf holdings performance python
- etf holdings performance function
- etf performance data
- etf returns
- etf performance metrics
- etf performance analysis
- etf performance statistics
- etf performance calculation
- etf performance chart
---

<!-- markdownlint-disable MD041 -->

Get the ETF holdings performance.

## Syntax

```excel wordwrap
=OBB.ETF.HOLDINGS_PERFORMANCE(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| one_day | One-day return.  |
| wtd | Week to date return.  |
| one_week | One-week return.  |
| mtd | Month to date return.  |
| one_month | One-month return.  |
| qtd | Quarter to date return.  |
| three_month | Three-month return.  |
| six_month | Six-month return.  |
| ytd | Year to date return.  |
| one_year | One-year return.  |
| three_year | Three-year return.  |
| five_year | Five-year return.  |
| ten_year | Ten-year return.  |
| max | Return from the beginning of the time series.  |
| symbol | The ticker symbol. (provider: fmp) |
