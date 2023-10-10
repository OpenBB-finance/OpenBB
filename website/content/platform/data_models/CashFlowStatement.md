---
title: CashFlowStatement
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
| year | Union[int] | Year of the statement to be fetched. |  | False |
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
| period | Union[str] | Reporting period of the statement. |
| cik | Union[str] | Central Index Key (CIK) of the company. |
| net_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net income. |
| depreciation_and_amortization | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Depreciation and amortization. |
| stock_based_compensation | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Stock based compensation. |
| deferred_income_tax | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Deferred income tax. |
| other_non_cash_items | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Changes in operating assets and liabilities. |
| accounts_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Accounts receivables. |
| inventory | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Inventory. |
| vendor_non_trade_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Vendor non-trade receivables. |
| other_current_and_non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other current and non-current assets. |
| accounts_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Accounts payables. |
| deferred_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Deferred revenue. |
| other_current_and_non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash flow from operating activities. |
| purchases_of_marketable_securities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Purchases of investments. |
| sales_from_maturities_of_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Investments in property, plant, and equipment. |
| payments_from_acquisitions | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Acquisitions, net of cash acquired, and other |
| other_investing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other investing activities |
| net_cash_flow_from_investing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Taxes paid on net share settlement of equity awards. |
| dividends_paid | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments for dividends and dividend equivalents |
| common_stock_repurchased | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments related to repurchase of common stock |
| debt_proceeds | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Proceeds from issuance of term debt |
| debt_repayment | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments of long-term debt |
| other_financing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other financing activities, net |
| net_cash_flow_from_financing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash flow from financing activities. |
| net_change_in_cash | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net increase (decrease) in cash, cash equivalents, and restricted cash |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | Date of the fetched statement. |
| period | Union[str] | Reporting period of the statement. |
| cik | Union[str] | Central Index Key (CIK) of the company. |
| net_income | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net income. |
| depreciation_and_amortization | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Depreciation and amortization. |
| stock_based_compensation | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Stock based compensation. |
| deferred_income_tax | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Deferred income tax. |
| other_non_cash_items | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other non-cash items. |
| changes_in_operating_assets_and_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Changes in operating assets and liabilities. |
| accounts_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Accounts receivables. |
| inventory | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Inventory. |
| vendor_non_trade_receivables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Vendor non-trade receivables. |
| other_current_and_non_current_assets | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other current and non-current assets. |
| accounts_payables | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Accounts payables. |
| deferred_revenue | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Deferred revenue. |
| other_current_and_non_current_liabilities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other current and non-current liabilities. |
| net_cash_flow_from_operating_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash flow from operating activities. |
| purchases_of_marketable_securities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Purchases of investments. |
| sales_from_maturities_of_investments | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Sales and maturities of investments. |
| investments_in_property_plant_and_equipment | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Investments in property, plant, and equipment. |
| payments_from_acquisitions | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Acquisitions, net of cash acquired, and other |
| other_investing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other investing activities |
| net_cash_flow_from_investing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash used for investing activities. |
| taxes_paid_on_net_share_settlement | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Taxes paid on net share settlement of equity awards. |
| dividends_paid | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments for dividends and dividend equivalents |
| common_stock_repurchased | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments related to repurchase of common stock |
| debt_proceeds | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Proceeds from issuance of term debt |
| debt_repayment | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Payments of long-term debt |
| other_financing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other financing activities, net |
| net_cash_flow_from_financing_activities | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net cash flow from financing activities. |
| net_change_in_cash | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Net increase (decrease) in cash, cash equivalents, and restricted cash |
| reported_currency | str | Reported currency in the statement. |
| filling_date | date | Filling date. |
| accepted_date | datetime | Accepted date. |
| calendar_year | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Calendar year. |
| change_in_working_capital | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Change in working capital. |
| other_working_capital | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Other working capital. |
| common_stock_issued | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Common stock issued. |
| effect_of_forex_changes_on_cash | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Effect of forex changes on cash. |
| cash_at_beginning_of_period | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Cash at beginning of period. |
| cash_at_end_of_period | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Cash, cash equivalents, and restricted cash at end of period |
| operating_cash_flow | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Operating cash flow. |
| capital_expenditure | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Capital expenditure. |
| free_cash_flow | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Free cash flow. |
| link | Union[str] | Link to the statement. |
| final_link | Union[str] | Link to the final statement. |
</TabItem>

</Tabs>

