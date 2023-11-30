<!-- markdownlint-disable MD041 -->

Get Executive Compensation. Information about the executive compensation for a given company.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.MANAGEMENT_COMPENSATION(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |

## Data

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
