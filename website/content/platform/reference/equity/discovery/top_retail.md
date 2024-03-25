---
title: "top_retail"
description: "Learn about the OBB.equity.discovery.top_retail function in Python, which  tracks retail activity and sentiment for over 9,500 US traded stocks, ADRs, and  ETPs. Find out how to use the function's parameters and understand the data it returns."
keywords:
- retail activity
- sentiment
- top retail
- equity discovery
- US traded stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/discovery/top_retail - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Tracks over $30B USD/day of individual investors trades.

It gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
ADRs, and ETPs.


Examples
--------

```python
from openbb import obb
obb.equity.discovery.top_retail(provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | The number of data entries to return. | 5 | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

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
    results : TopRetail
        Serializable results.
    provider : Literal['nasdaq']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| activity | float | Activity of the symbol. |
| sentiment | float | Sentiment of the symbol. 1 is bullish, -1 is bearish. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| activity | float | Activity of the symbol. |
| sentiment | float | Sentiment of the symbol. 1 is bullish, -1 is bearish. |
</TabItem>

</Tabs>

