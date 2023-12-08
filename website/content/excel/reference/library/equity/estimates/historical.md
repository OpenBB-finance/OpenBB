---
title: historical
description: Learn about historical analyst estimates and analyst stock recommendations
  with the OBBPy library in Python. Explore the usage of the `obb.equity.estimates.historical`
  function and its parameters, including `symbol`, `period`, `limit`, and `provider`.
  Understand the structure of the returned object, `OBBject`, with `results`, `provider`,
  `warnings`, `chart`, and `metadata` properties. Dive into the available data such
  as `symbol`, `date`, `estimated revenue`, `ebitda`, `ebit`, `net income`, `SGA expense`,
  `EPS`, and the number of analysts who estimated revenue and EPS.
keywords: 
- historical analyst estimates
- analyst stock recommendations
- python obb.equity.estimates.historical
- parameters
- standard
- symbol
- union[str, list[str]]
- period
- literal['quarter', 'annual']
- limit
- int
- provider
- literal['fmp']
- returns
- obbject
- list[analystestimates]
- serializable results
- optional[literal['fmp']]
- optional[list[warning_]]
- optional[chart]
- optional[metadata]
- data
- symbol
- str
- date
- estimated revenue low
- estimated revenue high
- estimated revenue average
- estimated ebitda low
- estimated ebitda high
- estimated ebitda average
- estimated ebit low
- estimated ebit high
- estimated ebit average
- estimated net income low
- estimated net income high
- estimated net income average
- estimated sga expense low
- estimated sga expense high
- estimated sga expense average
- estimated eps average
- estimated eps high
- estimated eps low
- number of analysts who estimated revenue
- number of analysts who estimated eps
---

<!-- markdownlint-disable MD041 -->

Historical Analyst Estimates. Analyst stock recommendations.

## Syntax

```excel wordwrap
=OBB.EQUITY.ESTIMATES.HISTORICAL(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| estimated_revenue_low | Estimated revenue low.  |
| estimated_revenue_high | Estimated revenue high.  |
| estimated_revenue_avg | Estimated revenue average.  |
| estimated_ebitda_low | Estimated EBITDA low.  |
| estimated_ebitda_high | Estimated EBITDA high.  |
| estimated_ebitda_avg | Estimated EBITDA average.  |
| estimated_ebit_low | Estimated EBIT low.  |
| estimated_ebit_high | Estimated EBIT high.  |
| estimated_ebit_avg | Estimated EBIT average.  |
| estimated_net_income_low | Estimated net income low.  |
| estimated_net_income_high | Estimated net income high.  |
| estimated_net_income_avg | Estimated net income average.  |
| estimated_sga_expense_low | Estimated SGA expense low.  |
| estimated_sga_expense_high | Estimated SGA expense high.  |
| estimated_sga_expense_avg | Estimated SGA expense average.  |
| estimated_eps_avg | Estimated EPS average.  |
| estimated_eps_high | Estimated EPS high.  |
| estimated_eps_low | Estimated EPS low.  |
| number_analyst_estimated_revenue | Number of analysts who estimated revenue.  |
| number_analysts_estimated_eps | Number of analysts who estimated EPS.  |
