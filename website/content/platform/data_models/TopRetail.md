---
title: Tracks over $30B USD/day of individual investors trades
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TopRetail` | `TopRetailQueryParams` | `TopRetailData` |

### Import Statement

```python
from openbb_core.provider.standard_models.top_retail import (
TopRetailData,
TopRetailQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | The number of data entries to return. | 5 | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

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
