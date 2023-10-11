---
title: Balance Sheet
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `BalanceSheet` | `BalanceSheetQueryParams` | `BalanceSheetData` |

### Import Statement

```python
from openbb_provider.standard_models.balance_sheet import (
BalanceSheetData,
BalanceSheetQueryParams,
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
| cik | Union[str] | Central Index Key (CIK) of the company. | None | True |
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
| date | date | Date of the fetched statement. |
| cik | Union[str] | Central Index Key (CIK) of the company. |
| currency | Union[str] | Reporting currency. |
| filling_date | Union[date] | Filling date. |
| accepted_date | Union[datetime] | Accepted date. |
| period | Union[str] | Reporting period of the statement. |
| cash_and_cash_equivalents | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Cash and cash equivalents |
| short_term_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Short-term investments |
| long_term_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Long-term investments |
| inventory | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Inventory |
| net_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Receivables, net |
| marketable_securities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Marketable securities |
| property_plant_equipment_net | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Property, plant and equipment, net |
| goodwill | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Goodwill |
| assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total assets |
| current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total current assets |
| other_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other current assets |
| intangible_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Intangible assets |
| tax_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes |
| other_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other assets |
| non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total non-current assets |
| other_non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other non-current assets |
| account_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accounts payable |
| tax_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes |
| deferred_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes, other deferred revenue |
| total_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total assets |
| long_term_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities |
| other_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other current liabilities |
| current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total current liabilities |
| total_liabilities_and_total_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities and total equity |
| other_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other liabilities |
| other_non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other non-current liabilities |
| non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities and stockholders' equity |
| other_stockholder_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other stockholders equity |
| total_stockholders_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total stockholders' equity |
| total_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities |
| common_stock | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Common stock |
| preferred_stock | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Preferred stock |
| accumulated_other_comprehensive_income_loss | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accumulated other comprehensive income (loss) |
| retained_earnings | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Retained earnings |
| minority_interest | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Minority interest |
| total_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total equity |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | Date of the fetched statement. |
| cik | Union[str] | Central Index Key (CIK) of the company. |
| currency | Union[str] | Reporting currency. |
| filling_date | Union[date] | Filling date. |
| accepted_date | Union[datetime] | Accepted date. |
| period | Union[str] | Reporting period of the statement. |
| cash_and_cash_equivalents | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Cash and cash equivalents |
| short_term_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Short-term investments |
| long_term_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Long-term investments |
| inventory | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Inventory |
| net_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Receivables, net |
| marketable_securities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Marketable securities |
| property_plant_equipment_net | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Property, plant and equipment, net |
| goodwill | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Goodwill |
| assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total assets |
| current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total current assets |
| other_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other current assets |
| intangible_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Intangible assets |
| tax_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes |
| other_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other assets |
| non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total non-current assets |
| other_non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other non-current assets |
| account_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accounts payable |
| tax_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes |
| deferred_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accrued income taxes, other deferred revenue |
| total_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total assets |
| long_term_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities |
| other_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other current liabilities |
| current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total current liabilities |
| total_liabilities_and_total_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities and total equity |
| other_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other liabilities |
| other_non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other non-current liabilities |
| non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities and stockholders' equity |
| other_stockholder_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Other stockholders equity |
| total_stockholders_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total stockholders' equity |
| total_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total liabilities |
| common_stock | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Common stock |
| preferred_stock | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Preferred stock |
| accumulated_other_comprehensive_income_loss | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Accumulated other comprehensive income (loss) |
| retained_earnings | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Retained earnings |
| minority_interest | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Minority interest |
| total_equity | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total equity |
| calendar_year | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Calendar Year |
| cash_and_short_term_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Cash and Short Term Investments |
| goodwill_and_intangible_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Goodwill and Intangible Assets |
| deferred_revenue_non_current | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Deferred Revenue Non Current |
| total_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total investments |
| capital_lease_obligations | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Capital lease obligations |
| deferred_tax_liabilities_non_current | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Deferred Tax Liabilities Non Current |
| total_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Total Debt |
| net_debt | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7febe2bb23a0>)]] | Net Debt |
| link | Union[str] | Link to the statement. |
| final_link | Union[str] | Link to the final statement. |
</TabItem>

</Tabs>

