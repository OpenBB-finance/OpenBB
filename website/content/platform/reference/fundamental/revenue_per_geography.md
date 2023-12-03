---
title: revenue_per_geography
description: Learn about the revenue per geography data with the geographic revenue
  data Python function in this documentation page. Understand the symbol, period,
  structure, and provider parameters. Explore the returns, results, metadata, and
  the data structure including the date, geographic segment, and revenue by region
  (Americas, Europe, Greater China, Japan, Rest of Asia Pacific).
keywords:
- geographic revenue data
- revenue per geography
- Python function
- documentation page
- symbol parameter
- period parameter
- structure parameter
- provider parameter
- returns
- results
- metadata
- data
- date
- geographic segment
- Americas
- Europe
- Greater China
- Japan
- Rest of Asia Pacific
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Revenue Geographic. Geographic revenue data.

```python wordwrap
obb.equity.fundamental.revenue_per_geography(symbol: Union[str, List[str]], period: Literal[str] = annual, structure: Literal[str] = flat, provider: Literal[str] = fmp)
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
    results : List[RevenueGeographic]
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
| geographic_segment | Dict[str, int] | Day level data containing the revenue of the geographic segment. |
| americas | int | Revenue from the American segment. |
| europe | int | Revenue from the European segment. |
| greater_china | int | Revenue from the Greater China segment. |
| japan | int | Revenue from the Japan segment. |
| rest_of_asia_pacific | int | Revenue from the Rest of Asia Pacific segment. |
</TabItem>

</Tabs>

