---
title: Fed Funds Rate Projections
description: This page provides implementation details and descriptions of parameters
  and data for the PROJECTIONS feature on our website. Discover how to use queries
  using 'fred' as the provider, understand data projections, and get to grips with
  different types of rates.
keywords:
- projections
- implementation
- query parameters
- data class
- fred provider
- data projections
- high projection rates
- central tendency rates
- median projection rates
- midpoint projections
- low projection rates
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Fed Funds Rate Projections - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `PROJECTIONS` | `PROJECTIONSQueryParams` | `PROJECTIONSData` |

### Import Statement

```python
from openbb_provider.standard_models. import (
PROJECTIONSData,
PROJECTIONSQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| long_run | bool | Flag to show long run projections | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| range_high | float | High projection of rates. |
| central_tendency_high | float | Central tendency of high projection of rates. |
| median | float | Median projection of rates. |
| range_midpoint | float | Midpoint projection of rates. |
| central_tendency_midpoint | float | Central tendency of midpoint projection of rates. |
| range_low | float | Low projection of rates. |
| central_tendency_low | float | Central tendency of low projection of rates. |
</TabItem>

</Tabs>
