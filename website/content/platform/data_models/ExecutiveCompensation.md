---
title: Get Executive Compensation
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
| `ExecutiveCompensation` | `ExecutiveCompensationQueryParams` | `ExecutiveCompensationData` |

### Import Statement

```python
from openbb_core.provider.standard_models.executive_compensation import (
ExecutiveCompensationData,
ExecutiveCompensationQueryParams,
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
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) of the company. |
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
