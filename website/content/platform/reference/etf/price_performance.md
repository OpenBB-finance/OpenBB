---
title: "price_performance"
description: "Learn about price performance returns over different periods and how  to retrieve data for a given symbol. Find out how to analyze the time series data,  view the provider information, and access additional metadata and warnings."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/price_performance - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Price performance as a return, over different periods. This is a proxy for `equity.price.performance`.


Examples
--------

```python
from openbb import obb
obb.etf.price_performance(symbol='QQQ', provider='fmp')
obb.etf.price_performance(symbol='SPY,QQQ,IWM,DJIA', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp. |  | False |
| provider | Literal['finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp. |  | False |
| provider | Literal['finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp. |  | False |
| provider | Literal['finviz', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : PricePerformance
        Serializable results.
    provider : Literal['finviz', 'fmp']
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

<TabItem value='finviz' label='finviz'>

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
| volatility_week | float | One-week realized volatility, as a normalized percent. |
| volatility_month | float | One-month realized volatility, as a normalized percent. |
| price | float | Last Price. |
| volume | float | Current volume. |
| average_volume | float | Average daily volume. |
| relative_volume | float | Relative volume as a ratio of current volume to average volume. |
| analyst_recommendation | float | The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell. |
| symbol | str | The ticker symbol. |
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

