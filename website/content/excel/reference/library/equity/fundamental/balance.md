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

<!-- markdownlint-disable MD041 -->

Balance Sheet. Balance sheet statement.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE( symbol; [provider]; [period]; [limit]; [fiscal_year]; [filing_date]; [filing_date_lt]; [filing_date_lte]; [filing_date_gt]; [filing_date_gte]; [period_of_report_date]; [period_of_report_date_lt]; [period_of_report_date_lte]; [period_of_report_date_gt]; [period_of_report_date_gte]; [include_sources]; [order]; [sort] )
```

---

## Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE("AAPL")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| provider | Text | Options: fmp, intrinio, polygon, defaults to fmp. | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| fiscal_year | Number | The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio) | True |
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
| cash_and_cash_equivalents | Cash and cash equivalents. (provider: fmp, intrinio) |
| short_term_investments | Short term investments. (provider: fmp, intrinio) |
| cashAndShortTermInvestments | Cash and short term investments. (provider: fmp) |
| netReceivables | Net receivables. (provider: fmp) |
| inventory | Inventory. (provider: fmp, polygon) |
| other_current_assets | Other current assets. (provider: fmp, intrinio, polygon) |
| total_current_assets | Total current assets. (provider: fmp, intrinio, polygon) |
| plant_property_equipment_net | Plant property equipment net. (provider: fmp, intrinio) |
| goodwill | Goodwill. (provider: fmp, intrinio) |
| intangible_assets | Intangible assets. (provider: fmp, intrinio, polygon) |
| goodwillAndIntangibleAssets | Goodwill and intangible assets. (provider: fmp) |
| long_term_investments | Long term investments. (provider: fmp, intrinio) |
| taxAssets | Tax assets. (provider: fmp) |
| other_non_current_assets | Other non current assets. (provider: fmp, polygon) |
| nonCurrentAssets | Total non current assets. (provider: fmp) |
| other_assets | Other assets. (provider: fmp, intrinio) |
| total_assets | Total assets. (provider: fmp, intrinio, polygon) |
| accounts_payable | Accounts payable. (provider: fmp, intrinio, polygon) |
| short_term_debt | Short term debt. (provider: fmp, intrinio) |
| taxPayables | Tax payables. (provider: fmp) |
| current_deferred_revenue | Current deferred revenue. (provider: fmp, intrinio) |
| other_current_liabilities | Other current liabilities. (provider: fmp, intrinio, polygon) |
| total_current_liabilities | Total current liabilities. (provider: fmp, intrinio, polygon) |
| long_term_debt | Long term debt. (provider: fmp, intrinio, polygon) |
| deferredRevenueNonCurrent | Non current deferred revenue. (provider: fmp) |
| deferredTaxLiabilitiesNonCurrent | Deferred tax liabilities non current. (provider: fmp) |
| other_non_current_liabilities | Other non current liabilities. (provider: fmp, polygon) |
| total_non_current_liabilities | Total non current liabilities. (provider: fmp, intrinio, polygon) |
| otherLiabilities | Other liabilities. (provider: fmp) |
| capital_lease_obligations | Capital lease obligations. (provider: fmp, intrinio) |
| total_liabilities | Total liabilities. (provider: fmp, intrinio, polygon) |
| preferred_stock | Preferred stock. (provider: fmp, intrinio, polygon) |
| common_stock | Common stock. (provider: fmp, intrinio) |
| retained_earnings | Retained earnings. (provider: fmp, intrinio) |
| accumulated_other_comprehensive_income | Accumulated other comprehensive income (loss). (provider: fmp, intrinio) |
| otherShareholdersEquity | Other shareholders equity. (provider: fmp) |
| otherTotalShareholdersEquity | Other total shareholders equity. (provider: fmp) |
| total_common_equity | Total common equity. (provider: fmp, intrinio) |
| total_equity_non_controlling_interests | Total equity non controlling interests. (provider: fmp, intrinio) |
| totalLiabilitiesAndShareholdersEquity | Total liabilities and shareholders equity. (provider: fmp) |
| minority_interest | Minority interest. (provider: fmp, polygon) |
| totalLiabilitiesAndTotalEquity | Total liabilities and total equity. (provider: fmp) |
| totalInvestments | Total investments. (provider: fmp) |
| totalDebt | Total debt. (provider: fmp) |
| netDebt | Net debt. (provider: fmp) |
| link | Link to the filing. (provider: fmp) |
| finalLink | Link to the filing document. (provider: fmp) |
| cash_and_due_from_banks | Cash and due from banks. (provider: intrinio) |
| restrictedCash | Restricted cash. (provider: intrinio) |
| federalFundsSold | Federal funds sold. (provider: intrinio) |
| accounts_receivable | Accounts receivable. (provider: intrinio, polygon) |
| noteAndLeaseReceivable | Note and lease receivable. (Vendor non-trade receivables) (provider: intrinio) |
| inventories | Net Inventories. (provider: intrinio) |
| customerAndOtherReceivables | Customer and other receivables. (provider: intrinio) |
| interestBearingDepositsAtOtherBanks | Interest bearing deposits at other banks. (provider: intrinio) |
| timeDepositsPlacedAndOtherShortTermInvestments | Time deposits placed and other short term investments. (provider: intrinio) |
| tradingAccountSecurities | Trading account securities. (provider: intrinio) |
| loansAndLeases | Loans and leases. (provider: intrinio) |
| allowanceForLoanAndLeaseLosses | Allowance for loan and lease losses. (provider: intrinio) |
| currentDeferredRefundableIncomeTaxes | Current deferred refundable income taxes. (provider: intrinio) |
| loansAndLeasesNetOfAllowance | Loans and leases net of allowance. (provider: intrinio) |
| accruedInvestmentIncome | Accrued investment income. (provider: intrinio) |
| otherCurrentNonOperatingAssets | Other current non-operating assets. (provider: intrinio) |
| loansHeldForSale | Loans held for sale. (provider: intrinio) |
| prepaid_expenses | Prepaid expenses. (provider: intrinio, polygon) |
| plantPropertyEquipmentGross | Plant property equipment gross. (provider: intrinio) |
| accumulatedDepreciation | Accumulated depreciation. (provider: intrinio) |
| premisesAndEquipmentNet | Net premises and equipment. (provider: intrinio) |
| mortgageServicingRights | Mortgage servicing rights. (provider: intrinio) |
| unearnedPremiumsAsset | Unearned premiums asset. (provider: intrinio) |
| nonCurrentNoteLeaseReceivables | Non-current note lease receivables. (provider: intrinio) |
| deferredAcquisitionCost | Deferred acquisition cost. (provider: intrinio) |
| separateAccountBusinessAssets | Separate account business assets. (provider: intrinio) |
| nonCurrentDeferredRefundableIncomeTaxes | Noncurrent deferred refundable income taxes. (provider: intrinio) |
| employeeBenefitAssets | Employee benefit assets. (provider: intrinio) |
| otherNonCurrentOperatingAssets | Other noncurrent operating assets. (provider: intrinio) |
| otherNonCurrentNonOperatingAssets | Other noncurrent non-operating assets. (provider: intrinio) |
| interestBearingDeposits | Interest bearing deposits. (provider: intrinio) |
| total_non_current_assets | Total noncurrent assets. (provider: intrinio, polygon) |
| nonInterestBearingDeposits | Non interest bearing deposits. (provider: intrinio) |
| federalFundsPurchasedAndSecuritiesSold | Federal funds purchased and securities sold. (provider: intrinio) |
| bankers_acceptance_outstanding | Bankers acceptance outstanding. (provider: intrinio) |
| currentDeferredPayableIncomeTaxLiabilities | Current deferred payable income tax liabilities. (provider: intrinio) |
| accruedInterestPayable | Accrued interest payable. (provider: intrinio) |
| accruedExpenses | Accrued expenses. (provider: intrinio) |
| otherShortTermPayables | Other short term payables. (provider: intrinio) |
| customerDeposits | Customer deposits. (provider: intrinio) |
| dividendsPayable | Dividends payable. (provider: intrinio) |
| claimsAndClaimExpense | Claims and claim expense. (provider: intrinio) |
| futurePolicyBenefits | Future policy benefits. (provider: intrinio) |
| currentEmployeeBenefitLiabilities | Current employee benefit liabilities. (provider: intrinio) |
| unearnedPremiumsLiability | Unearned premiums liability. (provider: intrinio) |
| otherTaxesPayable | Other taxes payable. (provider: intrinio) |
| policyHolderFunds | Policy holder funds. (provider: intrinio) |
| otherCurrentNonOperatingLiabilities | Other current non-operating liabilities. (provider: intrinio) |
| separateAccountBusinessLiabilities | Separate account business liabilities. (provider: intrinio) |
| otherLongTermLiabilities | Other long term liabilities. (provider: intrinio) |
| nonCurrentDeferredRevenue | Non-current deferred revenue. (provider: intrinio) |
| nonCurrentDeferredPayableIncomeTaxLiabilities | Non-current deferred payable income tax liabilities. (provider: intrinio) |
| nonCurrentEmployeeBenefitLiabilities | Non-current employee benefit liabilities. (provider: intrinio) |
| otherNonCurrentOperatingLiabilities | Other non-current operating liabilities. (provider: intrinio) |
| otherNonCurrentNonOperatingLiabilities | Other non-current, non-operating liabilities. (provider: intrinio) |
| assetRetirementReserveLitigationObligation | Asset retirement reserve litigation obligation. (provider: intrinio) |
| commitmentsContingencies | Commitments contingencies. (provider: intrinio) |
| redeemable_non_controlling_interest | Redeemable non-controlling interest. (provider: intrinio, polygon) |
| treasuryStock | Treasury stock. (provider: intrinio) |
| participatingPolicyHolderEquity | Participating policy holder equity. (provider: intrinio) |
| otherEquityAdjustments | Other equity adjustments. (provider: intrinio) |
| totalPreferredCommonEquity | Total preferred common equity. (provider: intrinio) |
| nonControllingInterest | Non-controlling interest. (provider: intrinio) |
| totalLiabilitiesShareholdersEquity | Total liabilities and shareholders equity. (provider: intrinio) |
| marketableSecurities | Marketable securities (provider: polygon) |
| propertyPlantEquipmentNet | Property plant and equipment net (provider: polygon) |
| employeeWages | Employee wages (provider: polygon) |
| temporary_equity_attributable_to_parent | Temporary equity attributable to parent (provider: polygon) |
| equity_attributable_to_parent | Equity attributable to parent (provider: polygon) |
| temporary_equity | Temporary equity (provider: polygon) |
| redeemableNonControllingInterestOther | Redeemable non-controlling interest other (provider: polygon) |
| totalStockHoldersEquity | Total stock holders equity (provider: polygon) |
| totalLiabilitiesAndStockHoldersEquity | Total liabilities and stockholders equity (provider: polygon) |
| totalEquity | Total equity (provider: polygon) |
