---
title: Commitment of Traders Reports
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
| `COT` | `COTQueryParams` | `COTData` |

### Import Statement

```python
from openbb_core.provider.standard_models.cot import (
COTData,
COTQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| id | str | The series ID string for the report. Default report is Two-Year Treasury Note Futures. | 042601 | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| id | str | The series ID string for the report. Default report is Two-Year Treasury Note Futures. | 042601 | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
| data_type | Literal['F', 'FO', 'CITS'] |
            The type of data to reuturn. Default is "FO".

            F = Futures only

            FO = Futures and Options

            CITS = Commodity Index Trader Supplemental. Only valid for commodities.
             | FO | True |
| legacy_format | bool | Returns the legacy format of report. Default is False. | False | True |
| report_type | Literal['ALL', 'CHG', 'OLD', 'OTR'] |
            The type of report to return. Default is "ALL".

            ALL = All

            CHG = Change in Positions

            OLD = Old Crop Years

            OTR = Other Crop Years
             | ALL | True |
| measure | Literal['CR', 'NT', 'OI', 'CHG'] |
            The measure to return. Default is None.

            CR = Concentration Ratios

            NT = Number of Traders

            OI = Percent of Open Interest

            CHG = Change in Positions. Only valid when data_type is "CITS".
             | None | True |
| start_date | date | The start date of the time series. Defaults to all. | None | True |
| end_date | date | The end date of the time series. Defaults to the most recent data. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as w/w difference, percent change, cumulative, or normalize. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>
