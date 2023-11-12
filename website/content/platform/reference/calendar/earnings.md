---
title: earnings
description: Learn how to retrieve upcoming and historical earnings calendar data
  using the OBB.equity.calendar.earnings Python function. The function allows you
  to specify symbols, limit the number of data entries, and choose a data provider.
  The returned data includes EPS, revenue, and other important details for the specified
  symbols and dates.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Upcoming and Historical earnings calendar.

```python wordwrap
obb.equity.calendar.earnings(symbol: Union[str, List[str]], limit: int = 50, provider: Literal[str] = fmp)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[CalendarEarnings]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
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

