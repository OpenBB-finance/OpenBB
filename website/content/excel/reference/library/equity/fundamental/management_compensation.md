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

<!-- markdownlint-disable MD041 -->

Get Executive Compensation. Information about the executive compensation for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.MANAGEMENT_COMPENSATION(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| filing_date | Date of the filing.  |
| accepted_date | Date the filing was accepted.  |
| name_and_position | Name and position of the executive.  |
| year | Year of the compensation.  |
| salary | Salary of the executive.  |
| bonus | Bonus of the executive.  |
| stock_award | Stock award of the executive.  |
| incentive_plan_compensation | Incentive plan compensation of the executive.  |
| all_other_compensation | All other compensation of the executive.  |
| total | Total compensation of the executive.  |
| url | URL of the filing data.  |
