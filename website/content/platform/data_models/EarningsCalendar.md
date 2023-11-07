---
title: Earnings Calendar
description: This page provides detailed implementation of a financial Earnings Calendar
  using the OpenBB Provider in Python. It covers model names, import statements, standard
  parameters, and data types including EPS, revenue, and fiscal dates.
keywords:
- Earnings Calendar
- OpenBB Provider
- Data Models
- Query Parameters
- Estimated Earnings
- Revenue
- EPS
- Fiscal Date
- Python
- Coding
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Earnings Calendar - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EarningsCalendar` | `EarningsCalendarQueryParams` | `EarningsCalendarData` |

### Import Statement

```python
from openbb_provider.standard_models.earnings_calendar import (
EarningsCalendarData,
EarningsCalendarQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 50 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | date | The date of the data. |
| eps | float | EPS of the earnings calendar. |
| eps_estimated | float | Estimated EPS of the earnings calendar. |
| time | str | Time of the earnings calendar. |
| revenue | float | Revenue of the earnings calendar. |
| revenue_estimated | float | Estimated revenue of the earnings calendar. |
| updated_from_date | date | Updated from date of the earnings calendar. |
| fiscal_date_ending | date | Fiscal date ending of the earnings calendar. |
</TabItem>

</Tabs>
