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
=OBB.EQUITY.FUNDAMENTAL.CASH( symbol; [provider]; [period]; [limit]; [cik]; [filing_date]; [filing_date_lt]; [filing_date_lte]; [filing_date_gt]; [filing_date_gte]; [period_of_report_date]; [period_of_report_date_lt]; [period_of_report_date_lte]; [period_of_report_date_gt]; [period_of_report_date_gte]; [include_sources]; [order]; [sort] )
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
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
| period_ending | The end date of the reporting period.  |
| fiscal_period | The fiscal period of the report.  |
| fiscal_year | The fiscal year of the fiscal period.  |
| filingDate | The date of the filing. (provider: fmp) |
| acceptedDate | The date the filing was accepted. (provider: fmp) |
| reported_currency | The currency in which the cash flow statement was reported. (provider: fmp);     The currency in which the balance sheet is reported. (provider: intrinio) |
| net_income | Net income. (provider: fmp);     Consolidated Net Income. (provider: intrinio) |
| depreciationAndAmortization | Depreciation and amortization. (provider: fmp) |
| deferredIncomeTax | Deferred income tax. (provider: fmp) |
| stockBasedCompensation | Stock-based compensation. (provider: fmp) |
| changeInWorkingCapital | Change in working capital. (provider: fmp) |
| changeInAccountReceivables | Change in account receivables. (provider: fmp) |
| changeInInventory | Change in inventory. (provider: fmp) |
| changeInAccountPayable | Change in account payable. (provider: fmp) |
| changeInOtherWorkingCapital | Change in other working capital. (provider: fmp) |
| changeInOtherNonCashItems | Change in other non-cash items. (provider: fmp) |
| net_cash_from_operating_activities | Net cash from operating activities. (provider: fmp, intrinio) |
| purchase_of_property_plant_and_equipment | Purchase of property, plant and equipment. (provider: fmp, intrinio) |
| acquisitions | Acquisitions. (provider: fmp, intrinio) |
| purchase_of_investment_securities | Purchase of investment securities. (provider: fmp, intrinio) |
| sale_and_maturity_of_investments | Sale and maturity of investments. (provider: fmp, intrinio) |
| other_investing_activities | Other investing activities. (provider: fmp, intrinio) |
| net_cash_from_investing_activities | Net cash from investing activities. (provider: fmp, intrinio) |
| repayment_of_debt | Repayment of debt. (provider: fmp, intrinio) |
| issuance_of_common_equity | Issuance of common equity. (provider: fmp, intrinio) |
| repurchase_of_common_equity | Repurchase of common equity. (provider: fmp, intrinio) |
| payment_of_dividends | Payment of dividends. (provider: fmp, intrinio) |
| other_financing_activities | Other financing activities. (provider: fmp, intrinio) |
| net_cash_from_financing_activities | Net cash from financing activities. (provider: fmp, intrinio) |
| effectOfExchangeRateChangesOnCash | Effect of exchange rate changes on cash. (provider: fmp) |
| net_change_in_cash_and_equivalents | Net change in cash and equivalents. (provider: fmp, intrinio) |
| cashAtBeginningOfPeriod | Cash at beginning of period. (provider: fmp) |
| cashAtEndOfPeriod | Cash at end of period. (provider: fmp) |
| operatingCashFlow | Operating cash flow. (provider: fmp) |
| capitalExpenditure | Capital expenditure. (provider: fmp) |
| freeCashFlow | None |
| link | Link to the filing. (provider: fmp) |
| finalLink | Link to the filing document. (provider: fmp) |
| provisionForLoanLosses | Provision for Loan Losses (provider: intrinio) |
| provision_for_credit_losses | Provision for credit losses (provider: intrinio) |
| depreciationExpense | Depreciation Expense. (provider: intrinio) |
| amortizationExpense | Amortization Expense. (provider: intrinio) |
| share_based_compensation | Share-based compensation. (provider: intrinio) |
| nonCashAdjustmentsToReconcileNetIncome | Non-Cash Adjustments to Reconcile Net Income. (provider: intrinio) |
| changesInOperatingAssetsAndLiabilities | Changes in Operating Assets and Liabilities (Net) (provider: intrinio) |
| netCashFromContinuingOperatingActivities | Net Cash from Continuing Operating Activities (provider: intrinio) |
| netCashFromDiscontinuedOperatingActivities | Net Cash from Discontinued Operating Activities (provider: intrinio) |
| netIncomeContinuingOperations | Net Income (Continuing Operations) (provider: intrinio) |
| netIncomeDiscontinuedOperations | Net Income (Discontinued Operations) (provider: intrinio) |
| divestitures | Divestitures (provider: intrinio) |
| saleOfPropertyPlantAndEquipment | Sale of Property, Plant, and Equipment (provider: intrinio) |
| purchaseOfInvestments | Purchase of Investments (provider: intrinio) |
| loansHeldForSale | Loans Held for Sale (Net) (provider: intrinio) |
| netCashFromContinuingInvestingActivities | Net Cash from Continuing Investing Activities (provider: intrinio) |
| netCashFromDiscontinuedInvestingActivities | Net Cash from Discontinued Investing Activities (provider: intrinio) |
| repurchaseOfPreferredEquity | Repurchase of Preferred Equity (provider: intrinio) |
| issuanceOfPreferredEquity | Issuance of Preferred Equity (provider: intrinio) |
| issuanceOfDebt | Issuance of Debt (provider: intrinio) |
| cashInterestReceived | Cash Interest Received (provider: intrinio) |
| netChangeInDeposits | Net Change in Deposits (provider: intrinio) |
| netIncreaseInFedFundsSold | Net Increase in Fed Funds Sold (provider: intrinio) |
| netCashFromContinuingFinancingActivities | Net Cash from Continuing Financing Activities (provider: intrinio) |
| netCashFromDiscontinuedFinancingActivities | Net Cash from Discontinued Financing Activities (provider: intrinio) |
| effectOfExchangeRateChanges | Effect of Exchange Rate Changes (provider: intrinio) |
| otherNetChangesInCash | Other Net Changes in Cash (provider: intrinio) |
| cashIncomeTaxesPaid | Cash Income Taxes Paid (provider: intrinio) |
| cashInterestPaid | Cash Interest Paid (provider: intrinio) |
| net_cash_flow_from_operating_activities_continuing | Net cash flow from operating activities continuing. (provider: polygon) |
| net_cash_flow_from_operating_activities_discontinued | Net cash flow from operating activities discontinued. (provider: polygon) |
| net_cash_flow_from_operating_activities | Net cash flow from operating activities. (provider: polygon) |
| net_cash_flow_from_investing_activities_continuing | Net cash flow from investing activities continuing. (provider: polygon) |
| net_cash_flow_from_investing_activities_discontinued | Net cash flow from investing activities discontinued. (provider: polygon) |
| net_cash_flow_from_investing_activities | Net cash flow from investing activities. (provider: polygon) |
| net_cash_flow_from_financing_activities_continuing | Net cash flow from financing activities continuing. (provider: polygon) |
| net_cash_flow_from_financing_activities_discontinued | Net cash flow from financing activities discontinued. (provider: polygon) |
| net_cash_flow_from_financing_activities | Net cash flow from financing activities. (provider: polygon) |
| net_cash_flow_continuing | Net cash flow continuing. (provider: polygon) |
| net_cash_flow_discontinued | Net cash flow discontinued. (provider: polygon) |
| exchange_gains_losses | Exchange gains losses. (provider: polygon) |
| net_cash_flow | Net cash flow. (provider: polygon) |
---

## Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.CASH( "AAPL" )
```

