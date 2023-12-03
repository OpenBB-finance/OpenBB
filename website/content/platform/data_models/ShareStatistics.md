---
title: Share Statistics
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
| `ShareStatistics` | `ShareStatisticsQueryParams` | `ShareStatisticsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.share_statistics import (
ShareStatisticsData,
ShareStatisticsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

</Tabs>
