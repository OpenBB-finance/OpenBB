---
title: price_performance
description: Learn about price performance returns over different periods and how
  to retrieve data for a given symbol. Find out how to analyze the time series data,
  view the provider information, and access additional metadata and warnings.
keywords: 
- price performance
- return
- periods
- symbol
- data
- time series
- chart
- provider
- metadata
- warnings
- one-day return
- week to date return
- one-week return
- month to date return
- one-month return
- quarter to date return
- three-month return
- six-month return
- year to date return
- one-year return
- three-year return
- five-year return
- ten-year return
- max return
- ticker symbol
---

<!-- markdownlint-disable MD041 -->

Price performance as a return, over different periods.

## Syntax

```excel wordwrap
=OBB.ETF.PRICE_PERFORMANCE(required;[optional])
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
