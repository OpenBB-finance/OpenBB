---
title: "employee_count"
description: "Learn how to retrieve historical employee count data using the Python  API. Understand the parameters, returns, and data structure for the OBB.equity.fundamental.employee_count  method."
keywords:
- historical employees
- employee count
- Python API
- data retrieval
- symbol
- provider
- warnings
- chart object
- metadata
- data
- CIK
- acceptance time
- period of report
- company name
- form type
- filing date
- source URL
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/employee_count - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get historical employee count data for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.employee_count(symbol='AAPL', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : HistoricalEmployees
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
| symbol | str | Symbol representing the entity requested in the data. |
| cik | int | Central Index Key (CIK) for the requested entity. |
| acceptance_time | datetime | Time of acceptance of the company employee. |
| period_of_report | date | Date of reporting of the company employee. |
| company_name | str | Registered name of the company to retrieve the historical employees of. |
| form_type | str | Form type of the company employee. |
| filing_date | date | Filing date of the company employee |
| employee_count | int | Count of employees of the company. |
| source | str | Source URL which retrieves this data for the company. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | int | Central Index Key (CIK) for the requested entity. |
| acceptance_time | datetime | Time of acceptance of the company employee. |
| period_of_report | date | Date of reporting of the company employee. |
| company_name | str | Registered name of the company to retrieve the historical employees of. |
| form_type | str | Form type of the company employee. |
| filing_date | date | Filing date of the company employee |
| employee_count | int | Count of employees of the company. |
| source | str | Source URL which retrieves this data for the company. |
</TabItem>

</Tabs>

