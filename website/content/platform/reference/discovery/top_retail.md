---
title: top_retail
description: Learn about the OBB.equity.discovery.top_retail function in Python, which
  tracks retail activity and sentiment for over 9,500 US traded stocks, ADRs, and
  ETPs. Find out how to use the function's parameters and understand the data it returns.
keywords:
- retail activity
- sentiment
- top retail
- equity discovery
- US traded stocks
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Tracks over $30B USD/day of individual investors trades.

It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
ADRs, and ETPs.

```python wordwrap
obb.equity.discovery.top_retail(limit: int = 5, provider: Literal[str] = nasdaq)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | The number of data entries to return. | 5 | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[TopRetail]
        Serializable results.

    provider : Optional[Literal['nasdaq']]
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
| symbol | str | Symbol representing the entity requested in the data. |
| activity | float | Activity of the symbol. |
| sentiment | float | Sentiment of the symbol. 1 is bullish, -1 is bearish. |
</TabItem>

</Tabs>

