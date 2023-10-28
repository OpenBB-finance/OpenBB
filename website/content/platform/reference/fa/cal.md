---
title: cal
description: This is a guide to using the 'cal' function to display a dividend calendar
  between a range of start and end dates. It provides full details of parameters,
  return values, and data labels.
keywords:
- Dividend calendar
- Cal Function
- Python
- Data
- Start date
- End date
- Provider
- Results
- Chart
- Metadata
- Symbol
- Adjusted Dividend
- Dividend amount
- Record date
- Payment date
- Declaration date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="cal - Fa - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cal

Dividend Calendar. Show Dividend Calendar for a given start and end dates.

```python wordwrap
cal(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
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
    results : List[DividendCalendar]
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
| symbol | str | Symbol to get data for. |
| date | date | The date of the data. |
| label | str | Date in human readable form in the calendar. |
| adj_dividend | float | Adjusted dividend on a date in the calendar. |
| dividend | float | Dividend amount in the calendar. |
| record_date | date | Record date of the dividend in the calendar. |
| payment_date | date | Payment date of the dividend in the calendar. |
| declaration_date | date | Declaration date of the dividend in the calendar. |
</TabItem>

</Tabs>
