---
title: projections
description: Browse through this comprehensive guide on federal funds rate projections
  inclusive of parameters, data, and returns. Useful commands and searches provided
  for providers such as 'fred'. Includes python wordwrap for ease. Get details on
  the target range, central tendencies and projection of rates.
keywords:
- projections
- federal funds rate
- target range
- python wordwrap
- parameters
- provider
- fred
- long_run
- returns
- OBBject results
- data
- date
- central tendency
- projection of rates
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.projections - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fed Funds Rate Projections.
    The projections for the federal funds rate are the value of the midpoint of the
    projected appropriate target range for the federal funds rate or the projected
    appropriate target level for the federal funds rate at the end of the specified
    calendar year or over the longer run.

```python wordwrap
projections(provider: Literal[str] = fred)
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
