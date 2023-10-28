---
title: balance
description: The balance page provides a comprehensive guide on how to obtain information
  about a company's balance sheet. It offers various parameters you can use to fetch
  data from different providers like FMP, Intrinio, or Polygon. The documentation
  is detailed, offering full information about returns, data types, defaults, and
  optional parameters.
keywords:
- balance sheet
- financial data
- parameters
- data providers
- FMP
- Intrinio
- Polygon
- symbol
- period
- CIK
- type
- year
- company name
- SIC
- filing date
- report date
- sources
- order
- sort
- Docusaurus page optimization
- SEO for Docusaurus
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.balance - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Balance Sheet. Balance sheet statement.

```python wordwrap
balance(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 12, provider: Literal[str] = fmp)
```

---

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
| cik | str | Central Index Key (CIK) of the company. | None | True |
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

---

## Returns

```python wordwrap
OBBject
    results : List[BalanceSheet]
        Serializable results.

    provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
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
| cik | str | Central Index Key (CIK) of the company. |
| currency | str | Reporting currency. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| period | str | Reporting period of the statement. |
| cash_and_cash_equivalents | int | Cash and cash equivalents |
| short_term_investments | int | Short-term investments |
| long_term_investments | int | Long-term investments |
| inventory | int | Inventory |
| net_receivables | int | Receivables, net |
| marketable_securities | int | Marketable securities |
| property_plant_equipment_net | int | Property, plant and equipment, net |
| goodwill | int | Goodwill |
| assets | int | Total assets |
| current_assets | int | Total current assets |
| other_current_assets | int | Other current assets |
| intangible_assets | int | Intangible assets |
| tax_assets | int | Accrued income taxes |
| other_assets | int | Other assets |
| non_current_assets | int | Total non-current assets |
| other_non_current_assets | int | Other non-current assets |
| account_payables | int | Accounts payable |
| tax_payables | int | Accrued income taxes |
| deferred_revenue | int | Accrued income taxes, other deferred revenue |
| total_assets | int | Total assets |
| long_term_debt | int | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | int | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | int | Total liabilities |
| other_current_liabilities | int | Other current liabilities |
| current_liabilities | int | Total current liabilities |
| total_liabilities_and_total_equity | int | Total liabilities and total equity |
| other_liabilities | int | Other liabilities |
| other_non_current_liabilities | int | Other non-current liabilities |
| non_current_liabilities | int | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | int | Total liabilities and stockholders' equity |
| other_stockholder_equity | int | Other stockholders equity |
| total_stockholders_equity | int | Total stockholders' equity |
| total_liabilities | int | Total liabilities |
| common_stock | int | Common stock |
| preferred_stock | int | Preferred stock |
| accumulated_other_comprehensive_income_loss | int | Accumulated other comprehensive income (loss) |
| retained_earnings | int | Retained earnings |
| minority_interest | int | Minority interest |
| total_equity | int | Total equity |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | date | Date of the fetched statement. |
| cik | str | Central Index Key (CIK) of the company. |
| currency | str | Reporting currency. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| period | str | Reporting period of the statement. |
| cash_and_cash_equivalents | int | Cash and cash equivalents |
| short_term_investments | int | Short-term investments |
| long_term_investments | int | Long-term investments |
| inventory | int | Inventory |
| net_receivables | int | Receivables, net |
| marketable_securities | int | Marketable securities |
| property_plant_equipment_net | int | Property, plant and equipment, net |
| goodwill | int | Goodwill |
| assets | int | Total assets |
| current_assets | int | Total current assets |
| other_current_assets | int | Other current assets |
| intangible_assets | int | Intangible assets |
| tax_assets | int | Accrued income taxes |
| other_assets | int | Other assets |
| non_current_assets | int | Total non-current assets |
| other_non_current_assets | int | Other non-current assets |
| account_payables | int | Accounts payable |
| tax_payables | int | Accrued income taxes |
| deferred_revenue | int | Accrued income taxes, other deferred revenue |
| total_assets | int | Total assets |
| long_term_debt | int | Long-term debt, Operating lease obligations, Long-term finance lease obligations |
| short_term_debt | int | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year |
| liabilities | int | Total liabilities |
| other_current_liabilities | int | Other current liabilities |
| current_liabilities | int | Total current liabilities |
| total_liabilities_and_total_equity | int | Total liabilities and total equity |
| other_liabilities | int | Other liabilities |
| other_non_current_liabilities | int | Other non-current liabilities |
| non_current_liabilities | int | Total non-current liabilities |
| total_liabilities_and_stockholders_equity | int | Total liabilities and stockholders' equity |
| other_stockholder_equity | int | Other stockholders equity |
| total_stockholders_equity | int | Total stockholders' equity |
| total_liabilities | int | Total liabilities |
| common_stock | int | Common stock |
| preferred_stock | int | Preferred stock |
| accumulated_other_comprehensive_income_loss | int | Accumulated other comprehensive income (loss) |
| retained_earnings | int | Retained earnings |
| minority_interest | int | Minority interest |
| total_equity | int | Total equity |
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
