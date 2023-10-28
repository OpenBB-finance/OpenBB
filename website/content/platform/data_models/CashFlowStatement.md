---
title: Cash Flow Statement
description: This document helps understand how the standard models like CashFlowStatement,
  CashFlowStatementQueryParams, and CashFlowStatementData are used to retrieve financial
  data. It provides clear guidelines on how to use the query parameters to fetch data
  from different finance data providers like fmp, intrinio, and polygon.
keywords:
- CashFlowStatement
- CashFlowStatementQueryParams
- CashFlowStatementData
- Docusaurus
- Python
- financial models
- economic data
- query parameters
- finance
- financial reporting
- financial data providers
- fmp
- intrinio
- polygon
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Cash Flow Statement - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CashFlowStatement` | `CashFlowStatementQueryParams` | `CashFlowStatementData` |

### Import Statement

```python
from openbb_provider.standard_models.cash_flow import (
CashFlowStatementData,
CashFlowStatementQueryParams,
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
| year | int | Year of the statement to be fetched. |  | False |
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
| date | date | Date of the fetched statement. |
| period | str | Reporting period of the statement. |
| cik | str | Central Index Key (CIK) of the company. |
| net_income | int | Net income. |
| depreciation_and_amortization | int | Depreciation and amortization. |
| stock_based_compensation | int | Stock based compensation. |
| deferred_income_tax | int | Deferred income tax. |
| other_non_cash_items | int | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | int | Changes in operating assets and liabilities. |
| accounts_receivables | int | Accounts receivables. |
| inventory | int | Inventory. |
| vendor_non_trade_receivables | int | Vendor non-trade receivables. |
| other_current_and_non_current_assets | int | Other current and non-current assets. |
| accounts_payables | int | Accounts payables. |
| deferred_revenue | int | Deferred revenue. |
| other_current_and_non_current_liabilities | int | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | int | Net cash flow from operating activities. |
| purchases_of_marketable_securities | int | Purchases of investments. |
| sales_from_maturities_of_investments | int | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | int | Investments in property, plant, and equipment. |
| payments_from_acquisitions | int | Acquisitions, net of cash acquired, and other |
| other_investing_activities | int | Other investing activities |
| net_cash_flow_from_investing_activities | int | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | int | Taxes paid on net share settlement of equity awards. |
| dividends_paid | int | Payments for dividends and dividend equivalents |
| common_stock_repurchased | int | Payments related to repurchase of common stock |
| debt_proceeds | int | Proceeds from issuance of term debt |
| debt_repayment | int | Payments of long-term debt |
| other_financing_activities | int | Other financing activities, net |
| net_cash_flow_from_financing_activities | int | Net cash flow from financing activities. |
| net_change_in_cash | int | Net increase (decrease) in cash, cash equivalents, and restricted cash |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | date | Date of the fetched statement. |
| period | str | Reporting period of the statement. |
| cik | str | Central Index Key (CIK) of the company. |
| net_income | int | Net income. |
| depreciation_and_amortization | int | Depreciation and amortization. |
| stock_based_compensation | int | Stock based compensation. |
| deferred_income_tax | int | Deferred income tax. |
| other_non_cash_items | int | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | int | Changes in operating assets and liabilities. |
| accounts_receivables | int | Accounts receivables. |
| inventory | int | Inventory. |
| vendor_non_trade_receivables | int | Vendor non-trade receivables. |
| other_current_and_non_current_assets | int | Other current and non-current assets. |
| accounts_payables | int | Accounts payables. |
| deferred_revenue | int | Deferred revenue. |
| other_current_and_non_current_liabilities | int | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | int | Net cash flow from operating activities. |
| purchases_of_marketable_securities | int | Purchases of investments. |
| sales_from_maturities_of_investments | int | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | int | Investments in property, plant, and equipment. |
| payments_from_acquisitions | int | Acquisitions, net of cash acquired, and other |
| other_investing_activities | int | Other investing activities |
| net_cash_flow_from_investing_activities | int | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | int | Taxes paid on net share settlement of equity awards. |
| dividends_paid | int | Payments for dividends and dividend equivalents |
| common_stock_repurchased | int | Payments related to repurchase of common stock |
| debt_proceeds | int | Proceeds from issuance of term debt |
| debt_repayment | int | Payments of long-term debt |
| other_financing_activities | int | Other financing activities, net |
| net_cash_flow_from_financing_activities | int | Net cash flow from financing activities. |
| net_change_in_cash | int | Net increase (decrease) in cash, cash equivalents, and restricted cash |
| reported_currency | str | Reported currency in the statement. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| calendar_year | int | Calendar year. |
| change_in_working_capital | int | Change in working capital. |
| other_working_capital | int | Other working capital. |
| common_stock_issued | int | Common stock issued. |
| effect_of_forex_changes_on_cash | int | Effect of forex changes on cash. |
| cash_at_beginning_of_period | int | Cash at beginning of period. |
| cash_at_end_of_period | int | Cash, cash equivalents, and restricted cash at end of period |
| operating_cash_flow | int | Operating cash flow. |
| capital_expenditure | int | Capital expenditure. |
| free_cash_flow | int | Free cash flow. |
| link | str | Link to the statement. |
| final_link | str | Link to the final statement. |
</TabItem>

</Tabs>
