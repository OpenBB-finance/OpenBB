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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Cash Flow Statement Growth. Information about the growth of the company cash flow statement.

```python wordwrap
obb.equity.fundamental.cash_growth(symbol: Union[str, List[str]], limit: int = 10, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 10 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CashFlowStatementGrowth]
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
| period | str | Period the statement is returned for. |
| growth_net_income | float | Growth rate of net income. |
| growth_depreciation_and_amortization | float | Growth rate of depreciation and amortization. |
| growth_deferred_income_tax | float | Growth rate of deferred income tax. |
| growth_stock_based_compensation | float | Growth rate of stock-based compensation. |
| growth_change_in_working_capital | float | Growth rate of change in working capital. |
| growth_accounts_receivables | float | Growth rate of accounts receivables. |
| growth_inventory | float | Growth rate of inventory. |
| growth_accounts_payables | float | Growth rate of accounts payables. |
| growth_other_working_capital | float | Growth rate of other working capital. |
| growth_other_non_cash_items | float | Growth rate of other non-cash items. |
| growth_net_cash_provided_by_operating_activities | float | Growth rate of net cash provided by operating activities. |
| growth_investments_in_property_plant_and_equipment | float | Growth rate of investments in property, plant, and equipment. |
| growth_acquisitions_net | float | Growth rate of net acquisitions. |
| growth_purchases_of_investments | float | Growth rate of purchases of investments. |
| growth_sales_maturities_of_investments | float | Growth rate of sales maturities of investments. |
| growth_other_investing_activities | float | Growth rate of other investing activities. |
| growth_net_cash_used_for_investing_activities | float | Growth rate of net cash used for investing activities. |
| growth_debt_repayment | float | Growth rate of debt repayment. |
| growth_common_stock_issued | float | Growth rate of common stock issued. |
| growth_common_stock_repurchased | float | Growth rate of common stock repurchased. |
| growth_dividends_paid | float | Growth rate of dividends paid. |
| growth_other_financing_activities | float | Growth rate of other financing activities. |
| growth_net_cash_used_provided_by_financing_activities | float | Growth rate of net cash used/provided by financing activities. |
| growth_effect_of_forex_changes_on_cash | float | Growth rate of the effect of foreign exchange changes on cash. |
| growth_net_change_in_cash | float | Growth rate of net change in cash. |
| growth_cash_at_end_of_period | float | Growth rate of cash at the end of the period. |
| growth_cash_at_beginning_of_period | float | Growth rate of cash at the beginning of the period. |
| growth_operating_cash_flow | float | Growth rate of operating cash flow. |
| growth_capital_expenditure | float | Growth rate of capital expenditure. |
| growth_free_cash_flow | float | Growth rate of free cash flow. |
</TabItem>

</Tabs>

