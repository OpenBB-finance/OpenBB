---
title: cash
description: OpenBB Terminal Function
---

# cash

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activities, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activities, Other investing activities, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Alpha Vantage]

### Usage

```python
usage: cash [-l LIMIT] [-q] [-r] [-p column]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of latest years/quarters. | 5 | True | None |
| b_quarter | Quarter fundamental data flag. | False | True | None |
| ratios | Shows percentage change of values. | False | True | None |
| plot | Rows to plot. (-1 represents invalid data) | None | True | net_income, depreciation_&_amortisation, deferred_income_taxes, stock-based_compensation, change_in working_capital, accounts_receivable, inventory, accounts_payable, other_working_capital, other_non-cash_items, net_cash_provided_by_operating_activities, investments_in_property, plant_and_equipment, acquisitions, net, purchases_of_investments, sales/maturities_of_investments, other_investing_activities, net_cash_used_for_investing_activities, debt_repayment, common_stock_issued, common_stock_repurchased, dividends_paid, other_financing_activities, net_cash_used_provided_by_(used_for)_financing_activities, net_change_in_cash, cash_at_beginning_of_period, cash_at_end_of_period, operating_cash_flow, capital_expenditure, free_cash_flow |
---

