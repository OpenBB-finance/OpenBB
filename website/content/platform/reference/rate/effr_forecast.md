---
title: effr_forecast
description: Learn about the Fed Funds Rate Projections, the target range and level
  for the federal funds rate, and query parameters for retrieving the data. Explore
  the returns and data available for analysis and decision-making.
keywords:
- Fed Funds Rate Projections
- federal funds rate
- target range
- target level
- calendar year
- long run
- query parameters
- returns
- data
---




<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fed Funds Rate Projections.

The projections for the federal funds rate are the value of the midpoint of the
projected appropriate target range for the federal funds rate or the projected
appropriate target level for the federal funds rate at the end of the specified
calendar year or over the longer run.

```python wordwrap
obb.fixedincome.rate.effr_forecast(provider: Literal[str] = fred)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[PROJECTIONS]
        Serializable results.

    provider : Optional[Literal['fred']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

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

