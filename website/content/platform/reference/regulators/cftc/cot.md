---
title: "cot"
description: "Learn how to lookup Commitment of Traders Reports by series ID and view  the results, metadata, warnings, and charts associated with the reports. Understand  the available parameters such as default report, provider, data type, legacy format,  report type, measure, start date, end date, and transform."
keywords:
- Commitment of Traders Reports
- lookup
- series ID
- CFTC
- regulators
- default report
- provider
- data type
- legacy format
- report type
- measure
- start date
- end date
- transform
- results
- metadata
- warnings
- chart
- traders
- date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/cftc/cot - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Commitment of Traders Reports.


Examples
--------

```python
from openbb import obb
obb.regulators.cftc.cot(provider='nasdaq')
# Get the Commitment of Traders Report for Gold.
obb.regulators.cftc.cot(id='GC=F', provider='nasdaq')
# Enter the report ID by the Nasdaq Data Link Code.
obb.regulators.cftc.cot(id='088691', provider='nasdaq')
# Get the report for futures only.
obb.regulators.cftc.cot(id='088691', data_type=F, provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| id | str | The series ID string for the report. Default report is Two-Year Treasury Note Futures. | 042601 | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| id | str | The series ID string for the report. Default report is Two-Year Treasury Note Futures. | 042601 | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
| data_type | Literal['F', 'FO', 'CITS'] | The type of data to reuturn. Default is 'FO'.       F = Futures only       FO = Futures and Options       CITS = Commodity Index Trader Supplemental. Only valid for commodities. | FO | True |
| legacy_format | bool | Returns the legacy format of report. Default is False. | False | True |
| report_type | Literal['ALL', 'CHG', 'OLD', 'OTR'] | The type of report to return. Default is 'ALL'.       ALL = All       CHG = Change in Positions       OLD = Old Crop Years       OTR = Other Crop Years | ALL | True |
| measure | Literal['CR', 'NT', 'OI', 'CHG'] | The measure to return. Default is None.       CR = Concentration Ratios       NT = Number of Traders       OI = Percent of Open Interest       CHG = Change in Positions. Only valid when data_type is 'CITS'. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : COT
        Serializable results.
    provider : Literal['nasdaq']
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
| date | date | The date of the data. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>

