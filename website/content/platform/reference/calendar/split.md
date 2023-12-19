---
title: split
description: Learn how to use the `obb.equity.calendar.split` function to show stock
  split calendar data, including start and end dates, provider, results, warnings,
  chart, metadata, and information about the stock splits.
keywords:
- Calendar splits
- stock split calendar
- equity calendar split
- start date
- end date
- provider
- data
- results
- warnings
- chart
- metadata
- date
- label
- symbol
- numerator
- denominator
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calendar Splits. Show Stock Split Calendar.

```python wordwrap
obb.equity.calendar.split(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CalendarSplits]
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
| date | date | The date of the data. |
| label | str | Label of the stock splits. |
| symbol | str | Symbol representing the entity requested in the data. |
| numerator | float | Numerator of the stock splits. |
| denominator | float | Denominator of the stock splits. |
</TabItem>

</Tabs>

