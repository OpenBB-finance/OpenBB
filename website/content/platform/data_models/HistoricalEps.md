---
title: HistoricalEps
description: Historical earnings-per-share for a given company
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalEps` | `HistoricalEpsQueryParams` | `HistoricalEpsData` |

### Import Statement

```python
from openbb_provider.standard_models.historical_eps import (
HistoricalEpsData,
HistoricalEpsQueryParams,
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

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| limit | int | The number of data entries to return. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
| actual_eps | float | The actual earnings per share announced. |
| revenue_estimated | float | Estimated consensus revenue for the reporting period. |
| actual_revenue | float | The actual reported revenue. |
| reporting_time | str | The reporting time - e.g. after market close. |
| updated_at | date | The date when the data was last updated. |
| period_ending | date | The fiscal period end date. |
</TabItem>

</Tabs>

