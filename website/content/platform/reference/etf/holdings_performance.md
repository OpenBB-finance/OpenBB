---
title: "holdings_performance"
description: "Get the ETF holdings performance using the `obb.etf.holdings_performance`  function in Python. This function returns a variety of performance metrics for ETF  holdings, including one-day return, week-to-date return, one-week return, month-to-date  return, and more. Analyze and chart the performance of ETF holdings with this comprehensive  function."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/holdings_performance - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the recent price performance of each ticker held in the ETF.


Examples
--------

```python
from openbb import obb
obb.etf.holdings_performance(symbol='XLK', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfHoldingsPerformance
        Serializable results.
    provider : Literal['fmp']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

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

