---
title: "management_compensation"
description: "Learn how to retrieve executive compensation data for a company using  the equity management compensation function in Python. Understand the parameters,  return values, and available data fields such as symbol, salary, bonus, stock award,  and more."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/management_compensation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get executive management team compensation for a given company over time.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.management_compensation(symbol='AAPL', provider='fmp')
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

## Returns

```python wordwrap
OBBject
    results : ExecutiveCompensation
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

