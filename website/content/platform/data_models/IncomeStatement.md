---
title: Income Statement
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `IncomeStatement` | `IncomeStatementQueryParams` | `IncomeStatementData` |

### Import Statement

```python
from openbb_provider.standard_models.income_statement import (
IncomeStatementData,
IncomeStatementQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| cik | str | The CIK of the company if no symbol is provided. | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| type | Literal['reported', 'standardized'] | Type of the statement to be fetched. | reported | True |
| year | int | Year of the statement to be fetched. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| company_name | str | Name of the company. | None | True |
| company_name_search | str | Name of the company to search. | None | True |
| sic | str | The Standard Industrial Classification (SIC) of the company. | None | True |
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
| link | str | Link to the income statement. |
| final_link | str | Final link to the income statement. |
</TabItem>

<TabItem value='fmp' label='fmp'>

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

