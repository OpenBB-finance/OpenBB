---
title: US Yield Curve
description: This page provides detailed implementation information for the USYieldCurve
  model, including parameters, data class, and import statements. It primarily explores
  the use of the 'fred' provider, the maturity and rate of the treasury, and getting
  inflation-adjusted rates.
keywords:
- USYieldCurve
- USYieldCurveData
- USYieldCurveQueryParams
- Parameters
- Data
- fred
- inflation adjusted rates
- maturity
- treasury rate
- maturity of the treasury rate
- associated rate
- Implementation details
- model name
- parameters class
- data class
- import statement
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="US Yield Curve - Data_Models | OpenBB Platform Docs" />


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
| date | date | Date to get Yield Curve data.  Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | bool | Get inflation adjusted rates. | False | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
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
