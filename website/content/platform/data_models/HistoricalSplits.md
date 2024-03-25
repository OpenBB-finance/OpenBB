---
title: "Historical Splits"
description: "Get historical stock splits for a given company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalSplits` | `HistoricalSplitsQueryParams` | `HistoricalSplitsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.historical_splits import (
HistoricalSplitsData,
HistoricalSplitsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| label | str | Label of the historical stock splits. |
| numerator | float | Numerator of the historical stock splits. |
| denominator | float | Denominator of the historical stock splits. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| label | str | Label of the historical stock splits. |
| numerator | float | Numerator of the historical stock splits. |
| denominator | float | Denominator of the historical stock splits. |
</TabItem>

</Tabs>

