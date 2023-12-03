---
title: income
description: Get income statement and financial performance data for a company. Parameters
  include symbol, period, limit, provider, and more. Data includes revenue, gross
  profit, operating expenses, net income, and more.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Income Statement. Report on a company's financial performance.

```python wordwrap
obb.equity.fundamental.income(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 5, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| cik | str | The CIK of the company if no symbol is provided. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 5 | True |
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

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[IncomeStatement]
        Serializable results.

    provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
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
| date | date | The date of the data. In this case, the date of the income statement. |
| period | str | Period of the income statement. |
| cik | str | Central Index Key. |
| revenue | float | Revenue. |
| cost_of_revenue | float | Cost of revenue. |
| gross_profit | float | Gross profit. |
| cost_and_expenses | float | Cost and expenses. |
| gross_profit_ratio | float | Gross profit ratio. |
| research_and_development_expenses | float | Research and development expenses. |
| general_and_administrative_expenses | float | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | float | Selling, general and administrative expenses. |
| other_expenses | float | Other expenses. |
| operating_expenses | float | Operating expenses. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| ebitda | float | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | float | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | float | Operating income. |
| operating_income_ratio | float | Operating income ratio. |
| interest_income | float | Interest income. |
| interest_expense | float | Interest expense. |
| total_other_income_expenses_net | float | Total other income expenses net. |
| income_before_tax | float | Income before tax. |
| income_before_tax_ratio | float | Income before tax ratio. |
| income_tax_expense | float | Income tax expense. |
| net_income | float | Net income. |
| net_income_ratio | float | Net income ratio. |
| eps | float | Earnings per share. |
| eps_diluted | float | Earnings per share diluted. |
| weighted_average_shares_outstanding | float | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | float | Weighted average shares outstanding diluted. |
| link | str | Link to the income statement. |
| final_link | str | Final link to the income statement. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. In this case, the date of the income statement. |
| period | str | Period of the income statement. |
| cik | str | Central Index Key. |
| revenue | float | Revenue. |
| cost_of_revenue | float | Cost of revenue. |
| gross_profit | float | Gross profit. |
| cost_and_expenses | float | Cost and expenses. |
| gross_profit_ratio | float | Gross profit ratio. |
| research_and_development_expenses | float | Research and development expenses. |
| general_and_administrative_expenses | float | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | float | Selling, general and administrative expenses. |
| other_expenses | float | Other expenses. |
| operating_expenses | float | Operating expenses. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| ebitda | float | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | float | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | float | Operating income. |
| operating_income_ratio | float | Operating income ratio. |
| interest_income | float | Interest income. |
| interest_expense | float | Interest expense. |
| total_other_income_expenses_net | float | Total other income expenses net. |
| income_before_tax | float | Income before tax. |
| income_before_tax_ratio | float | Income before tax ratio. |
| income_tax_expense | float | Income tax expense. |
| net_income | float | Net income. |
| net_income_ratio | float | Net income ratio. |
| eps | float | Earnings per share. |
| eps_diluted | float | Earnings per share diluted. |
| weighted_average_shares_outstanding | float | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | float | Weighted average shares outstanding diluted. |
| link | str | Link to the income statement. |
| final_link | str | Final link to the income statement. |
| reported_currency | str | Reporting currency. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| calendar_year | int | Calendar year. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. In this case, the date of the income statement. |
| period | str | Period of the income statement. |
| cik | str | Central Index Key. |
| revenue | float | Revenue. |
| cost_of_revenue | float | Cost of revenue. |
| gross_profit | float | Gross profit. |
| cost_and_expenses | float | Cost and expenses. |
| gross_profit_ratio | float | Gross profit ratio. |
| research_and_development_expenses | float | Research and development expenses. |
| general_and_administrative_expenses | float | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | float | Selling, general and administrative expenses. |
| other_expenses | float | Other expenses. |
| operating_expenses | float | Operating expenses. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| ebitda | float | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | float | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | float | Operating income. |
| operating_income_ratio | float | Operating income ratio. |
| interest_income | float | Interest income. |
| interest_expense | float | Interest expense. |
| total_other_income_expenses_net | float | Total other income expenses net. |
| income_before_tax | float | Income before tax. |
| income_before_tax_ratio | float | Income before tax ratio. |
| income_tax_expense | float | Income tax expense. |
| net_income | float | Net income. |
| net_income_ratio | float | Net income ratio. |
| eps | float | Earnings per share. |
| eps_diluted | float | Earnings per share diluted. |
| weighted_average_shares_outstanding | float | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | float | Weighted average shares outstanding diluted. |
| link | str | Link to the income statement. |
| final_link | str | Final link to the income statement. |
| income_loss_from_continuing_operations_before_tax | float | Income/Loss From Continuing Operations After Tax |
| income_loss_from_continuing_operations_after_tax | float | Income (loss) from continuing operations after tax |
| benefits_costs_expenses | float | Benefits, costs and expenses |
| net_income_loss_attributable_to_noncontrolling_interest | int | Net income (loss) attributable to noncontrolling interest |
| net_income_loss_attributable_to_parent | float | Net income (loss) attributable to parent |
| net_income_loss_available_to_common_stockholders_basic | float | Net Income/Loss Available To Common Stockholders Basic |
| participating_securities_distributed_and_undistributed_earnings_loss_basic | float | Participating Securities Distributed And Undistributed Earnings Loss Basic |
| nonoperating_income_loss | float | Nonoperating Income Loss |
| preferred_stock_dividends_and_other_adjustments | float | Preferred stock dividends and other adjustments |
</TabItem>

</Tabs>

