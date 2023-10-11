---
title: US Yield Curve
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `USYieldCurve` | `USYieldCurveQueryParams` | `USYieldCurveData` |

### Import Statement

```python
from openbb_provider.standard_models.us_yield_curve import (
USYieldCurveData,
USYieldCurveQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date] | Date to get Yield Curve data.  Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | Union[bool] | Get inflation adjusted rates. | False | True |
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | float | Maturity of the treasury rate in years. |
| rate | float | Associated rate given in decimal form (0.05 is 5%) |
</TabItem>

</Tabs>

