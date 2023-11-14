---
title: revenue_per_segment
description: Learn how to get revenue data for a specific business line using the
  equity fundamental revenue per segment function.
keywords:
- Revenue Business Line
- business line revenue data
- equity fundamental revenue per segment
- symbol
- period
- structure
- provider
- results
- RevenueBusinessLine
- chart
- metadata
- data
- date
- business line
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Revenue Business Line. Business line revenue data.

```python wordwrap
obb.equity.fundamental.revenue_per_segment(symbol: Union[str, List[str]], period: Literal[str] = annual, structure: Literal[str] = flat, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Time period of the data to return. | annual | True |
| structure | Literal['hierarchical', 'flat'] | Structure of the returned data. | flat | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[RevenueBusinessLine]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| business_line | Dict[str, int] | Day level data containing the revenue of the business line. |
</TabItem>

</Tabs>

