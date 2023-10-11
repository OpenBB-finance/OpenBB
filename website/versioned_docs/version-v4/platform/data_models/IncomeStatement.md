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
from openbb_provider.standard_models.income_statement_growth import (
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
| provider | Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| cik | Union[str] | The CIK of the company if no symbol is provided. | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| type | Literal['reported', 'standardized'] | Type of the statement to be fetched. | reported | True |
| year | Union[int] | Year of the statement to be fetched. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| company_name | Union[str] | Name of the company. | None | True |
| company_name_search | Union[str] | Name of the company to search. | None | True |
| sic | Union[str] | The Standard Industrial Classification (SIC) of the company. | None | True |
| filing_date | Union[date] | Filing date of the financial statement. | None | True |
| filing_date_lt | Union[date] | Filing date less than the given date. | None | True |
| filing_date_lte | Union[date] | Filing date less than or equal to the given date. | None | True |
| filing_date_gt | Union[date] | Filing date greater than the given date. | None | True |
| filing_date_gte | Union[date] | Filing date greater than or equal to the given date. | None | True |
| period_of_report_date | Union[date] | Period of report date of the financial statement. | None | True |
| period_of_report_date_lt | Union[date] | Period of report date less than the given date. | None | True |
| period_of_report_date_lte | Union[date] | Period of report date less than or equal to the given date. | None | True |
| period_of_report_date_gt | Union[date] | Period of report date greater than the given date. | None | True |
| period_of_report_date_gte | Union[date] | Period of report date greater than or equal to the given date. | None | True |
| include_sources | Union[bool] | Whether to include the sources of the financial statement. | None | True |
| order | Union[Literal['asc', 'desc']] | Order of the financial statement. | None | True |
| sort | Union[Literal['filing_date', 'period_of_report_date']] | Sort of the financial statement. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | Date of the income statement. |
| period | Union[str] | Period of the income statement. |
| cik | Union[str] | Central Index Key. |
| revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Revenue. |
| cost_of_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost of revenue. |
| gross_profit | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Gross profit. |
| cost_and_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost and expenses. |
| gross_profit_ratio | Union[float] | Gross profit ratio. |
| research_and_development_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Research and development expenses. |
| general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Selling, general and administrative expenses. |
| other_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Other expenses. |
| operating_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating expenses. |
| depreciation_and_amortization | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Depreciation and amortization. |
| ebitda | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | Union[float] | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating income. |
| operating_income_ratio | Union[float] | Operating income ratio. |
| interest_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest income. |
| interest_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest expense. |
| total_other_income_expenses_net | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Total other income expenses net. |
| income_before_tax | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income before tax. |
| income_before_tax_ratio | Union[float] | Income before tax ratio. |
| income_tax_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income tax expense. |
| net_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Net income. |
| net_income_ratio | Union[float] | Net income ratio. |
| eps | Union[float] | Earnings per share. |
| eps_diluted | Union[float] | Earnings per share diluted. |
| weighted_average_shares_outstanding | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding diluted. |
| link | Union[str] | Link to the income statement. |
| final_link | Union[str] | Final link to the income statement. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | Date of the income statement. |
| period | Union[str] | Period of the income statement. |
| cik | Union[str] | Central Index Key. |
| revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Revenue. |
| cost_of_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost of revenue. |
| gross_profit | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Gross profit. |
| cost_and_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost and expenses. |
| gross_profit_ratio | Union[float] | Gross profit ratio. |
| research_and_development_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Research and development expenses. |
| general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Selling, general and administrative expenses. |
| other_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Other expenses. |
| operating_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating expenses. |
| depreciation_and_amortization | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Depreciation and amortization. |
| ebitda | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | Union[float] | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating income. |
| operating_income_ratio | Union[float] | Operating income ratio. |
| interest_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest income. |
| interest_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest expense. |
| total_other_income_expenses_net | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Total other income expenses net. |
| income_before_tax | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income before tax. |
| income_before_tax_ratio | Union[float] | Income before tax ratio. |
| income_tax_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income tax expense. |
| net_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Net income. |
| net_income_ratio | Union[float] | Net income ratio. |
| eps | Union[float] | Earnings per share. |
| eps_diluted | Union[float] | Earnings per share diluted. |
| weighted_average_shares_outstanding | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding diluted. |
| link | Union[str] | Link to the income statement. |
| final_link | Union[str] | Final link to the income statement. |
| reported_currency | Union[str] | Reporting currency. |
| filling_date | Union[date] | Filling date. |
| accepted_date | Union[datetime] | Accepted date. |
| calendar_year | Union[int] | Calendar year. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | Date of the income statement. |
| period | Union[str] | Period of the income statement. |
| cik | Union[str] | Central Index Key. |
| revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Revenue. |
| cost_of_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost of revenue. |
| gross_profit | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Gross profit. |
| cost_and_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Cost and expenses. |
| gross_profit_ratio | Union[float] | Gross profit ratio. |
| research_and_development_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Research and development expenses. |
| general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | General and administrative expenses. |
| selling_and_marketing_expenses | float | Selling and marketing expenses. |
| selling_general_and_administrative_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Selling, general and administrative expenses. |
| other_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Other expenses. |
| operating_expenses | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating expenses. |
| depreciation_and_amortization | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Depreciation and amortization. |
| ebitda | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Earnings before interest, taxes, depreciation and amortization. |
| ebitda_ratio | Union[float] | Earnings before interest, taxes, depreciation and amortization ratio. |
| operating_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Operating income. |
| operating_income_ratio | Union[float] | Operating income ratio. |
| interest_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest income. |
| interest_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Interest expense. |
| total_other_income_expenses_net | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Total other income expenses net. |
| income_before_tax | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income before tax. |
| income_before_tax_ratio | Union[float] | Income before tax ratio. |
| income_tax_expense | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Income tax expense. |
| net_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Net income. |
| net_income_ratio | Union[float] | Net income ratio. |
| eps | Union[float] | Earnings per share. |
| eps_diluted | Union[float] | Earnings per share diluted. |
| weighted_average_shares_outstanding | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding. |
| weighted_average_shares_outstanding_dil | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Weighted average shares outstanding diluted. |
| link | Union[str] | Link to the income statement. |
| final_link | Union[str] | Final link to the income statement. |
| income_loss_from_continuing_operations_before_tax | Union[float] | Income/Loss From Continuing Operations After Tax |
| income_loss_from_continuing_operations_after_tax | Union[float] | Income (loss) from continuing operations after tax |
| benefits_costs_expenses | Union[float] | Benefits, costs and expenses |
| net_income_loss_attributable_to_noncontrolling_interest | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f07e013e430>)]] | Net income (loss) attributable to noncontrolling interest |
| net_income_loss_attributable_to_parent | Union[float] | Net income (loss) attributable to parent |
| net_income_loss_available_to_common_stockholders_basic | Union[float] | Net Income/Loss Available To Common Stockholders Basic |
| participating_securities_distributed_and_undistributed_earnings_loss_basic | Union[float] | Participating Securities Distributed And Undistributed Earnings Loss Basic |
| nonoperating_income_loss | Union[float] | Nonoperating Income Loss |
| preferred_stock_dividends_and_other_adjustments | Union[float] | Preferred stock dividends and other adjustments |
</TabItem>

</Tabs>

