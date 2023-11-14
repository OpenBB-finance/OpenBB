---
title: balance
description: Learn how to use the balance sheet function in Python to retrieve financial
  statement data. This documentation provides details about the function parameters,
  return values, and available data types.
keywords:
- balance sheet statement
- balance sheet function
- python function
- financial statement function
- balance sheet data parameters
- balance sheet data returns
- balance sheet data types
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Balance Sheet. Balance sheet statement.

```python wordwrap
obb.equity.fundamental.balance(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 5, provider: Literal[str] = fmp)
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
| cik | str | Central Index Key (CIK) of the company. | None | True |
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
    results : List[BalanceSheet]
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
| date | date | The date of the data. |
| cik | str | Central Index Key (CIK) of the company. |
| currency | str | Reporting currency. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| period | str | Reporting period of the statement. |
| cash_and_cash_equivalents | float | Cash and cash equivalents |
| short_term_investments | float | Short-term investments |
| long_term_investments | float | Long-term investments |
| inventory | float | Inventory |
| net_receivables | float | Receivables, net |
| marketable_securities | float | Marketable securities |
| property_plant_equipment_net | float | Property, plant and equipment, net |
| goodwill | float | Goodwill |
| assets | float | Total assets |
| current_assets | float | Total current assets |
| other_current_assets | float | Other current assets |
| intangible_assets | float | Intangible assets |
| tax_assets | float | Accrued income taxes |
| non_current_assets | float | Total non-current assets |
| other_non_current_assets | float | Other non-current assets |
| account_payables | float | Accounts payable |
| tax_payables | float | Accrued income taxes |
| deferred_revenue | float | Accrued income taxes, other deferred revenue |
| other_assets | float | Other assets |
| total_assets | float | Total assets |
| long_term_debt | float | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | float | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | float | Total liabilities |
| other_current_liabilities | float | Other current liabilities |
| current_liabilities | float | Total current liabilities |
| total_liabilities_and_total_equity | float | Total liabilities and total equity |
| other_non_current_liabilities | float | Other non-current liabilities |
| non_current_liabilities | float | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | float | Total liabilities and stockholders' equity |
| other_stockholder_equity | float | Other stockholders equity |
| total_stockholders_equity | float | Total stockholders' equity |
| other_liabilities | float | Other liabilities |
| total_liabilities | float | Total liabilities |
| common_stock | float | Common stock |
| preferred_stock | float | Preferred stock |
| accumulated_other_comprehensive_income_loss | float | Accumulated other comprehensive income (loss) |
| retained_earnings | float | Retained earnings |
| minority_interest | float | Minority interest |
| total_equity | float | Total equity |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| cik | str | Central Index Key (CIK) of the company. |
| currency | str | Reporting currency. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| period | str | Reporting period of the statement. |
| cash_and_cash_equivalents | float | Cash and cash equivalents |
| short_term_investments | float | Short-term investments |
| long_term_investments | float | Long-term investments |
| inventory | float | Inventory |
| net_receivables | float | Receivables, net |
| marketable_securities | float | Marketable securities |
| property_plant_equipment_net | float | Property, plant and equipment, net |
| goodwill | float | Goodwill |
| assets | float | Total assets |
| current_assets | float | Total current assets |
| other_current_assets | float | Other current assets |
| intangible_assets | float | Intangible assets |
| tax_assets | float | Accrued income taxes |
| non_current_assets | float | Total non-current assets |
| other_non_current_assets | float | Other non-current assets |
| account_payables | float | Accounts payable |
| tax_payables | float | Accrued income taxes |
| deferred_revenue | float | Accrued income taxes, other deferred revenue |
| other_assets | float | Other assets |
| total_assets | float | Total assets |
| long_term_debt | float | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | float | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | float | Total liabilities |
| other_current_liabilities | float | Other current liabilities |
| current_liabilities | float | Total current liabilities |
| total_liabilities_and_total_equity | float | Total liabilities and total equity |
| other_non_current_liabilities | float | Other non-current liabilities |
| non_current_liabilities | float | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | float | Total liabilities and stockholders' equity |
| other_stockholder_equity | float | Other stockholders equity |
| total_stockholders_equity | float | Total stockholders' equity |
| other_liabilities | float | Other liabilities |
| total_liabilities | float | Total liabilities |
| common_stock | float | Common stock |
| preferred_stock | float | Preferred stock |
| accumulated_other_comprehensive_income_loss | float | Accumulated other comprehensive income (loss) |
| retained_earnings | float | Retained earnings |
| minority_interest | float | Minority interest |
| total_equity | float | Total equity |
| calendar_year | int | Calendar Year |
| cash_and_short_term_investments | int | Cash and Short Term Investments |
| goodwill_and_intangible_assets | int | Goodwill and Intangible Assets |
| deferred_revenue_non_current | int | Deferred Revenue Non Current |
| total_investments | int | Total investments |
| capital_lease_obligations | int | Capital lease obligations |
| deferred_tax_liabilities_non_current | int | Deferred Tax Liabilities Non Current |
| total_debt | int | Total Debt |
| net_debt | int | Net Debt |
| link | str | Link to the statement. |
| final_link | str | Link to the final statement. |
</TabItem>

</Tabs>

