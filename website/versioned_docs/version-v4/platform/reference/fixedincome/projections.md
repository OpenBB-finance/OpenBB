---
title: projections
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# projections

Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

```python wordwrap
projections(provider: Union[Literal[str]] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| long_run | bool | Flag to show long run projections | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[PROJECTIONS]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fred'], NoneType]]
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
| range_high | Union[float] | High projection of rates. |
| central_tendency_high | Union[float] | Central tendency of high projection of rates. |
| median | Union[float] | Median projection of rates. |
| range_midpoint | Union[float] | Midpoint projection of rates. |
| central_tendency_midpoint | Union[float] | Central tendency of midpoint projection of rates. |
| range_low | Union[float] | Low projection of rates. |
| central_tendency_low | Union[float] | Central tendency of low projection of rates. |
</TabItem>

</Tabs>

