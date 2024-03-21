---
title: "cash"
description: "Learn how to use the Cash Flow Statement API endpoint to retrieve information  about cash flow statements. Understand the parameters and return values of the API,  and explore the available data fields for cash flow statements."
keywords:
- Cash Flow Statement
- cash flow statement parameters
- cash flow statement returns
- cash flow statement data
- python obb.equity.fundamental.cash
- symbol
- period
- limit
- provider
- cik
- filing date
- period of report date
- include sources
- order
- sort
- net income
- depreciation and amortization
- stock based compensation
- deferred income tax
- other non-cash items
- changes in operating assets and liabilities
- accounts receivables
- inventory
- vendor non-trade receivables
- other current and non-current assets
- accounts payables
- deferred revenue
- other current and non-current liabilities
- net cash flow from operating activities
- purchases of marketable securities
- sales from maturities of investments
- investments in property plant and equipment
- payments from acquisitions
- other investing activities
- net cash flow from investing activities
- taxes paid on net share settlement
- dividends paid
- common stock repurchased
- debt proceeds
- debt repayment
- other financing activities
- net cash flow from financing activities
- net change in cash
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/cash - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the cash flow statement for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.cash(symbol='AAPL', provider='fmp')
obb.equity.fundamental.cash(symbol='AAPL', period='annual', limit=5, provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| fiscal_year | int | The specific fiscal year. Reports do not go beyond 2008. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| filing_date | date | Filing date of the financial statement. | None | True |
| filing_date_lt | date | Filing date less than the given date. | None | True |
| filing_date_lte | date | Filing date less than or equal to the given date. | None | True |
| filing_date_gt | date | Filing date greater than the given date. | None | True |
| filing_date_gte | date | Filing date greater than or equal to the given date. | None | True |
| period_of_report_date | date | Period of report date of the financial statement. | None | True |
| period_of_report_date_lt | date | Period of report date less than the given date. | None | True |
| period_of_report_date_lte | date | Period of report date less than or equal to the given date. | None | True |
| period_of_report_date_gt | date | Period of report date greater than the given date. | None | True |
| period_of_report_date_gte | date | Period of report date greater than or equal to the given date. | None | True |
| include_sources | bool | Whether to include the sources of the financial statement. | False | True |
| order | Literal[None, 'asc', 'desc'] | Order of the financial statement. | None | True |
| sort | Literal[None, 'filing_date', 'period_of_report_date'] | Sort of the financial statement. | None | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CashFlowStatement
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'polygon', 'yfinance']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| filing_date | date | The date of the filing. |
| accepted_date | datetime | The date the filing was accepted. |
| reported_currency | str | The currency in which the cash flow statement was reported. |
| net_income | float | Net income. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| deferred_income_tax | float | Deferred income tax. |
| stock_based_compensation | float | Stock-based compensation. |
| change_in_working_capital | float | Change in working capital. |
| change_in_account_receivables | float | Change in account receivables. |
| change_in_inventory | float | Change in inventory. |
| change_in_account_payable | float | Change in account payable. |
| change_in_other_working_capital | float | Change in other working capital. |
| change_in_other_non_cash_items | float | Change in other non-cash items. |
| net_cash_from_operating_activities | float | Net cash from operating activities. |
| purchase_of_property_plant_and_equipment | float | Purchase of property, plant and equipment. |
| acquisitions | float | Acquisitions. |
| purchase_of_investment_securities | float | Purchase of investment securities. |
| sale_and_maturity_of_investments | float | Sale and maturity of investments. |
| other_investing_activities | float | Other investing activities. |
| net_cash_from_investing_activities | float | Net cash from investing activities. |
| repayment_of_debt | float | Repayment of debt. |
| issuance_of_common_equity | float | Issuance of common equity. |
| repurchase_of_common_equity | float | Repurchase of common equity. |
| payment_of_dividends | float | Payment of dividends. |
| other_financing_activities | float | Other financing activities. |
| net_cash_from_financing_activities | float | Net cash from financing activities. |
| effect_of_exchange_rate_changes_on_cash | float | Effect of exchange rate changes on cash. |
| net_change_in_cash_and_equivalents | float | Net change in cash and equivalents. |
| cash_at_beginning_of_period | float | Cash at beginning of period. |
| cash_at_end_of_period | float | Cash at end of period. |
| operating_cash_flow | float | Operating cash flow. |
| capital_expenditure | float | Capital expenditure. |
| free_cash_flow | float | None |
| link | str | Link to the filing. |
| final_link | str | Link to the filing document. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| reported_currency | str | The currency in which the balance sheet is reported. |
| net_income_continuing_operations | float | Net Income (Continuing Operations) |
| net_income_discontinued_operations | float | Net Income (Discontinued Operations) |
| net_income | float | Consolidated Net Income. |
| provision_for_loan_losses | float | Provision for Loan Losses |
| provision_for_credit_losses | float | Provision for credit losses |
| depreciation_expense | float | Depreciation Expense. |
| amortization_expense | float | Amortization Expense. |
| share_based_compensation | float | Share-based compensation. |
| non_cash_adjustments_to_reconcile_net_income | float | Non-Cash Adjustments to Reconcile Net Income. |
| changes_in_operating_assets_and_liabilities | float | Changes in Operating Assets and Liabilities (Net) |
| net_cash_from_continuing_operating_activities | float | Net Cash from Continuing Operating Activities |
| net_cash_from_discontinued_operating_activities | float | Net Cash from Discontinued Operating Activities |
| net_cash_from_operating_activities | float | Net Cash from Operating Activities |
| divestitures | float | Divestitures |
| sale_of_property_plant_and_equipment | float | Sale of Property, Plant, and Equipment |
| acquisitions | float | Acquisitions |
| purchase_of_investments | float | Purchase of Investments |
| purchase_of_investment_securities | float | Purchase of Investment Securities |
| sale_and_maturity_of_investments | float | Sale and Maturity of Investments |
| loans_held_for_sale | float | Loans Held for Sale (Net) |
| purchase_of_property_plant_and_equipment | float | Purchase of Property, Plant, and Equipment |
| other_investing_activities | float | Other Investing Activities (Net) |
| net_cash_from_continuing_investing_activities | float | Net Cash from Continuing Investing Activities |
| net_cash_from_discontinued_investing_activities | float | Net Cash from Discontinued Investing Activities |
| net_cash_from_investing_activities | float | Net Cash from Investing Activities |
| payment_of_dividends | float | Payment of Dividends |
| repurchase_of_common_equity | float | Repurchase of Common Equity |
| repurchase_of_preferred_equity | float | Repurchase of Preferred Equity |
| issuance_of_common_equity | float | Issuance of Common Equity |
| issuance_of_preferred_equity | float | Issuance of Preferred Equity |
| issuance_of_debt | float | Issuance of Debt |
| repayment_of_debt | float | Repayment of Debt |
| other_financing_activities | float | Other Financing Activities (Net) |
| cash_interest_received | float | Cash Interest Received |
| net_change_in_deposits | float | Net Change in Deposits |
| net_increase_in_fed_funds_sold | float | Net Increase in Fed Funds Sold |
| net_cash_from_continuing_financing_activities | float | Net Cash from Continuing Financing Activities |
| net_cash_from_discontinued_financing_activities | float | Net Cash from Discontinued Financing Activities |
| net_cash_from_financing_activities | float | Net Cash from Financing Activities |
| effect_of_exchange_rate_changes | float | Effect of Exchange Rate Changes |
| other_net_changes_in_cash | float | Other Net Changes in Cash |
| net_change_in_cash_and_equivalents | float | Net Change in Cash and Equivalents |
| cash_income_taxes_paid | float | Cash Income Taxes Paid |
| cash_interest_paid | float | Cash Interest Paid |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| net_cash_flow_from_operating_activities_continuing | int | Net cash flow from operating activities continuing. |
| net_cash_flow_from_operating_activities_discontinued | int | Net cash flow from operating activities discontinued. |
| net_cash_flow_from_operating_activities | int | Net cash flow from operating activities. |
| net_cash_flow_from_investing_activities_continuing | int | Net cash flow from investing activities continuing. |
| net_cash_flow_from_investing_activities_discontinued | int | Net cash flow from investing activities discontinued. |
| net_cash_flow_from_investing_activities | int | Net cash flow from investing activities. |
| net_cash_flow_from_financing_activities_continuing | int | Net cash flow from financing activities continuing. |
| net_cash_flow_from_financing_activities_discontinued | int | Net cash flow from financing activities discontinued. |
| net_cash_flow_from_financing_activities | int | Net cash flow from financing activities. |
| net_cash_flow_continuing | int | Net cash flow continuing. |
| net_cash_flow_discontinued | int | Net cash flow discontinued. |
| exchange_gains_losses | int | Exchange gains losses. |
| net_cash_flow | int | Net cash flow. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

</Tabs>

