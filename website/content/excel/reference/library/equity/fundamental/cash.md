---
title: cash
description: Learn how to use the Cash Flow Statement API endpoint to retrieve information
  about cash flow statements. Understand the parameters and return values of the API,
  and explore the available data fields for cash flow statements.
keywords: 
- Cash Flow Statement
- cash flow statement parameters
- cash flow statement returns
- cash flow statement data
- python obb.equity.fundamental.cash
- symbol
- period
- limit
- provider
- cik
- filing date
- period of report date
- include sources
- order
- sort
- net income
- depreciation and amortization
- stock based compensation
- deferred income tax
- other non-cash items
- changes in operating assets and liabilities
- accounts receivables
- inventory
- vendor non-trade receivables
- other current and non-current assets
- accounts payables
- deferred revenue
- other current and non-current liabilities
- net cash flow from operating activities
- purchases of marketable securities
- sales from maturities of investments
- investments in property plant and equipment
- payments from acquisitions
- other investing activities
- net cash flow from investing activities
- taxes paid on net share settlement
- dividends paid
- common stock repurchased
- debt proceeds
- debt repayment
- other financing activities
- net cash flow from financing activities
- net change in cash
---

<!-- markdownlint-disable MD041 -->

Cash Flow Statement. Information about the cash flow statement.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.CASH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio, polygon | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| cik | Text | Central Index Key (CIK) of the company. (provider: fmp) | True |
| filing_date | Text | Filing date of the financial statement. (provider: polygon) | True |
| filing_date_lt | Text | Filing date less than the given date. (provider: polygon) | True |
| filing_date_lte | Text | Filing date less than or equal to the given date. (provider: polygon) | True |
| filing_date_gt | Text | Filing date greater than the given date. (provider: polygon) | True |
| filing_date_gte | Text | Filing date greater than or equal to the given date. (provider: polygon) | True |
| period_of_report_date | Text | Period of report date of the financial statement. (provider: polygon) | True |
| period_of_report_date_lt | Text | Period of report date less than the given date. (provider: polygon) | True |
| period_of_report_date_lte | Text | Period of report date less than or equal to the given date. (provider: polygon) | True |
| period_of_report_date_gt | Text | Period of report date greater than the given date. (provider: polygon) | True |
| period_of_report_date_gte | Text | Period of report date greater than or equal to the given date. (provider: polygon) | True |
| include_sources | Boolean | Whether to include the sources of the financial statement. (provider: polygon) | True |
| order | Text | Order of the financial statement. (provider: polygon) | True |
| sort | Text | Sort of the financial statement. (provider: polygon) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| period | Reporting period of the statement.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| net_income | Net income.  |
| depreciation_and_amortization | Depreciation and amortization.  |
| stock_based_compensation | Stock based compensation.  |
| deferred_income_tax | Deferred income tax.  |
| other_non_cash_items | Other non-cash items.  |
| changes_in_operating_assets_and_liabilities | Changes in operating assets and liabilities.  |
| accounts_receivables | Accounts receivables.  |
| inventory | Inventory.  |
| vendor_non_trade_receivables | Vendor non-trade receivables.  |
| other_current_and_non_current_assets | Other current and non-current assets.  |
| accounts_payables | Accounts payables.  |
| deferred_revenue | Deferred revenue.  |
| other_current_and_non_current_liabilities | Other current and non-current liabilities.  |
| net_cash_flow_from_operating_activities | Net cash flow from operating activities.  |
| purchases_of_marketable_securities | Purchases of investments.  |
| sales_from_maturities_of_investments | Sales and maturities of investments.  |
| investments_in_property_plant_and_equipment | Investments in property, plant, and equipment.  |
| payments_from_acquisitions | Acquisitions, net of cash acquired, and other  |
| other_investing_activities | Other investing activities  |
| net_cash_flow_from_investing_activities | Net cash used for investing activities.  |
| taxes_paid_on_net_share_settlement | Taxes paid on net share settlement of equity awards.  |
| dividends_paid | Payments for dividends and dividend equivalents  |
| common_stock_repurchased | Payments related to repurchase of common stock  |
| debt_proceeds | Proceeds from issuance of term debt  |
| debt_repayment | Payments of long-term debt  |
| other_financing_activities | Other financing activities, net  |
| net_cash_flow_from_financing_activities | Net cash flow from financing activities.  |
| net_change_in_cash | Net increase (decrease) in cash, cash equivalents, and restricted cash  |
| reportedCurrency | Reported currency in the statement. (provider: fmp) |
| filling_date | Filling date. (provider: fmp) |
| accepted_date | Accepted date. (provider: fmp) |
| calendar_year | Calendar year. (provider: fmp) |
| change_in_working_capital | Change in working capital. (provider: fmp) |
| other_working_capital | Other working capital. (provider: fmp) |
| common_stock_issued | Common stock issued. (provider: fmp) |
| effect_of_forex_changes_on_cash | Effect of forex changes on cash. (provider: fmp) |
| cash_at_beginning_of_period | Cash at beginning of period. (provider: fmp) |
| cash_at_end_of_period | Cash, cash equivalents, and restricted cash at end of period (provider: fmp) |
| operating_cash_flow | Operating cash flow. (provider: fmp) |
| capital_expenditure | Capital expenditure. (provider: fmp) |
| free_cash_flow | Free cash flow. (provider: fmp) |
| link | Link to the statement. (provider: fmp) |
| final_link | Link to the final statement. (provider: fmp) |
| net_income_continuing | Net income from continuing operations. (provider: intrinio) |
| net_cash_from_continuing_operating_activities | Net cash from continuing operating activities. (provider: intrinio) |
| net_cash_from_continuing_investing_activities | Net cash from continuing investing activities. (provider: intrinio) |
| net_cash_from_continuing_financing_activities | Net cash from continuing financing activities. (provider: intrinio) |
| cash_interest_paid | Cash paid for interest. (provider: intrinio) |
| cash_income_taxes_paid | Cash paid for income taxes. (provider: intrinio) |
| issuance_of_common_equity | Issuance of common equity. (provider: intrinio) |
