---
title: Cash Flow Statement
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models.cash_flow import (
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

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Reporting period of the statement. |
| cik | str | Central Index Key (CIK) of the company. |
| net_income | float | Net income. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| stock_based_compensation | float | Stock based compensation. |
| deferred_income_tax | float | Deferred income tax. |
| other_non_cash_items | float | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | float | Changes in operating assets and liabilities. |
| accounts_receivables | float | Accounts receivables. |
| inventory | float | Inventory. |
| vendor_non_trade_receivables | float | Vendor non-trade receivables. |
| other_current_and_non_current_assets | float | Other current and non-current assets. |
| accounts_payables | float | Accounts payables. |
| deferred_revenue | float | Deferred revenue. |
| other_current_and_non_current_liabilities | float | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | float | Net cash flow from operating activities. |
| purchases_of_marketable_securities | float | Purchases of investments. |
| sales_from_maturities_of_investments | float | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | float | Investments in property, plant, and equipment. |
| payments_from_acquisitions | float | Acquisitions, net of cash acquired, and other |
| other_investing_activities | float | Other investing activities |
| net_cash_flow_from_investing_activities | float | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | float | Taxes paid on net share settlement of equity awards. |
| dividends_paid | float | Payments for dividends and dividend equivalents |
| common_stock_repurchased | float | Payments related to repurchase of common stock |
| debt_proceeds | float | Proceeds from issuance of term debt |
| debt_repayment | float | Payments of long-term debt |
| other_financing_activities | float | Other financing activities, net |
| net_cash_flow_from_financing_activities | float | Net cash flow from financing activities. |
| net_change_in_cash | float | Net increase (decrease) in cash, cash equivalents, and restricted cash |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Reporting period of the statement. |
| cik | str | Central Index Key (CIK) of the company. |
| net_income | float | Net income. |
| depreciation_and_amortization | float | Depreciation and amortization. |
| stock_based_compensation | float | Stock based compensation. |
| deferred_income_tax | float | Deferred income tax. |
| other_non_cash_items | float | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | float | Changes in operating assets and liabilities. |
| accounts_receivables | float | Accounts receivables. |
| inventory | float | Inventory. |
| vendor_non_trade_receivables | float | Vendor non-trade receivables. |
| other_current_and_non_current_assets | float | Other current and non-current assets. |
| accounts_payables | float | Accounts payables. |
| deferred_revenue | float | Deferred revenue. |
| other_current_and_non_current_liabilities | float | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | float | Net cash flow from operating activities. |
| purchases_of_marketable_securities | float | Purchases of investments. |
| sales_from_maturities_of_investments | float | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | float | Investments in property, plant, and equipment. |
| payments_from_acquisitions | float | Acquisitions, net of cash acquired, and other |
| other_investing_activities | float | Other investing activities |
| net_cash_flow_from_investing_activities | float | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | float | Taxes paid on net share settlement of equity awards. |
| dividends_paid | float | Payments for dividends and dividend equivalents |
| common_stock_repurchased | float | Payments related to repurchase of common stock |
| debt_proceeds | float | Proceeds from issuance of term debt |
| debt_repayment | float | Payments of long-term debt |
| other_financing_activities | float | Other financing activities, net |
| net_cash_flow_from_financing_activities | float | Net cash flow from financing activities. |
| net_change_in_cash | float | Net increase (decrease) in cash, cash equivalents, and restricted cash |
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
