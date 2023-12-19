---
title: Get reported Fail-to-deliver (FTD) data
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
| `ShortVolume` | `ShortVolumeQueryParams` | `ShortVolumeData` |

### Import Statement

```python
from openbb_core.provider.standard_models.short_volume import (
ShortVolumeData,
ShortVolumeQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['stockgrid'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'stockgrid' if there is no default. | stockgrid | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| market | str | Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF |
| short_volume | int | Aggregate reported share volume of executed short sale and short sale exempt trades during regular trading hours |
| short_exempt_volume | int | Aggregate reported share volume of executed short sale exempt trades during regular trading hours |
| total_volume | int | Aggregate reported share volume of executed trades during regular trading hours |
</TabItem>

<TabItem value='stockgrid' label='stockgrid'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| market | str | Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF |
| short_volume | int | Aggregate reported share volume of executed short sale and short sale exempt trades during regular trading hours |
| short_exempt_volume | int | Aggregate reported share volume of executed short sale exempt trades during regular trading hours |
| total_volume | int | Aggregate reported share volume of executed trades during regular trading hours |
| close | float | Closing price of the stock on the date. |
| short_volume_percent | float | Percentage of the total volume that was short volume. |
</TabItem>

</Tabs>
