---
title: IncomeStatement
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | NonNegativeInt | The number of data entries to return. | 12 | True |
| provider | Literal['fmp', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| company_name | str | Name of the company. |  | True |
| company_name_search | str | Name of the company to search. |  | True |
| sic | str | The Standard Industrial Classification (SIC) of the company. |  | True |
| filing_date | date | Filing date of the financial statement. |  | True |
| filing_date_lt | date | Filing date less than the given date. |  | True |
| filing_date_lte | date | Filing date less than or equal to the given date. |  | True |
| filing_date_gt | date | Filing date greater than the given date. |  | True |
| filing_date_gte | date | Filing date greater than or equal to the given date. |  | True |
| period_of_report_date | date | Period of report date of the financial statement. |  | True |
| period_of_report_date_lt | date | Period of report date less than the given date. |  | True |
| period_of_report_date_lte | date | Period of report date less than or equal to the given date. |  | True |
| period_of_report_date_gt | date | Period of report date greater than the given date. |  | True |
| period_of_report_date_gte | date | Period of report date greater than or equal to the given date. |  | True |
| include_sources | bool | Whether to include the sources of the financial statement. |  | True |
| order | Literal['asc', 'desc'] | Order of the financial statement. |  | True |
| sort | Literal['filing_date', 'period_of_report_date'] | Sort of the financial statement. |  | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | date | Date of the income statement. |
| period | str | Period of the income statement. |
| cik | str | Central Index Key. |
| revenue | int | Revenue. |
| cost_of_revenue | int | Cost of revenue. |
| gross_profit | int | Gross profit. |
| cost_and_expenses | int | Cost and expenses. |
| gross_profit_ratio | float | Gross profit ratio. |
| research_and_development_expenses | int | Research and development expenses. |
| general_and_administrative_expenses | int | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | int | Selling, general and administrative expenses. |
| other_expenses | int | Other expenses. |
| operating_expenses | int | Operating expenses. |
| depreciation_and_amortization | int | Depreciation and amortization. |
| ebitda | int | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | float | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | int | Operating income. |
| operating_income_ratio | float | Operating income ratio. |
| interest_income | int | Interest income. |
| interest_expense | int | Interest expense. |
| total_other_income_expenses_net | int | Total other income expenses net. |
| income_before_tax | int | Income before tax. |
| income_before_tax_ratio | float | Income before tax ratio. |
| income_tax_expense | int | Income tax expense. |
| net_income | int | Net income. |
| net_income_ratio | float | Net income ratio. |
| eps | float | Earnings per share. |
| eps_diluted | float | Earnings per share diluted. |
| weighted_average_shares_outstanding | int | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | int | Weighted average shares outstanding diluted. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| income_loss_from_continuing_operations_before_tax | float | Income/Loss From Continuing Operations After Tax |
| income_loss_from_continuing_operations_after_tax | float | Income/Loss From Continuing Operations After Tax |
| benefits_costs_expenses | float | Benefits, Costs And Expenses |
| net_income_loss_attributable_to_noncontrolling_interest | float | Net Income/Loss Attributable To Noncontrolling Interest |
| net_income_loss_attributable_to_parent | float | Net Income/Loss Attributable To Parent |
| income_tax_expense_benefit_deferred | float | Income Tax Expense/Benefit Deferred |
| participating_securities_distributed_and_undistributed_earnings_loss_basic | float | Participating Securities Distributed And Undistributed Earnings Loss Basic |
| net_income_loss_available_to_common_stockholders_basic | float | Net Income/Loss Available To Common Stockholders Basic |
| nonoperating_income_loss | float | Nonoperating Income Loss |
| preferred_stock_dividends_and_other_adjustments | float | Preferred Stock Dividends And Other Adjustments |
</TabItem>

</Tabs>

