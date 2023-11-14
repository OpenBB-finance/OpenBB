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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Analyst Estimates. Analyst stock recommendations.

```python wordwrap
obb.equity.estimates.historical(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 30, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 30 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[AnalystEstimates]
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
| date | date | The date of the data. |
| estimated_revenue_low | int | Estimated revenue low. |
| estimated_revenue_high | int | Estimated revenue high. |
| estimated_revenue_avg | int | Estimated revenue average. |
| estimated_ebitda_low | int | Estimated EBITDA low. |
| estimated_ebitda_high | int | Estimated EBITDA high. |
| estimated_ebitda_avg | int | Estimated EBITDA average. |
| estimated_ebit_low | int | Estimated EBIT low. |
| estimated_ebit_high | int | Estimated EBIT high. |
| estimated_ebit_avg | int | Estimated EBIT average. |
| estimated_net_income_low | int | Estimated net income low. |
| estimated_net_income_high | int | Estimated net income high. |
| estimated_net_income_avg | int | Estimated net income average. |
| estimated_sga_expense_low | int | Estimated SGA expense low. |
| estimated_sga_expense_high | int | Estimated SGA expense high. |
| estimated_sga_expense_avg | int | Estimated SGA expense average. |
| estimated_eps_avg | float | Estimated EPS average. |
| estimated_eps_high | float | Estimated EPS high. |
| estimated_eps_low | float | Estimated EPS low. |
| number_analyst_estimated_revenue | int | Number of analysts who estimated revenue. |
| number_analysts_estimated_eps | int | Number of analysts who estimated EPS. |
</TabItem>

</Tabs>

