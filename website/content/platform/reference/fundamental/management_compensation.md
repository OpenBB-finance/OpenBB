---
title: management_compensation
description: Learn how to retrieve executive compensation data for a company using
  the equity management compensation function in Python. Understand the parameters,
  return values, and available data fields such as symbol, salary, bonus, stock award,
  and more.
keywords:
- executive compensation
- company executive compensation
- equity management compensation
- symbol parameter
- provider parameter
- return values
- data
- symbol
- cik
- filing date
- accepted date
- name and position
- year of compensation
- salary
- bonus
- stock award
- incentive plan compensation
- all other compensation
- total compensation
- URL
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Executive Compensation. Information about the executive compensation for a given company.

```python wordwrap
obb.equity.fundamental.management_compensation(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
    results : List[ExecutiveCompensation]
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

