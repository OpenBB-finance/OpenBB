---
title: balance
description: OpenBB Terminal Function
---

# balance

Prints a complete balance sheet statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Account payables, Accumulated other comprehensive income loss, Cash and cash equivalents, Cash and short term investments, Common stock, Deferred revenue, Deferred revenue non current, Deferred tax liabilities non current, Filling date, Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory, Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets, Other current assets, Other current liabilities, Other liabilities, Other non current assets, Other non current liabilities, Othertotal stockholders equity, Period, Property plant equipment net, Retained earnings, Short term debt, Short term investments, Tax assets, Tax payables, Total assets, Total current assets, Total current liabilities, Total debt, Total investments, Total liabilities, Total liabilities and stockholders equity, Total non current assets, Total non current liabilities, and Total stockholders equity. [Source: Alpha Vantage]

### Usage

```python
usage: balance [-q] [-r] [-p column]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_quarter | Quarter fundamental data flag. | False | True | None |
| ratios | Shows percentage change of values. | False | True | None |
| plot | Rows to plot, comma separated. (-1 represents invalid data) | None | True | cash_and_cash_equivalents, other_short-term_investments, total_cash, net_receivables, inventory, other_current_assets, total_current_assets, gross_property, plant_and_equipment, accumulated_depreciation, net_property, plant_and_equipment, equity_and_other_investments, other_long-term_assets, total_non-current_assets, total_assets, current_debt, accounts_payable, deferred_revenues, other_current_liabilities, total_current_liabilities, long-term_debt, deferred_tax_liabilities, deferred_revenues, other_long-term_liabilities, total_non-current_liabilities, total_liabilities, common_stock, retained_earnings, accumulated_other_comprehensive_income, total_stockholders'_equity, total_liabilities_and_stockholders'_equity |
---

