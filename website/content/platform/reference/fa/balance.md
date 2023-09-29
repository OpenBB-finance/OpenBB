---
title: balance
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# balance

Balance Sheet.

```python wordwrap
balance(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: NonNegativeInt = 12, provider: Literal[str] = fmp)
```

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

---

## Returns

```python wordwrap
OBBject
    results : List[BalanceSheet]
        Serializable results.

    provider : Optional[Literal['fmp', 'polygon', 'yfinance']]
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
| symbol | str | Symbol to get data for. |
| date | date | Date of the fetched statement. |
| period | str | Reporting period of the statement. |
| cik | int | Central Index Key (CIK) of the company. |
| cash_and_cash_equivalents | int | Cash and cash equivalents |
| short_term_investments | int | Short-term investments |
| net_receivables | int | Receivables, net |
| inventory | int | Inventory |
| other_current_assets | int | Other current assets |
| total_current_assets | int | Total current assets |
| marketable_securities | int | Marketable securities |
| property_plant_equipment_net | int | Property, plant and equipment, net |
| goodwill | int | Goodwill |
| intangible_assets | int | Intangible assets |
| tax_assets | int | Accrued income taxes |
| other_non_current_assets | int | Other non-current assets |
| total_non_current_assets | int | Total non-current assets |
| other_assets | int | Other assets |
| total_assets | int | Total assets |
| account_payables | int | Accounts payables |
| short_term_debt | int | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| tax_payables | int | Accrued income taxes |
| deferred_revenue | int | Accrued income taxes, other deferred revenue |
| other_current_liabilities | int | Other current liabilities |
| total_current_liabilities | int | Total current liabilities |
| long_term_debt | int | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| deferred_revenue_non_current | int | Deferred revenue, non-current |
| deferred_tax_liabilities_non_current | int | Deferred income taxes and other |
| other_non_current_liabilities | int | Deferred income taxes and other |
| total_non_current_liabilities | int | Total non-current liabilities |
| other_liabilities | int | Other liabilities |
| total_liabilities | int | Total liabilities |
| preferred_stock | int | Preferred stock |
| common_stock | int | Common stock |
| retained_earnings | int | Retained earnings |
| accumulated_other_comprehensive_income_loss | int | Accumulated other comprehensive income (loss) |
| other_shareholder_equity | int | Other shareholder's equity |
| total_shareholder_equity | int | Total shareholder's equity |
| total_equity | int | Total equity |
| total_liabilities_and_shareholders_equity | int | Total liabilities and shareholder's equity |
| minority_interest | int | Minority interest |
| total_liabilities_and_total_equity | int | Total liabilities and total equity |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| reported_currency | str | Reported currency in the statement. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| calendar_year | int | Calendar year. |
| cash_and_short_term_investments | int | Cash and short term investments |
| goodwill_and_intangible_assets | int | Goodwill and Intangible Assets |
| capital_lease_obligations | int | Capital lease obligations |
| total_investments | int | Total investments |
| total_debt | int | Total debt |
| net_debt | int | Net debt |
| link | str | Link to the statement. |
| final_link | str | Link to the final statement. |
</TabItem>

</Tabs>

