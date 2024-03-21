---
title: "Price Performance"
description: "Price performance as a return, over different periods"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `PricePerformance` | `PricePerformanceQueryParams` | `PricePerformanceData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
PricePerformanceData,
PricePerformanceQueryParams,
)
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

