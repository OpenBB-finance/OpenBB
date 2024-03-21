---
title: "Historical Employees"
description: "Get historical employee count data for a given company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models.historical_employees import (
HistoricalEmployeesData,
HistoricalEmployeesQueryParams,
)
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

