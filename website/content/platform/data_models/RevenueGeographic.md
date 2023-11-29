---
title: Revenue Geographic
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
| `RevenueGeographic` | `RevenueGeographicQueryParams` | `RevenueGeographicData` |

### Import Statement

```python
from openbb_core.provider.standard_models.revenue_geographic import (
RevenueGeographicData,
RevenueGeographicQueryParams,
)
```

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
