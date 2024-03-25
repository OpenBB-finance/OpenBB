---
title: "earnings"
description: "Learn how to retrieve upcoming and historical earnings calendar data  using the OBB.equity.calendar.earnings Python function. The function allows you  to specify symbols, limit the number of data entries, and choose a data provider.  The returned data includes EPS, revenue, and other important details for the specified  symbols and dates."
keywords:
- earnings calendar
- upcoming earnings
- historical earnings
- Python function
- earnings data retrieval
- symbol
- limit
- provider
- data entries
- chart
- metadata
- data
- EPS
- revenue
- estimated EPS
- estimated revenue
- date
- time
- updated from date
- fiscal date ending
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/calendar/earnings - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get historical and upcoming company earnings releases. Includes earnings per share (EPS) and revenue data.


Examples
--------

```python
from openbb import obb
obb.equity.calendar.earnings(provider='fmp')
# Get earnings calendar for specific dates.
obb.equity.calendar.earnings(start_date='2024-02-01', end_date='2024-02-07', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CalendarEarnings
        Serializable results.
    provider : Literal['fmp', 'nasdaq', 'tmx']
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
| report_date | date | The date of the earnings report. |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| eps_previous | float | The earnings-per-share from the same previously reported period. |
| eps_consensus | float | The analyst conesus earnings-per-share estimate. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| report_date | date | The date of the earnings report. |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| eps_previous | float | The earnings-per-share from the same previously reported period. |
| eps_consensus | float | The analyst conesus earnings-per-share estimate. |
| eps_actual | float | The actual earnings per share announced. |
| revenue_actual | float | The actual reported revenue. |
| revenue_consensus | float | The revenue forecast consensus. |
| period_ending | date | The fiscal period end date. |
| reporting_time | str | The reporting time - e.g. after market close. |
| updated_date | date | The date the data was updated last. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| report_date | date | The date of the earnings report. |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| eps_previous | float | The earnings-per-share from the same previously reported period. |
| eps_consensus | float | The analyst conesus earnings-per-share estimate. |
| eps_actual | float | The actual earnings per share (USD) announced. |
| surprise_percent | float | The earnings surprise as normalized percentage points. |
| num_estimates | int | The number of analysts providing estimates for the consensus. |
| period_ending | str | The fiscal period end date. |
| previous_report_date | date | The previous report date for the same period last year. |
| reporting_time | str | The reporting time - e.g. after market close. |
| market_cap | int | The market cap (USD) of the reporting entity. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| report_date | date | The date of the earnings report. |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| eps_previous | float | The earnings-per-share from the same previously reported period. |
| eps_consensus | float | The analyst conesus earnings-per-share estimate. |
| eps_actual | float | The actual EPS in dollars. |
| eps_surprise | float | The EPS surprise in dollars. |
| surprise_percent | float | The EPS surprise as a normalized percent. |
| reporting_time | str | The time of the report - i.e., before or after market. |
</TabItem>

</Tabs>

