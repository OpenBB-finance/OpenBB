---
title: est
description: This page provides detailed parameters and data options for retrieving
  Analyst Estimates and stock recommendations using the est function. It further explains
  the returned objects including results, provider name, warnings, chart object, and
  metadata. The page also provides an enumeration of the estimated data types like
  revenue, EBITDA, net income amongst others that can be obtained.
keywords:
- Analyst Estimates
- stock recommendations
- analyst data
- data query
- financial market provider
- estimated revenue
- estimated EBITDA
- estimated net income
- estimated EPS
- fmp provider
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.est - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Analyst Estimates. Analyst stock recommendations.

```python wordwrap
est(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 30, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['quarter', 'annual'] | Period of the data to return. | annual | True |
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
| symbol | str | Symbol to get data for. |
| date | date | A specific date to get data for. |
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
