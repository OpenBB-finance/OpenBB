---
title: "Trailing Dividend Yield"
description: "Get the 1 year trailing dividend yield for a given company over time"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TrailingDividendYield` | `TrailingDividendYieldQueryParams` | `TrailingDividendYieldData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
TrailingDividendYieldData,
TrailingDividendYieldQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. Default is 252, the number of trading days in a year. | 252 | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. Default is 252, the number of trading days in a year. | 252 | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

<TabItem value='tiingo' label='tiingo'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

</Tabs>

