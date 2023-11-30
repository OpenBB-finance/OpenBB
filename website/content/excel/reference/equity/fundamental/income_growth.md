<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Income Statement Growth. Information about the growth of the company income statement.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME_GROWTH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |
| limit | number | The number of data entries to return. | true |
| period | string | Time period of the data to return. | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| period | Period the statement is returned for.  |
| growth_revenue | Growth rate of total revenue.  |
| growth_cost_of_revenue | Growth rate of cost of goods sold.  |
| growth_gross_profit | Growth rate of gross profit.  |
| growth_gross_profit_ratio | Growth rate of gross profit as a percentage of revenue.  |
| growth_research_and_development_expenses | Growth rate of expenses on research and development.  |
| growth_general_and_administrative_expenses | Growth rate of general and administrative expenses.  |
| growth_selling_and_marketing_expenses | Growth rate of expenses on selling and marketing activities.  |
| growth_other_expenses | Growth rate of other operating expenses.  |
| growth_operating_expenses | Growth rate of total operating expenses.  |
| growth_cost_and_expenses | Growth rate of total costs and expenses.  |
| growth_interest_expense | Growth rate of interest expenses.  |
| growth_depreciation_and_amortization | Growth rate of depreciation and amortization expenses.  |
| growth_ebitda | Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization.  |
| growth_ebitda_ratio | Growth rate of EBITDA as a percentage of revenue.  |
| growth_operating_income | Growth rate of operating income.  |
| growth_operating_income_ratio | Growth rate of operating income as a percentage of revenue.  |
| growth_total_other_income_expenses_net | Growth rate of net total other income and expenses.  |
| growth_income_before_tax | Growth rate of income before taxes.  |
| growth_income_before_tax_ratio | Growth rate of income before taxes as a percentage of revenue.  |
| growth_income_tax_expense | Growth rate of income tax expenses.  |
| growth_net_income | Growth rate of net income.  |
| growth_net_income_ratio | Growth rate of net income as a percentage of revenue.  |
| growth_eps | Growth rate of Earnings Per Share (EPS).  |
| growth_eps_diluted | Growth rate of diluted Earnings Per Share (EPS).  |
| growth_weighted_average_shs_out | Growth rate of weighted average shares outstanding.  |
| growth_weighted_average_shs_out_dil | Growth rate of diluted weighted average shares outstanding.  |
