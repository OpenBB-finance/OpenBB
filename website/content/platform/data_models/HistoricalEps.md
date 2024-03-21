---
title: "Historical Eps"
description: "Get historical earnings per share data for a given company"
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
from openbb_core.provider.standard_models.historical_eps import (
HistoricalEpsData,
HistoricalEpsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage. |  | False |
| provider | Literal['alpha_vantage', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage. |  | False |
| provider | Literal['alpha_vantage', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | quarter | True |
| limit | int | The number of data entries to return. | None | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): alpha_vantage. |  | False |
| provider | Literal['alpha_vantage', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'alpha_vantage' if there is no default. | alpha_vantage | True |
| limit | int | The number of data entries to return. | None | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
</TabItem>

<TabItem value='alpha_vantage' label='alpha_vantage'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
| surprise | float | Surprise in EPS (Actual - Estimated). |
| surprise_percent | Union[float, str] | EPS surprise as a normalized percent. |
| reported_date | date | Date of the earnings report. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| announce_time | str | Timing of the earnings announcement. |
| eps_actual | float | Actual EPS from the earnings date. |
| eps_estimated | float | Estimated EPS for the earnings date. |
| revenue_estimated | float | Estimated consensus revenue for the reporting period. |
| revenue_actual | float | The actual reported revenue. |
| reporting_time | str | The reporting time - e.g. after market close. |
| updated_at | date | The date when the data was last updated. |
| period_ending | date | The fiscal period end date. |
</TabItem>

</Tabs>

