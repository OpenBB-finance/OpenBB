---
title: "EU Yield Curve"
description: "Euro Area Yield Curve"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EUYieldCurve` | `EUYieldCurveQueryParams` | `EUYieldCurveData` |

### Import Statement

```python
from openbb_core.provider.standard_models.eu_yield_curve import (
EUYieldCurveData,
EUYieldCurveQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. | None | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. | None | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
| rating | Literal['aaa', 'all_ratings'] | The rating type, either 'aaa' or 'all_ratings'. | aaa | True |
| yield_curve_type | Literal['spot_rate', 'instantaneous_forward', 'par_yield'] | The yield curve type. | spot_rate | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | float | Maturity, in years. |
| rate | float | Yield curve rate, as a normalized percent. |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | float | Maturity, in years. |
| rate | float | Yield curve rate, as a normalized percent. |
</TabItem>

</Tabs>

