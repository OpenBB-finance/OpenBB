---
title: Dividend Calendar
description: This documentation page provides comprehensive details on the implementation,
  parameters and data for the DividendCalendar, DividendCalendarQueryParams, and DividendCalendarData
  models from the openbb_provider's Python standard models. It includes a detailed
  breakdown of parameter and data types such as start_date, end_date, provider, symbol,
  dates, and dividends.
keywords:
- DividendCalendar
- DividendCalendarQueryParams
- DividendCalendarData
- parameters
- data class
- Python
- openbb_provider
- dividend
- provider
- start_date
- end_date
- fmp
- symbol
- date
- label
- adj_dividend
- dividend
- record_date
- payment_date
- declaration_date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Dividend Calendar - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `DividendCalendar` | `DividendCalendarQueryParams` | `DividendCalendarData` |

### Import Statement

```python
from openbb_provider.standard_models.dividend_calendar import (
DividendCalendarData,
DividendCalendarQueryParams,
)
```

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
