---
title: "revenue_per_geography"
description: "Learn about the revenue per geography data with the geographic revenue  data Python function in this documentation page. Understand the symbol, period,  structure, and provider parameters. Explore the returns, results, metadata, and  the data structure including the date, geographic segment, and revenue by region  (Americas, Europe, Greater China, Japan, Rest of Asia Pacific)."
keywords:
- geographic revenue data
- revenue per geography
- Python function
- documentation page
- symbol parameter
- period parameter
- structure parameter
- provider parameter
- returns
- results
- metadata
- data
- date
- geographic segment
- Americas
- Europe
- Greater China
- Japan
- Rest of Asia Pacific
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/revenue_per_geography - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the revenue geographic breakdown for a given company over time.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.revenue_per_geography(symbol='AAPL', provider='fmp')
obb.equity.fundamental.revenue_per_geography(symbol='AAPL', period='annual', structure='flat', provider='fmp')
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
    results : RevenueGeographic
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
| geographic_segment | int | Dictionary of the revenue by geographic segment. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the reporting period. |
| fiscal_year | int | The fiscal year of the reporting period. |
| filing_date | date | The filing date of the report. |
| geographic_segment | int | Dictionary of the revenue by geographic segment. |
</TabItem>

</Tabs>

