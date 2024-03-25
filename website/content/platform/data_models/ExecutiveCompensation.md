---
title: "Executive Compensation"
description: "Get executive management team compensation for a given company over time"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ExecutiveCompensation` | `ExecutiveCompensationQueryParams` | `ExecutiveCompensationData` |

### Import Statement

```python
from openbb_core.provider.standard_models.executive_compensation import (
ExecutiveCompensationData,
ExecutiveCompensationQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fmp. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fmp. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
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
| cik | str | Central Index Key (CIK) for the requested entity. |
| filing_date | date | Date of the filing. |
| accepted_date | datetime | Date the filing was accepted. |
| name_and_position | str | Name and position of the executive. |
| year | int | Year of the compensation. |
| salary | float | Salary of the executive. |
| bonus | float | Bonus of the executive. |
| stock_award | float | Stock award of the executive. |
| incentive_plan_compensation | float | Incentive plan compensation of the executive. |
| all_other_compensation | float | All other compensation of the executive. |
| total | float | Total compensation of the executive. |
| url | str | URL of the filing data. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| filing_date | date | Date of the filing. |
| accepted_date | datetime | Date the filing was accepted. |
| name_and_position | str | Name and position of the executive. |
| year | int | Year of the compensation. |
| salary | float | Salary of the executive. |
| bonus | float | Bonus of the executive. |
| stock_award | float | Stock award of the executive. |
| incentive_plan_compensation | float | Incentive plan compensation of the executive. |
| all_other_compensation | float | All other compensation of the executive. |
| total | float | Total compensation of the executive. |
| url | str | URL of the filing data. |
</TabItem>

</Tabs>

