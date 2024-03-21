---
title: "income"
description: "Get income statement and financial performance data for a company. Parameters  include symbol, period, limit, provider, and more. Data includes revenue, gross  profit, operating expenses, net income, and more."
keywords:
- income statement
- financial performance
- get income data
- period
- limit
- provider
- symbol
- cik
- filing date
- period of report date
- include sources
- order
- sort
- revenue
- cost of revenue
- gross profit
- cost and expenses
- research and development expenses
- general and administrative expenses
- selling and marketing expenses
- other expenses
- operating expenses
- depreciation and amortization
- ebitda
- operating income
- interest income
- interest expense
- income before tax
- income tax expense
- net income
- eps
- weighted average shares outstanding
- link
- reported currency
- filling date
- accepted date
- calendar year
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/income - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the income statement for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.income(symbol='AAPL', provider='fmp')
obb.equity.fundamental.income(symbol='AAPL', period='annual', limit=5, provider='intrinio')
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
| include_sources | bool | Whether to include the sources of the financial statement. | None | True |
| order | Literal['asc', 'desc'] | Order of the financial statement. | None | True |
| sort | Literal['filing_date', 'period_of_report_date'] | Sort of the financial statement. | None | True |
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
    results : IncomeStatement
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
| filing_date | date | The date when the filing was made. |
| accepted_date | datetime | The date and time when the filing was accepted. |
| reported_currency | str | The currency in which the balance sheet was reported. |
| revenue | float | Total revenue. |
| cost_of_revenue | float | Cost of revenue. |
| gross_profit | float | Gross profit. |
| gross_profit_margin | float | Gross profit margin. |
| general_and_admin_expense | float | General and administrative expenses. |
| research_and_development_expense | float | Research and development expenses. |
| selling_and_marketing_expense | float | Selling and marketing expenses. |
| selling_general_and_admin_expense | float | Selling, general and administrative expenses. |
| other_expenses | float | Other expenses. |
| total_operating_expenses | float | Total operating expenses. |
| cost_and_expenses | float | Cost and expenses. |
| interest_income | float | Interest income. |
| total_interest_expense | float | Total interest expenses. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| ebitda | float | EBITDA. |
| ebitda_margin | float | EBITDA margin. |
| total_operating_income | float | Total operating income. |
| operating_income_margin | float | Operating income margin. |
| total_other_income_expenses | float | Total other income and expenses. |
| total_pre_tax_income | float | Total pre-tax income. |
| pre_tax_income_margin | float | Pre-tax income margin. |
| income_tax_expense | float | Income tax expense. |
| consolidated_net_income | float | Consolidated net income. |
| net_income_margin | float | Net income margin. |
| basic_earnings_per_share | float | Basic earnings per share. |
| diluted_earnings_per_share | float | Diluted earnings per share. |
| weighted_average_basic_shares_outstanding | float | Weighted average basic shares outstanding. |
| weighted_average_diluted_shares_outstanding | float | Weighted average diluted shares outstanding. |
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
| revenue | float | Total revenue |
| operating_revenue | float | Total operating revenue |
| cost_of_revenue | float | Total cost of revenue |
| operating_cost_of_revenue | float | Total operating cost of revenue |
| gross_profit | float | Total gross profit |
| gross_profit_margin | float | Gross margin ratio. |
| provision_for_credit_losses | float | Provision for credit losses |
| research_and_development_expense | float | Research and development expense |
| selling_general_and_admin_expense | float | Selling, general, and admin expense |
| salaries_and_employee_benefits | float | Salaries and employee benefits |
| marketing_expense | float | Marketing expense |
| net_occupancy_and_equipment_expense | float | Net occupancy and equipment expense |
| other_operating_expenses | float | Other operating expenses |
| depreciation_expense | float | Depreciation expense |
| amortization_expense | float | Amortization expense |
| amortization_of_deferred_policy_acquisition_costs | float | Amortization of deferred policy acquisition costs |
| exploration_expense | float | Exploration expense |
| depletion_expense | float | Depletion expense |
| total_operating_expenses | float | Total operating expenses |
| total_operating_income | float | Total operating income |
| deposits_and_money_market_investments_interest_income | float | Deposits and money market investments interest income |
| federal_funds_sold_and_securities_borrowed_interest_income | float | Federal funds sold and securities borrowed interest income |
| investment_securities_interest_income | float | Investment securities interest income |
| loans_and_leases_interest_income | float | Loans and leases interest income |
| trading_account_interest_income | float | Trading account interest income |
| other_interest_income | float | Other interest income |
| total_non_interest_income | float | Total non-interest income |
| interest_and_investment_income | float | Interest and investment income |
| short_term_borrowings_interest_expense | float | Short-term borrowings interest expense |
| long_term_debt_interest_expense | float | Long-term debt interest expense |
| capitalized_lease_obligations_interest_expense | float | Capitalized lease obligations interest expense |
| deposits_interest_expense | float | Deposits interest expense |
| federal_funds_purchased_and_securities_sold_interest_expense | float | Federal funds purchased and securities sold interest expense |
| other_interest_expense | float | Other interest expense |
| total_interest_expense | float | Total interest expense |
| net_interest_income | float | Net interest income |
| other_non_interest_income | float | Other non-interest income |
| investment_banking_income | float | Investment banking income |
| trust_fees_by_commissions | float | Trust fees by commissions |
| premiums_earned | float | Premiums earned |
| insurance_policy_acquisition_costs | float | Insurance policy acquisition costs |
| current_and_future_benefits | float | Current and future benefits |
| property_and_liability_insurance_claims | float | Property and liability insurance claims |
| total_non_interest_expense | float | Total non-interest expense |
| net_realized_and_unrealized_capital_gains_on_investments | float | Net realized and unrealized capital gains on investments |
| other_gains | float | Other gains |
| non_operating_income | float | Non-operating income |
| other_income | float | Other income |
| other_revenue | float | Other revenue |
| extraordinary_income | float | Extraordinary income |
| total_other_income | float | Total other income |
| ebitda | float | Earnings Before Interest, Taxes, Depreciation and Amortization. |
| ebitda_margin | float | Margin on Earnings Before Interest, Taxes, Depreciation and Amortization. |
| total_pre_tax_income | float | Total pre-tax income |
| ebit | float | Earnings Before Interest and Taxes. |
| pre_tax_income_margin | float | Pre-Tax Income Margin. |
| income_tax_expense | float | Income tax expense |
| impairment_charge | float | Impairment charge |
| restructuring_charge | float | Restructuring charge |
| service_charges_on_deposit_accounts | float | Service charges on deposit accounts |
| other_service_charges | float | Other service charges |
| other_special_charges | float | Other special charges |
| other_cost_of_revenue | float | Other cost of revenue |
| net_income_continuing_operations | float | Net income (continuing operations) |
| net_income_discontinued_operations | float | Net income (discontinued operations) |
| consolidated_net_income | float | Consolidated net income |
| other_adjustments_to_consolidated_net_income | float | Other adjustments to consolidated net income |
| other_adjustment_to_net_income_attributable_to_common_shareholders | float | Other adjustment to net income attributable to common shareholders |
| net_income_attributable_to_noncontrolling_interest | float | Net income attributable to noncontrolling interest |
| net_income_attributable_to_common_shareholders | float | Net income attributable to common shareholders |
| basic_earnings_per_share | float | Basic earnings per share |
| diluted_earnings_per_share | float | Diluted earnings per share |
| basic_and_diluted_earnings_per_share | float | Basic and diluted earnings per share |
| cash_dividends_to_common_per_share | float | Cash dividends to common per share |
| preferred_stock_dividends_declared | float | Preferred stock dividends declared |
| weighted_average_basic_shares_outstanding | float | Weighted average basic shares outstanding |
| weighted_average_diluted_shares_outstanding | float | Weighted average diluted shares outstanding |
| weighted_average_basic_and_diluted_shares_outstanding | float | Weighted average basic and diluted shares outstanding |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| revenue | float | Total Revenue |
| cost_of_revenue_goods | float | Cost of Revenue - Goods |
| cost_of_revenue_services | float | Cost of Revenue - Services |
| cost_of_revenue | float | Cost of Revenue |
| gross_profit | float | Gross Profit |
| provisions_for_loan_lease_and_other_losses | float | Provisions for loan lease and other losses |
| depreciation_and_amortization | float | Depreciation and Amortization |
| income_tax_expense_benefit_current | float | Income tax expense benefit current |
| deferred_tax_benefit | float | Deferred tax benefit |
| benefits_costs_expenses | float | Benefits, costs and expenses |
| selling_general_and_administrative_expense | float | Selling, general and administrative expense |
| research_and_development | float | Research and development |
| costs_and_expenses | float | Costs and expenses |
| other_operating_expenses | float | Other Operating Expenses |
| operating_expenses | float | Operating expenses |
| operating_income | float | Operating Income/Loss |
| non_operating_income | float | Non Operating Income/Loss |
| interest_and_dividend_income | float | Interest and Dividend Income |
| total_interest_expense | float | Interest Expense |
| interest_and_debt_expense | float | Interest and Debt Expense |
| net_interest_income | float | Interest Income Net |
| interest_income_after_provision_for_losses | float | Interest Income After Provision for Losses |
| non_interest_expense | float | Non-Interest Expense |
| non_interest_income | float | Non-Interest Income |
| income_from_discontinued_operations_net_of_tax_on_disposal | float | Income From Discontinued Operations Net of Tax on Disposal |
| income_from_discontinued_operations_net_of_tax | float | Income From Discontinued Operations Net of Tax |
| income_before_equity_method_investments | float | Income Before Equity Method Investments |
| income_from_equity_method_investments | float | Income From Equity Method Investments |
| total_pre_tax_income | float | Income Before Tax |
| income_tax_expense | float | Income Tax Expense |
| income_after_tax | float | Income After Tax |
| consolidated_net_income | float | Net Income/Loss |
| net_income_attributable_noncontrolling_interest | float | Net income (loss) attributable to noncontrolling interest |
| net_income_attributable_to_parent | float | Net income (loss) attributable to parent |
| net_income_attributable_to_common_shareholders | float | Net Income/Loss Available To Common Stockholders Basic |
| participating_securities_earnings | float | Participating Securities Distributed And Undistributed Earnings Loss Basic |
| undistributed_earnings_allocated_to_participating_securities | float | Undistributed Earnings Allocated To Participating Securities |
| common_stock_dividends | float | Common Stock Dividends |
| preferred_stock_dividends_and_other_adjustments | float | Preferred stock dividends and other adjustments |
| basic_earnings_per_share | float | Earnings Per Share |
| diluted_earnings_per_share | float | Diluted Earnings Per Share |
| weighted_average_basic_shares_outstanding | float | Basic Average Shares |
| weighted_average_diluted_shares_outstanding | float | Diluted Average Shares |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

</Tabs>

