---
title: Stock Split Calendar
description: Documentation regarding StockSplitCalendarData, StockSplitCalendarQueryParams
  classes by openbb_provider. The page includes implementation details, parameters,
  data, and usage explanations for stock splits in Python.
keywords:
- StockSplitCalendar
- StockSplitCalendarQueryParams
- StockSplitCalendarData
- openbb_provider
- python
- class
- parameters
- data
- stock splits
- start_date
- end_date
- provider
- fmp
- date
- label
- symbol
- numerator
- denominator
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Stock Split Calendar - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockSplitCalendar` | `StockSplitCalendarQueryParams` | `StockSplitCalendarData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_splits import (
StockSplitCalendarData,
StockSplitCalendarQueryParams,
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
| date | date | Date of the stock splits. |
| label | str | Label of the stock splits. |
| symbol | str | Symbol of the company. |
| numerator | float | Numerator of the stock splits. |
| denominator | float | Denominator of the stock splits. |
</TabItem>

</Tabs>
