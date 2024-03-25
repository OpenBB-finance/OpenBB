---
title: "balance_of_payments"
description: "Balance of Payments Reports"
keywords:
- economy
- balance_of_payments
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/balance_of_payments - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Balance of Payments Reports.


Examples
--------

```python
from openbb import obb
obb.economy.balance_of_payments(provider='ecb')
obb.economy.balance_of_payments(report_type=summary, provider='ecb')
# The `country` parameter will override the `report_type`.
obb.economy.balance_of_payments(country=united_states, provider='ecb')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['ecb'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'ecb' if there is no default. | ecb | True |
| report_type | Literal['main', 'summary', 'services', 'investment_income', 'direct_investment', 'portfolio_investment', 'other_investment'] | The report type, the level of detail in the data. | main | True |
| frequency | Literal['monthly', 'quarterly'] | The frequency of the data. Monthly is valid only for ['main', 'summary']. | monthly | True |
| country | Literal['brazil', 'canada', 'china', 'eu_ex_euro_area', 'eu_institutions', 'india', 'japan', 'russia', 'switzerland', 'united_kingdom', 'united_states', 'total'] | The country/region of the data. This parameter will override the 'report_type' parameter. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : BalanceOfPayments
        Serializable results.
    provider : Literal['ecb']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period | date | The date representing the beginning of the reporting period. |
| current_account | float | Current Account Balance (Billions of EUR) |
| goods | float | Goods Balance (Billions of EUR) |
| services | float | Services Balance (Billions of EUR) |
| primary_income | float | Primary Income Balance (Billions of EUR) |
| secondary_income | float | Secondary Income Balance (Billions of EUR) |
| capital_account | float | Capital Account Balance (Billions of EUR) |
| net_lending_to_rest_of_world | float | Balance of net lending to the rest of the world (Billions of EUR) |
| financial_account | float | Financial Account Balance (Billions of EUR) |
| direct_investment | float | Direct Investment Balance (Billions of EUR) |
| portfolio_investment | float | Portfolio Investment Balance (Billions of EUR) |
| financial_derivatives | float | Financial Derivatives Balance (Billions of EUR) |
| other_investment | float | Other Investment Balance (Billions of EUR) |
| reserve_assets | float | Reserve Assets Balance (Billions of EUR) |
| errors_and_ommissions | float | Errors and Omissions (Billions of EUR) |
| current_account_credit | float | Current Account Credits (Billions of EUR) |
| current_account_debit | float | Current Account Debits (Billions of EUR) |
| current_account_balance | float | Current Account Balance (Billions of EUR) |
| goods_credit | float | Goods Credits (Billions of EUR) |
| goods_debit | float | Goods Debits (Billions of EUR) |
| services_credit | float | Services Credits (Billions of EUR) |
| services_debit | float | Services Debits (Billions of EUR) |
| primary_income_credit | float | Primary Income Credits (Billions of EUR) |
| primary_income_employee_compensation_credit | float | Primary Income Employee Compensation Credit (Billions of EUR) |
| primary_income_debit | float | Primary Income Debits (Billions of EUR) |
| primary_income_employee_compensation_debit | float | Primary Income Employee Compensation Debit (Billions of EUR) |
| secondary_income_credit | float | Secondary Income Credits (Billions of EUR) |
| secondary_income_debit | float | Secondary Income Debits (Billions of EUR) |
| capital_account_credit | float | Capital Account Credits (Billions of EUR) |
| capital_account_debit | float | Capital Account Debits (Billions of EUR) |
| services_total_credit | float | Services Total Credit (Billions of EUR) |
| services_total_debit | float | Services Total Debit (Billions of EUR) |
| transport_credit | float | Transport Credit (Billions of EUR) |
| transport_debit | float | Transport Debit (Billions of EUR) |
| travel_credit | float | Travel Credit (Billions of EUR) |
| travel_debit | float | Travel Debit (Billions of EUR) |
| financial_services_credit | float | Financial Services Credit (Billions of EUR) |
| financial_services_debit | float | Financial Services Debit (Billions of EUR) |
| communications_credit | float | Communications Credit (Billions of EUR) |
| communications_debit | float | Communications Debit (Billions of EUR) |
| other_business_services_credit | float | Other Business Services Credit (Billions of EUR) |
| other_business_services_debit | float | Other Business Services Debit (Billions of EUR) |
| other_services_credit | float | Other Services Credit (Billions of EUR) |
| other_services_debit | float | Other Services Debit (Billions of EUR) |
| investment_total_credit | float | Investment Total Credit (Billions of EUR) |
| investment_total_debit | float | Investment Total Debit (Billions of EUR) |
| equity_credit | float | Equity Credit (Billions of EUR) |
| equity_reinvested_earnings_credit | float | Equity Reinvested Earnings Credit (Billions of EUR) |
| equity_debit | float | Equity Debit (Billions of EUR) |
| equity_reinvested_earnings_debit | float | Equity Reinvested Earnings Debit (Billions of EUR) |
| debt_instruments_credit | float | Debt Instruments Credit (Billions of EUR) |
| debt_instruments_debit | float | Debt Instruments Debit (Billions of EUR) |
| portfolio_investment_equity_credit | float | Portfolio Investment Equity Credit (Billions of EUR) |
| portfolio_investment_equity_debit | float | Portfolio Investment Equity Debit (Billions of EUR) |
| portfolio_investment_debt_instruments_credit | float | Portfolio Investment Debt Instruments Credit (Billions of EUR) |
| portofolio_investment_debt_instruments_debit | float | Portfolio Investment Debt Instruments Debit (Billions of EUR) |
| other_investment_credit | float | Other Investment Credit (Billions of EUR) |
| other_investment_debit | float | Other Investment Debit (Billions of EUR) |
| reserve_assets_credit | float | Reserve Assets Credit (Billions of EUR) |
| assets_total | float | Assets Total (Billions of EUR) |
| assets_equity | float | Assets Equity (Billions of EUR) |
| assets_debt_instruments | float | Assets Debt Instruments (Billions of EUR) |
| assets_mfi | float | Assets MFIs (Billions of EUR) |
| assets_non_mfi | float | Assets Non MFIs (Billions of EUR) |
| assets_direct_investment_abroad | float | Assets Direct Investment Abroad (Billions of EUR) |
| liabilities_total | float | Liabilities Total (Billions of EUR) |
| liabilities_equity | float | Liabilities Equity (Billions of EUR) |
| liabilities_debt_instruments | float | Liabilities Debt Instruments (Billions of EUR) |
| liabilities_mfi | float | Liabilities MFIs (Billions of EUR) |
| liabilities_non_mfi | float | Liabilities Non MFIs (Billions of EUR) |
| liabilities_direct_investment_euro_area | float | Liabilities Direct Investment in Euro Area (Billions of EUR) |
| assets_equity_and_fund_shares | float | Assets Equity and Investment Fund Shares (Billions of EUR) |
| assets_equity_shares | float | Assets Equity Shares (Billions of EUR) |
| assets_investment_fund_shares | float | Assets Investment Fund Shares (Billions of EUR) |
| assets_debt_short_term | float | Assets Debt Short Term (Billions of EUR) |
| assets_debt_long_term | float | Assets Debt Long Term (Billions of EUR) |
| assets_resident_sector_eurosystem | float | Assets Resident Sector Eurosystem (Billions of EUR) |
| assets_resident_sector_mfi_ex_eurosystem | float | Assets Resident Sector MFIs outside Eurosystem (Billions of EUR) |
| assets_resident_sector_government | float | Assets Resident Sector Government (Billions of EUR) |
| assets_resident_sector_other | float | Assets Resident Sector Other (Billions of EUR) |
| liabilities_equity_and_fund_shares | float | Liabilities Equity and Investment Fund Shares (Billions of EUR) |
| liabilities_investment_fund_shares | float | Liabilities Investment Fund Shares (Billions of EUR) |
| liabilities_debt_short_term | float | Liabilities Debt Short Term (Billions of EUR) |
| liabilities_debt_long_term | float | Liabilities Debt Long Term (Billions of EUR) |
| liabilities_resident_sector_government | float | Liabilities Resident Sector Government (Billions of EUR) |
| liabilities_resident_sector_other | float | Liabilities Resident Sector Other (Billions of EUR) |
| assets_currency_and_deposits | float | Assets Currency and Deposits (Billions of EUR) |
| assets_loans | float | Assets Loans (Billions of EUR) |
| assets_trade_credit_and_advances | float | Assets Trade Credits and Advances (Billions of EUR) |
| assets_eurosystem | float | Assets Eurosystem (Billions of EUR) |
| assets_other_mfi_ex_eurosystem | float | Assets Other MFIs outside Eurosystem (Billions of EUR) |
| assets_government | float | Assets Government (Billions of EUR) |
| assets_other_sectors | float | Assets Other Sectors (Billions of EUR) |
| liabilities_currency_and_deposits | float | Liabilities Currency and Deposits (Billions of EUR) |
| liabilities_loans | float | Liabilities Loans (Billions of EUR) |
| liabilities_trade_credit_and_advances | float | Liabilities Trade Credits and Advances (Billions of EUR) |
| liabilities_eurosystem | float | Liabilities Eurosystem (Billions of EUR) |
| liabilities_other_mfi_ex_eurosystem | float | Liabilities Other MFIs outside Eurosystem (Billions of EUR) |
| liabilities_government | float | Liabilities Government (Billions of EUR) |
| liabilities_other_sectors | float | Liabilities Other Sectors (Billions of EUR) |
| goods_balance | float | Goods Balance (Billions of EUR) |
| services_balance | float | Services Balance (Billions of EUR) |
| primary_income_balance | float | Primary Income Balance (Billions of EUR) |
| investment_income_balance | float | Investment Income Balance (Billions of EUR) |
| investment_income_credit | float | Investment Income Credits (Billions of EUR) |
| investment_income_debit | float | Investment Income Debits (Billions of EUR) |
| secondary_income_balance | float | Secondary Income Balance (Billions of EUR) |
| capital_account_balance | float | Capital Account Balance (Billions of EUR) |
</TabItem>

<TabItem value='ecb' label='ecb'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period | date | The date representing the beginning of the reporting period. |
| current_account | float | Current Account Balance (Billions of EUR) |
| goods | float | Goods Balance (Billions of EUR) |
| services | float | Services Balance (Billions of EUR) |
| primary_income | float | Primary Income Balance (Billions of EUR) |
| secondary_income | float | Secondary Income Balance (Billions of EUR) |
| capital_account | float | Capital Account Balance (Billions of EUR) |
| net_lending_to_rest_of_world | float | Balance of net lending to the rest of the world (Billions of EUR) |
| financial_account | float | Financial Account Balance (Billions of EUR) |
| direct_investment | float | Direct Investment Balance (Billions of EUR) |
| portfolio_investment | float | Portfolio Investment Balance (Billions of EUR) |
| financial_derivatives | float | Financial Derivatives Balance (Billions of EUR) |
| other_investment | float | Other Investment Balance (Billions of EUR) |
| reserve_assets | float | Reserve Assets Balance (Billions of EUR) |
| errors_and_ommissions | float | Errors and Omissions (Billions of EUR) |
| current_account_credit | float | Current Account Credits (Billions of EUR) |
| current_account_debit | float | Current Account Debits (Billions of EUR) |
| current_account_balance | float | Current Account Balance (Billions of EUR) |
| goods_credit | float | Goods Credits (Billions of EUR) |
| goods_debit | float | Goods Debits (Billions of EUR) |
| services_credit | float | Services Credits (Billions of EUR) |
| services_debit | float | Services Debits (Billions of EUR) |
| primary_income_credit | float | Primary Income Credits (Billions of EUR) |
| primary_income_employee_compensation_credit | float | Primary Income Employee Compensation Credit (Billions of EUR) |
| primary_income_debit | float | Primary Income Debits (Billions of EUR) |
| primary_income_employee_compensation_debit | float | Primary Income Employee Compensation Debit (Billions of EUR) |
| secondary_income_credit | float | Secondary Income Credits (Billions of EUR) |
| secondary_income_debit | float | Secondary Income Debits (Billions of EUR) |
| capital_account_credit | float | Capital Account Credits (Billions of EUR) |
| capital_account_debit | float | Capital Account Debits (Billions of EUR) |
| services_total_credit | float | Services Total Credit (Billions of EUR) |
| services_total_debit | float | Services Total Debit (Billions of EUR) |
| transport_credit | float | Transport Credit (Billions of EUR) |
| transport_debit | float | Transport Debit (Billions of EUR) |
| travel_credit | float | Travel Credit (Billions of EUR) |
| travel_debit | float | Travel Debit (Billions of EUR) |
| financial_services_credit | float | Financial Services Credit (Billions of EUR) |
| financial_services_debit | float | Financial Services Debit (Billions of EUR) |
| communications_credit | float | Communications Credit (Billions of EUR) |
| communications_debit | float | Communications Debit (Billions of EUR) |
| other_business_services_credit | float | Other Business Services Credit (Billions of EUR) |
| other_business_services_debit | float | Other Business Services Debit (Billions of EUR) |
| other_services_credit | float | Other Services Credit (Billions of EUR) |
| other_services_debit | float | Other Services Debit (Billions of EUR) |
| investment_total_credit | float | Investment Total Credit (Billions of EUR) |
| investment_total_debit | float | Investment Total Debit (Billions of EUR) |
| equity_credit | float | Equity Credit (Billions of EUR) |
| equity_reinvested_earnings_credit | float | Equity Reinvested Earnings Credit (Billions of EUR) |
| equity_debit | float | Equity Debit (Billions of EUR) |
| equity_reinvested_earnings_debit | float | Equity Reinvested Earnings Debit (Billions of EUR) |
| debt_instruments_credit | float | Debt Instruments Credit (Billions of EUR) |
| debt_instruments_debit | float | Debt Instruments Debit (Billions of EUR) |
| portfolio_investment_equity_credit | float | Portfolio Investment Equity Credit (Billions of EUR) |
| portfolio_investment_equity_debit | float | Portfolio Investment Equity Debit (Billions of EUR) |
| portfolio_investment_debt_instruments_credit | float | Portfolio Investment Debt Instruments Credit (Billions of EUR) |
| portofolio_investment_debt_instruments_debit | float | Portfolio Investment Debt Instruments Debit (Billions of EUR) |
| other_investment_credit | float | Other Investment Credit (Billions of EUR) |
| other_investment_debit | float | Other Investment Debit (Billions of EUR) |
| reserve_assets_credit | float | Reserve Assets Credit (Billions of EUR) |
| assets_total | float | Assets Total (Billions of EUR) |
| assets_equity | float | Assets Equity (Billions of EUR) |
| assets_debt_instruments | float | Assets Debt Instruments (Billions of EUR) |
| assets_mfi | float | Assets MFIs (Billions of EUR) |
| assets_non_mfi | float | Assets Non MFIs (Billions of EUR) |
| assets_direct_investment_abroad | float | Assets Direct Investment Abroad (Billions of EUR) |
| liabilities_total | float | Liabilities Total (Billions of EUR) |
| liabilities_equity | float | Liabilities Equity (Billions of EUR) |
| liabilities_debt_instruments | float | Liabilities Debt Instruments (Billions of EUR) |
| liabilities_mfi | float | Liabilities MFIs (Billions of EUR) |
| liabilities_non_mfi | float | Liabilities Non MFIs (Billions of EUR) |
| liabilities_direct_investment_euro_area | float | Liabilities Direct Investment in Euro Area (Billions of EUR) |
| assets_equity_and_fund_shares | float | Assets Equity and Investment Fund Shares (Billions of EUR) |
| assets_equity_shares | float | Assets Equity Shares (Billions of EUR) |
| assets_investment_fund_shares | float | Assets Investment Fund Shares (Billions of EUR) |
| assets_debt_short_term | float | Assets Debt Short Term (Billions of EUR) |
| assets_debt_long_term | float | Assets Debt Long Term (Billions of EUR) |
| assets_resident_sector_eurosystem | float | Assets Resident Sector Eurosystem (Billions of EUR) |
| assets_resident_sector_mfi_ex_eurosystem | float | Assets Resident Sector MFIs outside Eurosystem (Billions of EUR) |
| assets_resident_sector_government | float | Assets Resident Sector Government (Billions of EUR) |
| assets_resident_sector_other | float | Assets Resident Sector Other (Billions of EUR) |
| liabilities_equity_and_fund_shares | float | Liabilities Equity and Investment Fund Shares (Billions of EUR) |
| liabilities_investment_fund_shares | float | Liabilities Investment Fund Shares (Billions of EUR) |
| liabilities_debt_short_term | float | Liabilities Debt Short Term (Billions of EUR) |
| liabilities_debt_long_term | float | Liabilities Debt Long Term (Billions of EUR) |
| liabilities_resident_sector_government | float | Liabilities Resident Sector Government (Billions of EUR) |
| liabilities_resident_sector_other | float | Liabilities Resident Sector Other (Billions of EUR) |
| assets_currency_and_deposits | float | Assets Currency and Deposits (Billions of EUR) |
| assets_loans | float | Assets Loans (Billions of EUR) |
| assets_trade_credit_and_advances | float | Assets Trade Credits and Advances (Billions of EUR) |
| assets_eurosystem | float | Assets Eurosystem (Billions of EUR) |
| assets_other_mfi_ex_eurosystem | float | Assets Other MFIs outside Eurosystem (Billions of EUR) |
| assets_government | float | Assets Government (Billions of EUR) |
| assets_other_sectors | float | Assets Other Sectors (Billions of EUR) |
| liabilities_currency_and_deposits | float | Liabilities Currency and Deposits (Billions of EUR) |
| liabilities_loans | float | Liabilities Loans (Billions of EUR) |
| liabilities_trade_credit_and_advances | float | Liabilities Trade Credits and Advances (Billions of EUR) |
| liabilities_eurosystem | float | Liabilities Eurosystem (Billions of EUR) |
| liabilities_other_mfi_ex_eurosystem | float | Liabilities Other MFIs outside Eurosystem (Billions of EUR) |
| liabilities_government | float | Liabilities Government (Billions of EUR) |
| liabilities_other_sectors | float | Liabilities Other Sectors (Billions of EUR) |
| goods_balance | float | Goods Balance (Billions of EUR) |
| services_balance | float | Services Balance (Billions of EUR) |
| primary_income_balance | float | Primary Income Balance (Billions of EUR) |
| investment_income_balance | float | Investment Income Balance (Billions of EUR) |
| investment_income_credit | float | Investment Income Credits (Billions of EUR) |
| investment_income_debit | float | Investment Income Debits (Billions of EUR) |
| secondary_income_balance | float | Secondary Income Balance (Billions of EUR) |
| capital_account_balance | float | Capital Account Balance (Billions of EUR) |
</TabItem>

</Tabs>

