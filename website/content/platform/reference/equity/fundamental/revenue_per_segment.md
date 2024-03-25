---
title: "revenue_per_segment"
description: "Learn how to get revenue data for a specific business line using the  equity fundamental revenue per segment function."
keywords:
- Revenue Business Line
- business line revenue data
- equity fundamental revenue per segment
- symbol
- period
- structure
- provider
- results
- RevenueBusinessLine
- chart
- metadata
- data
- date
- business line
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/revenue_per_segment - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the revenue breakdown by business segment for a given company over time.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.revenue_per_segment(symbol='AAPL', provider='fmp')
obb.equity.fundamental.revenue_per_segment(symbol='AAPL', period='annual', structure='flat', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Time period of the data to return. | annual | True |
| structure | Literal['hierarchical', 'flat'] | Structure of the returned data. | flat | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Time period of the data to return. | annual | True |
| structure | Literal['hierarchical', 'flat'] | Structure of the returned data. | flat | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : RevenueBusinessLine
        Serializable results.
    provider : Literal['fmp']
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
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the reporting period. |
| fiscal_year | int | The fiscal year of the reporting period. |
| filing_date | date | The filing date of the report. |
| business_line | int | Dictionary containing the revenue of the business line. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the reporting period. |
| fiscal_year | int | The fiscal year of the reporting period. |
| filing_date | date | The filing date of the report. |
| business_line | int | Dictionary containing the revenue of the business line. |
</TabItem>

</Tabs>

