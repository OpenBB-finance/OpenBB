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



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the ETF holdings performance.

```python wordwrap
obb.etf.holdings_performance(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EtfHoldingsPerformance]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| one_day | float | One-day return. |
| wtd | float | Week to date return. |
| one_week | float | One-week return. |
| mtd | float | Month to date return. |
| one_month | float | One-month return. |
| qtd | float | Quarter to date return. |
| three_month | float | Three-month return. |
| six_month | float | Six-month return. |
| ytd | float | Year to date return. |
| one_year | float | One-year return. |
| three_year | float | Three-year return. |
| five_year | float | Five-year return. |
| ten_year | float | Ten-year return. |
| max | float | Return from the beginning of the time series. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| one_day | float | One-day return. |
| wtd | float | Week to date return. |
| one_week | float | One-week return. |
| mtd | float | Month to date return. |
| one_month | float | One-month return. |
| qtd | float | Quarter to date return. |
| three_month | float | Three-month return. |
| six_month | float | Six-month return. |
| ytd | float | Year to date return. |
| one_year | float | One-year return. |
| three_year | float | Three-year return. |
| five_year | float | Five-year return. |
| ten_year | float | Ten-year return. |
| max | float | Return from the beginning of the time series. |
| symbol | str | The ticker symbol. |
</TabItem>

</Tabs>

