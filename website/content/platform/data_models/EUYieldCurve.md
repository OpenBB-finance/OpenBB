---
title: Euro Area Yield Curve
description: OpenBB Platform Data Model
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

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | A specific date to get data for. | None | True |
| yield_curve_type | Literal['spot_rate', 'instantaneous_forward', 'par_yield'] | The yield curve type. | spot_rate | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | A specific date to get data for. | None | True |
| yield_curve_type | Literal['spot_rate', 'instantaneous_forward', 'par_yield'] | The yield curve type. | spot_rate | True |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
| rating | Literal['A', 'C'] | The rating type. | A | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | str | Yield curve rate maturity. |
| rate | float | Yield curve rate. |
</TabItem>

</Tabs>
