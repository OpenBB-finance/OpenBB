---
title: Share Statistics
description: This page provides detailed implementation methods for ShareStatistics.
  It includes parameters and data involved, such as symbol, provider, date, and shares
  data.
keywords:
- ShareStatistics
- symbol
- provider
- date
- free_float
- float_shares
- outstanding_shares
- source
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Share Statistics - Data_Models | OpenBB Platform Docs" />


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
from openbb_provider.standard_models.share_statistics import (
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
| symbol | str | Symbol to get data for. |
| date | date | A specific date to get data for. |
| free_float | float | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | float | Number of shares available for trading by the general public. |
| outstanding_shares | float | Total number of shares of a publicly-traded company. |
| source | str | Source of the received data. |
</TabItem>

</Tabs>
