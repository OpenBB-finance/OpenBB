---
title: income
description: Get income statement and financial performance data for a company. Parameters
  include symbol, period, limit, provider, and more. Data includes revenue, gross
  profit, operating expenses, net income, and more.
keywords: 
- income statement
- financial performance
- get income data
- period
- limit
- provider
- symbol
- cik
- filing date
- period of report date
- include sources
- order
- sort
- revenue
- cost of revenue
- gross profit
- cost and expenses
- research and development expenses
- general and administrative expenses
- selling and marketing expenses
- other expenses
- operating expenses
- depreciation and amortization
- ebitda
- operating income
- interest income
- interest expense
- income before tax
- income tax expense
- net income
- eps
- weighted average shares outstanding
- link
- reported currency
- filling date
- accepted date
- calendar year
---

<!-- markdownlint-disable MD041 -->

Income Statement. Report on a company's financial performance.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME( symbol; [provider]; [period]; [limit]; [cik]; [filing_date]; [filing_date_lt]; [filing_date_lte]; [filing_date_gt]; [filing_date_gte]; [period_of_report_date]; [period_of_report_date_lt]; [period_of_report_date_lte]; [period_of_report_date_gt]; [period_of_report_date_gte]; [include_sources]; [order]; [sort] )
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| provider | Text | Options: fmp, intrinio, polygon | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| cik | Text | The CIK of the company if no symbol is provided. (provider: fmp) | True |
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
| filingDate | The date when the filing was made. (provider: fmp) |
| acceptedDate | The date and time when the filing was accepted. (provider: fmp) |
| reported_currency | The currency in which the balance sheet was reported. (provider: fmp, intrinio) |
| revenue | Total revenue. (provider: fmp, intrinio, polygon) |
| cost_of_revenue | Cost of revenue. (provider: fmp, intrinio, polygon) |
| gross_profit | Gross profit. (provider: fmp, intrinio, polygon) |
| gross_profit_margin | Gross profit margin. (provider: fmp);     Gross margin ratio. (provider: intrinio) |
| generalAndAdminExpense | General and administrative expenses. (provider: fmp) |
| research_and_development_expense | Research and development expenses. (provider: fmp, intrinio) |
| sellingAndMarketingExpense | Selling and marketing expenses. (provider: fmp) |
| selling_general_and_admin_expense | Selling, general and administrative expenses. (provider: fmp, intrinio) |
| otherExpenses | Other expenses. (provider: fmp) |
| total_operating_expenses | Total operating expenses. (provider: fmp, intrinio) |
| costAndExpenses | Cost and expenses. (provider: fmp) |
| interestIncome | Interest income. (provider: fmp) |
| total_interest_expense | Total interest expenses. (provider: fmp, intrinio);     Interest Expense (provider: polygon) |
| depreciation_and_amortization | Depreciation and amortization. (provider: fmp, polygon) |
| ebitda | EBITDA. (provider: fmp);     Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio) |
| ebitda_margin | EBITDA margin. (provider: fmp);     Margin on Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio) |
| total_operating_income | Total operating income. (provider: fmp, intrinio) |
| operatingIncomeMargin | Operating income margin. (provider: fmp) |
| totalOtherIncomeExpenses | Total other income and expenses. (provider: fmp) |
| total_pre_tax_income | Total pre-tax income. (provider: fmp, intrinio);     Income Before Tax (provider: polygon) |
| pre_tax_income_margin | Pre-tax income margin. (provider: fmp, intrinio) |
| income_tax_expense | Income tax expense. (provider: fmp, intrinio, polygon) |
| consolidated_net_income | Consolidated net income. (provider: fmp, intrinio);     Net Income/Loss (provider: polygon) |
| netIncomeMargin | Net income margin. (provider: fmp) |
| basic_earnings_per_share | Basic earnings per share. (provider: fmp, intrinio);     Earnings Per Share (provider: polygon) |
| diluted_earnings_per_share | Diluted earnings per share. (provider: fmp, intrinio, polygon) |
| weighted_average_basic_shares_outstanding | Weighted average basic shares outstanding. (provider: fmp, intrinio);     Basic Average Shares (provider: polygon) |
| weighted_average_diluted_shares_outstanding | Weighted average diluted shares outstanding. (provider: fmp, intrinio);     Diluted Average Shares (provider: polygon) |
| link | Link to the filing. (provider: fmp) |
| finalLink | Link to the filing document. (provider: fmp) |
| operatingRevenue | Total operating revenue (provider: intrinio) |
| operatingCostOfRevenue | Total operating cost of revenue (provider: intrinio) |
| provisionForCreditLosses | Provision for credit losses (provider: intrinio) |
| salariesAndEmployeeBenefits | Salaries and employee benefits (provider: intrinio) |
| marketingExpense | Marketing expense (provider: intrinio) |
| netOccupancyAndEquipmentExpense | Net occupancy and equipment expense (provider: intrinio) |
| other_operating_expenses | Other operating expenses (provider: intrinio, polygon) |
| depreciationExpense | Depreciation expense (provider: intrinio) |
| amortizationExpense | Amortization expense (provider: intrinio) |
| amortization_of_deferred_policy_acquisition_costs | Amortization of deferred policy acquisition costs (provider: intrinio) |
| explorationExpense | Exploration expense (provider: intrinio) |
| depletionExpense | Depletion expense (provider: intrinio) |
| depositsAndMoneyMarketInvestmentsInterestIncome | Deposits and money market investments interest income (provider: intrinio) |
| federalFundsSoldAndSecuritiesBorrowedInterestIncome | Federal funds sold and securities borrowed interest income (provider: intrinio) |
| investmentSecuritiesInterestIncome | Investment securities interest income (provider: intrinio) |
| loansAndLeasesInterestIncome | Loans and leases interest income (provider: intrinio) |
| tradingAccountInterestIncome | Trading account interest income (provider: intrinio) |
| otherInterestIncome | Other interest income (provider: intrinio) |
| totalNonInterestIncome | Total non-interest income (provider: intrinio) |
| interestAndInvestmentIncome | Interest and investment income (provider: intrinio) |
| shortTermBorrowingsInterestExpense | Short-term borrowings interest expense (provider: intrinio) |
| longTermDebtInterestExpense | Long-term debt interest expense (provider: intrinio) |
| capitalizedLeaseObligationsInterestExpense | Capitalized lease obligations interest expense (provider: intrinio) |
| depositsInterestExpense | Deposits interest expense (provider: intrinio) |
| federalFundsPurchasedAndSecuritiesSoldInterestExpense | Federal funds purchased and securities sold interest expense (provider: intrinio) |
| otherInterestExpense | Other interest expense (provider: intrinio) |
| net_interest_income | Net interest income (provider: intrinio);     Interest Income Net (provider: polygon) |
| otherNonInterestIncome | Other non-interest income (provider: intrinio) |
| investmentBankingIncome | Investment banking income (provider: intrinio) |
| trustFeesByCommissions | Trust fees by commissions (provider: intrinio) |
| premiumsEarned | Premiums earned (provider: intrinio) |
| insurancePolicyAcquisitionCosts | Insurance policy acquisition costs (provider: intrinio) |
| currentAndFutureBenefits | Current and future benefits (provider: intrinio) |
| propertyAndLiabilityInsuranceClaims | Property and liability insurance claims (provider: intrinio) |
| totalNonInterestExpense | Total non-interest expense (provider: intrinio) |
| netRealizedAndUnrealizedCapitalGainsOnInvestments | Net realized and unrealized capital gains on investments (provider: intrinio) |
| otherGains | Other gains (provider: intrinio) |
| non_operating_income | Non-operating income (provider: intrinio);     Non Operating Income/Loss (provider: polygon) |
| otherIncome | Other income (provider: intrinio) |
| otherRevenue | Other revenue (provider: intrinio) |
| extraordinaryIncome | Extraordinary income (provider: intrinio) |
| totalOtherIncome | Total other income (provider: intrinio) |
| ebit | Earnings Before Interest and Taxes. (provider: intrinio) |
| impairmentCharge | Impairment charge (provider: intrinio) |
| restructuringCharge | Restructuring charge (provider: intrinio) |
| serviceChargesOnDepositAccounts | Service charges on deposit accounts (provider: intrinio) |
| otherServiceCharges | Other service charges (provider: intrinio) |
| otherSpecialCharges | Other special charges (provider: intrinio) |
| otherCostOfRevenue | Other cost of revenue (provider: intrinio) |
| netIncomeContinuingOperations | Net income (continuing operations) (provider: intrinio) |
| netIncomeDiscontinuedOperations | Net income (discontinued operations) (provider: intrinio) |
| otherAdjustmentsToConsolidatedNetIncome | Other adjustments to consolidated net income (provider: intrinio) |
| otherAdjustmentToNetIncomeAttributableToCommonShareholders | Other adjustment to net income attributable to common shareholders (provider: intrinio) |
| netIncomeAttributableToNoncontrollingInterest | Net income attributable to noncontrolling interest (provider: intrinio) |
| net_income_attributable_to_common_shareholders | Net income attributable to common shareholders (provider: intrinio);     Net Income/Loss Available To Common Stockholders Basic (provider: polygon) |
| basicAndDilutedEarningsPerShare | Basic and diluted earnings per share (provider: intrinio) |
| cashDividendsToCommonPerShare | Cash dividends to common per share (provider: intrinio) |
| preferredStockDividendsDeclared | Preferred stock dividends declared (provider: intrinio) |
| weightedAverageBasicAndDilutedSharesOutstanding | Weighted average basic and diluted shares outstanding (provider: intrinio) |
| cost_of_revenue_goods | Cost of Revenue - Goods (provider: polygon) |
| cost_of_revenue_services | Cost of Revenue - Services (provider: polygon) |
| provisionsForLoanLeaseAndOtherLosses | Provisions for loan lease and other losses (provider: polygon) |
| incomeTaxExpenseBenefitCurrent | Income tax expense benefit current (provider: polygon) |
| deferredTaxBenefit | Deferred tax benefit (provider: polygon) |
| benefits_costs_expenses | Benefits, costs and expenses (provider: polygon) |
| selling_general_and_administrative_expense | Selling, general and administrative expense (provider: polygon) |
| research_and_development | Research and development (provider: polygon) |
| costs_and_expenses | Costs and expenses (provider: polygon) |
| operating_expenses | Operating expenses (provider: polygon) |
| operatingIncome | Operating Income/Loss (provider: polygon) |
| interestAndDividendIncome | Interest and Dividend Income (provider: polygon) |
| interestAndDebtExpense | Interest and Debt Expense (provider: polygon) |
| interestIncomeAfterProvisionForLosses | Interest Income After Provision for Losses (provider: polygon) |
| nonInterestExpense | Non-Interest Expense (provider: polygon) |
| nonInterestIncome | Non-Interest Income (provider: polygon) |
| incomeFromDiscontinuedOperationsNetOfTaxOnDisposal | Income From Discontinued Operations Net of Tax on Disposal (provider: polygon) |
| incomeFromDiscontinuedOperationsNetOfTax | Income From Discontinued Operations Net of Tax (provider: polygon) |
| incomeBeforeEquityMethodInvestments | Income Before Equity Method Investments (provider: polygon) |
| incomeFromEquityMethodInvestments | Income From Equity Method Investments (provider: polygon) |
| incomeAfterTax | Income After Tax (provider: polygon) |
| net_income_attributable_noncontrolling_interest | Net income (loss) attributable to noncontrolling interest (provider: polygon) |
| netIncomeAttributableToParent | Net income (loss) attributable to parent (provider: polygon) |
| participatingSecuritiesEarnings | Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon) |
| undistributedEarningsAllocatedToParticipatingSecurities | Undistributed Earnings Allocated To Participating Securities (provider: polygon) |
| common_stock_dividends | Common Stock Dividends (provider: polygon) |
| preferred_stock_dividends_and_other_adjustments | Preferred stock dividends and other adjustments (provider: polygon) |
---

## Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME( "AAPL" )
```

