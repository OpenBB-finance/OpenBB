---
title: Income Statement Growth
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
| `IncomeStatementGrowth` | `IncomeStatementGrowthQueryParams` | `IncomeStatementGrowthData` |

### Import Statement

```python
from openbb_core.provider.standard_models.income_statement_growth import (
IncomeStatementGrowthData,
IncomeStatementGrowthQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 10 | True |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Period the statement is returned for. |
| growth_revenue | float | Growth rate of total revenue. |
| growth_cost_of_revenue | float | Growth rate of cost of goods sold. |
| growth_gross_profit | float | Growth rate of gross profit. |
| growth_gross_profit_ratio | float | Growth rate of gross profit as a percentage of revenue. |
| growth_research_and_development_expenses | float | Growth rate of expenses on research and development. |
| growth_general_and_administrative_expenses | float | Growth rate of general and administrative expenses. |
| growth_selling_and_marketing_expenses | float | Growth rate of expenses on selling and marketing activities. |
| growth_other_expenses | float | Growth rate of other operating expenses. |
| growth_operating_expenses | float | Growth rate of total operating expenses. |
| growth_cost_and_expenses | float | Growth rate of total costs and expenses. |
| growth_interest_expense | float | Growth rate of interest expenses. |
| growth_depreciation_and_amortization | float | Growth rate of depreciation and amortization expenses. |
| growth_ebitda | float | Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization. |
| growth_ebitda_ratio | float | Growth rate of EBITDA as a percentage of revenue. |
| growth_operating_income | float | Growth rate of operating income. |
| growth_operating_income_ratio | float | Growth rate of operating income as a percentage of revenue. |
| growth_total_other_income_expenses_net | float | Growth rate of net total other income and expenses. |
| growth_income_before_tax | float | Growth rate of income before taxes. |
| growth_income_before_tax_ratio | float | Growth rate of income before taxes as a percentage of revenue. |
| growth_income_tax_expense | float | Growth rate of income tax expenses. |
| growth_net_income | float | Growth rate of net income. |
| growth_net_income_ratio | float | Growth rate of net income as a percentage of revenue. |
| growth_eps | float | Growth rate of Earnings Per Share (EPS). |
| growth_eps_diluted | float | Growth rate of diluted Earnings Per Share (EPS). |
| growth_weighted_average_shs_out | float | Growth rate of weighted average shares outstanding. |
| growth_weighted_average_shs_out_dil | float | Growth rate of diluted weighted average shares outstanding. |
</TabItem>

</Tabs>
