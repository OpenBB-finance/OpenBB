---
title: employee_count
description: Learn how to retrieve historical employee count data using the Python
  API. Understand the parameters, returns, and data structure for the OBB.equity.fundamental.employee_count
  method.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Employees. Historical number of employees.

```python wordwrap
obb.equity.fundamental.employee_count(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HistoricalEmployees]
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
| cik | int | CIK of the company to retrieve the historical employees of. |
| acceptance_time | datetime | Time of acceptance of the company employee. |
| period_of_report | date | Date of reporting of the company employee. |
| company_name | str | Registered name of the company to retrieve the historical employees of. |
| form_type | str | Form type of the company employee. |
| filing_date | date | Filing date of the company employee |
| employee_count | int | Count of employees of the company. |
| source | str | Source URL which retrieves this data for the company. |
</TabItem>

</Tabs>

