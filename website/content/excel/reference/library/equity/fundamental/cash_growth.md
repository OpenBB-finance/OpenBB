---
title: cash_growth
description: Learn about Cash Flow Statement Growth and how to retrieve cash growth
  data using the Python function obb.equity.fundamental.cash_growth(). This page provides
  details on the function's parameters and the data it returns, including information
  on net income, depreciation and amortization, working capital, investments, financing
  activities, and more.
keywords: 
- Cash Flow Statement Growth
- company cash flow
- cash growth
- Python
- function
- parameters
- symbol
- limit
- provider
- data
- returns
- net income
- depreciation and amortization
- deferred income tax
- stock-based compensation
- working capital
- accounts receivables
- inventory
- accounts payables
- other non-cash items
- net cash provided by operating activities
- investments in property, plant, and equipment
- net acquisitions
- purchases of investments
- sales maturities of investments
- net cash used for investing activities
- debt repayment
- common stock issued
- common stock repurchased
- dividends paid
- net cash used/provided by financing activities
- foreign exchange changes on cash
- net change in cash
- cash at end of period
- cash at beginning of period
- operating cash flow
- capital expenditure
- free cash flow
---

<!-- markdownlint-disable MD041 -->

Cash Flow Statement Growth. Information about the growth of the company cash flow statement.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.CASH_GROWTH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| limit | Number | The number of data entries to return. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| period | Period the statement is returned for.  |
| growth_net_income | Growth rate of net income.  |
| growth_depreciation_and_amortization | Growth rate of depreciation and amortization.  |
| growth_deferred_income_tax | Growth rate of deferred income tax.  |
| growth_stock_based_compensation | Growth rate of stock-based compensation.  |
| growth_change_in_working_capital | Growth rate of change in working capital.  |
| growth_accounts_receivables | Growth rate of accounts receivables.  |
| growth_inventory | Growth rate of inventory.  |
| growth_accounts_payables | Growth rate of accounts payables.  |
| growth_other_working_capital | Growth rate of other working capital.  |
| growth_other_non_cash_items | Growth rate of other non-cash items.  |
| growth_net_cash_provided_by_operating_activities | Growth rate of net cash provided by operating activities.  |
| growth_investments_in_property_plant_and_equipment | Growth rate of investments in property, plant, and equipment.  |
| growth_acquisitions_net | Growth rate of net acquisitions.  |
| growth_purchases_of_investments | Growth rate of purchases of investments.  |
| growth_sales_maturities_of_investments | Growth rate of sales maturities of investments.  |
| growth_other_investing_activities | Growth rate of other investing activities.  |
| growth_net_cash_used_for_investing_activities | Growth rate of net cash used for investing activities.  |
| growth_debt_repayment | Growth rate of debt repayment.  |
| growth_common_stock_issued | Growth rate of common stock issued.  |
| growth_common_stock_repurchased | Growth rate of common stock repurchased.  |
| growth_dividends_paid | Growth rate of dividends paid.  |
| growth_other_financing_activities | Growth rate of other financing activities.  |
| growth_net_cash_used_provided_by_financing_activities | Growth rate of net cash used/provided by financing activities.  |
| growth_effect_of_forex_changes_on_cash | Growth rate of the effect of foreign exchange changes on cash.  |
| growth_net_change_in_cash | Growth rate of net change in cash.  |
| growth_cash_at_end_of_period | Growth rate of cash at the end of the period.  |
| growth_cash_at_beginning_of_period | Growth rate of cash at the beginning of the period.  |
| growth_operating_cash_flow | Growth rate of operating cash flow.  |
| growth_capital_expenditure | Growth rate of capital expenditure.  |
| growth_free_cash_flow | Growth rate of free cash flow.  |
