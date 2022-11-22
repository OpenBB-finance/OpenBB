---
title: income
description: OpenBB Terminal Function
---

# income

Prints a complete income statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Cost and expenses, Cost of revenue, Depreciation and amortization, Ebitda, Ebitda Ratio, Eps, EPS Diluted, Filling date, Final link, General and administrative expenses, Gross profit, Gross profit ratio, Income before tax, Income before tax ratio, Income tax expense, Interest expense, Link, Net income, Net income ratio, Operating expenses, Operating income, Operating income ratio, Other expenses, Period, Research and development expenses, Revenue, Selling and marketing expenses, Total other income expenses net, Weighted average shs out, Weighted average shs out dil [Source: Alpha Vantage]

### Usage

```python
usage: income [-q] [-r] [-p column]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_quarter | Quarter fundamental data flag. | False | True | None |
| ratios | Shows percentage change of values. | False | True | None |
| plot | Rows to plot, comma separated. (-1 represents invalid data) | None | True | total_revenue, cost_of_revenue, gross_profit, research_development, selling_general_and_administrative, total_operating_expenses, operating_income_or_loss, interest_expense, total_other_income/expenses_net, income_before_tax, income_tax_expense, income_from_continuing_operations, net_income, net_income_available_to_common_shareholders, basic_eps, diluted_eps, basic_average_shares, diluted_average_shares, ebitda |
---

