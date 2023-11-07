---
title: Historical Employees
description: Details on the implementation of HistoricalEmployees model including
  class names, parameters information (such as symbol, provider), and data information
  (like cik, acceptance_time, period_of_report, company_name, form_type, filing_date,
  employee_count and source).
keywords:
- HistoricalEmployees
- HistoricalEmployeesData
- HistoricalEmployeesQueryParams
- Parameters
- Data
- symbol
- provider
- cik
- acceptance_time
- period_of_report
- company_name
- form_type
- filing_date
- employee_count
- source
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Historical Employees - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalEmployees` | `HistoricalEmployeesQueryParams` | `HistoricalEmployeesData` |

### Import Statement

```python
from openbb_provider.standard_models.historical_employees import (
HistoricalEmployeesData,
HistoricalEmployeesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
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
