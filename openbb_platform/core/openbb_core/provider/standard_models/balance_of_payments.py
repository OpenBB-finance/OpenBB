"""Balance of Payments Model."""

from datetime import (
    date as dateType,
)
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class BalanceOfPaymentsQueryParams(QueryParams):
    """Balance Of Payments Query."""


class BP6BopUsdData(Data):
    """OECD BP6 Balance of Payments Items, in USD."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    balance_percent_of_gdp: Optional[float] = Field(
        default=None,
        description="Current Account Balance as Percent of GDP",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    balance_total: Optional[float] = Field(
        default=None, description="Current Account Total Balance (USD)"
    )
    balance_total_services: Optional[float] = Field(
        default=None, description="Current Account Total Services Balance (USD)"
    )
    balance_total_secondary_income: Optional[float] = Field(
        default=None, description="Current Account Total Secondary Income Balance (USD)"
    )
    balance_total_goods: Optional[float] = Field(
        default=None, description="Current Account Total Goods Balance (USD)"
    )
    balance_total_primary_income: Optional[float] = Field(
        default=None, description="Current Account Total Primary Income Balance (USD)"
    )
    credits_services_percent_of_goods_and_services: Optional[float] = Field(
        default=None,
        description="Current Account Credits Services as Percent of Goods and Services",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    credits_services_percent_of_current_account: Optional[float] = Field(
        default=None,
        description="Current Account Credits Services as Percent of Current Account",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    credits_total_services: Optional[float] = Field(
        default=None, description="Current Account Credits Total Services (USD)"
    )
    credits_total_goods: Optional[float] = Field(
        default=None, description="Current Account Credits Total Goods (USD)"
    )
    credits_total_primary_income: Optional[float] = Field(
        default=None, description="Current Account Credits Total Primary Income (USD)"
    )
    credits_total_secondary_income: Optional[float] = Field(
        default=None, description="Current Account Credits Total Secondary Income (USD)"
    )
    credits_total: Optional[float] = Field(
        default=None, description="Current Account Credits Total (USD)"
    )
    debits_services_percent_of_goods_and_services: Optional[float] = Field(
        default=None,
        description="Current Account Debits Services as Percent of Goods and Services",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    debits_services_percent_of_current_account: Optional[float] = Field(
        default=None,
        description="Current Account Debits Services as Percent of Current Account",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    debits_total_services: Optional[float] = Field(
        default=None, description="Current Account Debits Total Services (USD)"
    )
    debits_total_goods: Optional[float] = Field(
        default=None, description="Current Account Debits Total Goods (USD)"
    )
    debits_total_primary_income: Optional[float] = Field(
        default=None, description="Current Account Debits Total Primary Income (USD)"
    )
    debits_total: Optional[float] = Field(
        default=None, description="Current Account Debits Total (USD)"
    )
    debits_total_secondary_income: Optional[float] = Field(
        default=None, description="Current Account Debits Total Secondary Income (USD)"
    )


class ECBMain(Data):
    """ECB Main Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    current_account: Optional[float] = Field(
        default=None, description="Current Account Balance (Billions of EUR)"
    )
    goods: Optional[float] = Field(
        default=None, description="Goods Balance (Billions of EUR)"
    )
    services: Optional[float] = Field(
        default=None, description="Services Balance (Billions of EUR)"
    )
    primary_income: Optional[float] = Field(
        default=None, description="Primary Income Balance (Billions of EUR)"
    )
    secondary_income: Optional[float] = Field(
        default=None, description="Secondary Income Balance (Billions of EUR)"
    )
    capital_account: Optional[float] = Field(
        default=None, description="Capital Account Balance (Billions of EUR)"
    )
    net_lending_to_rest_of_world: Optional[float] = Field(
        default=None,
        description="Balance of net lending to the rest of the world (Billions of EUR)",
    )
    financial_account: Optional[float] = Field(
        default=None, description="Financial Account Balance (Billions of EUR)"
    )
    direct_investment: Optional[float] = Field(
        default=None, description="Direct Investment Balance (Billions of EUR)"
    )
    portfolio_investment: Optional[float] = Field(
        default=None, description="Portfolio Investment Balance (Billions of EUR)"
    )
    financial_derivatives: Optional[float] = Field(
        default=None, description="Financial Derivatives Balance (Billions of EUR)"
    )
    other_investment: Optional[float] = Field(
        default=None, description="Other Investment Balance (Billions of EUR)"
    )
    reserve_assets: Optional[float] = Field(
        default=None, description="Reserve Assets Balance (Billions of EUR)"
    )
    errors_and_ommissions: Optional[float] = Field(
        default=None, description="Errors and Omissions (Billions of EUR)"
    )


class ECBSummary(Data):
    """ECB Summary Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    current_account_credit: Optional[float] = Field(
        default=None, description="Current Account Credit (Billions of EUR)"
    )
    current_account_debit: Optional[float] = Field(
        default=None, description="Current Account Debit (Billions of EUR)"
    )
    current_account_balance: Optional[float] = Field(
        default=None, description="Current Account Balance (Billions of EUR)"
    )
    goods_credit: Optional[float] = Field(
        default=None, description="Goods Credit (Billions of EUR)"
    )
    goods_debit: Optional[float] = Field(
        default=None, description="Goods Debit (Billions of EUR)"
    )
    services_credit: Optional[float] = Field(
        default=None, description="Services Credit (Billions of EUR)"
    )
    services_debit: Optional[float] = Field(
        default=None, description="Services Debit (Billions of EUR)"
    )
    primary_income_credit: Optional[float] = Field(
        default=None, description="Primary Income Credit (Billions of EUR)"
    )
    primary_income_employee_compensation_credit: Optional[float] = Field(
        default=None,
        description="Primary Income Employee Compensation Credit (Billions of EUR)",
    )
    primary_income_debit: Optional[float] = Field(
        default=None, description="Primary Income Debit (Billions of EUR)"
    )
    primary_income_employee_compensation_debit: Optional[float] = Field(
        default=None,
        description="Primary Income Employee Compensation Debit (Billions of EUR)",
    )
    secondary_income_credit: Optional[float] = Field(
        default=None, description="Secondary Income Credit (Billions of EUR)"
    )
    secondary_income_debit: Optional[float] = Field(
        default=None, description="Secondary Income Debit (Billions of EUR)"
    )
    capital_account_credit: Optional[float] = Field(
        default=None, description="Capital Account Credit (Billions of EUR)"
    )
    capital_account_debit: Optional[float] = Field(
        default=None, description="Capital Account Debit (Billions of EUR)"
    )


class ECBServices(Data):
    """ECB Services Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    services_total_credit: Optional[float] = Field(
        default=None, description="Services Total Credit (Billions of EUR)"
    )
    services_total_debit: Optional[float] = Field(
        default=None, description="Services Total Debit (Billions of EUR)"
    )
    transport_credit: Optional[float] = Field(
        default=None, description="Transport Credit (Billions of EUR)"
    )
    transport_debit: Optional[float] = Field(
        default=None, description="Transport Debit (Billions of EUR)"
    )
    travel_credit: Optional[float] = Field(
        default=None, description="Travel Credit (Billions of EUR)"
    )
    travel_debit: Optional[float] = Field(
        default=None, description="Travel Debit (Billions of EUR)"
    )
    financial_services_credit: Optional[float] = Field(
        default=None, description="Financial Services Credit (Billions of EUR)"
    )
    financial_services_debit: Optional[float] = Field(
        default=None, description="Financial Services Debit (Billions of EUR)"
    )
    communications_credit: Optional[float] = Field(
        default=None, description="Communications Credit (Billions of EUR)"
    )
    communications_debit: Optional[float] = Field(
        default=None, description="Communications Debit (Billions of EUR)"
    )
    other_business_services_credit: Optional[float] = Field(
        default=None, description="Other Business Services Credit (Billions of EUR)"
    )
    other_business_services_debit: Optional[float] = Field(
        default=None, description="Other Business Services Debit (Billions of EUR)"
    )
    other_services_credit: Optional[float] = Field(
        default=None, description="Other Services Credit (Billions of EUR)"
    )
    other_services_debit: Optional[float] = Field(
        default=None, description="Other Services Debit (Billions of EUR)"
    )


class ECBInvestmentIncome(Data):
    """ECB Investment Income Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    investment_total_credit: Optional[float] = Field(
        default=None, description="Investment Total Credit (Billions of EUR)"
    )
    investment_total_debit: Optional[float] = Field(
        default=None, description="Investment Total Debit (Billions of EUR)"
    )
    equity_credit: Optional[float] = Field(
        default=None, description="Equity Credit (Billions of EUR)"
    )
    equity_reinvested_earnings_credit: Optional[float] = Field(
        default=None, description="Equity Reinvested Earnings Credit (Billions of EUR)"
    )
    equity_debit: Optional[float] = Field(
        default=None, description="Equity Debit (Billions of EUR)"
    )
    equity_reinvested_earnings_debit: Optional[float] = Field(
        default=None, description="Equity Reinvested Earnings Debit (Billions of EUR)"
    )
    debt_instruments_credit: Optional[float] = Field(
        default=None, description="Debt Instruments Credit (Billions of EUR)"
    )
    debt_instruments_debit: Optional[float] = Field(
        default=None, description="Debt Instruments Debit (Billions of EUR)"
    )
    portfolio_investment_equity_credit: Optional[float] = Field(
        default=None, description="Portfolio Investment Equity Credit (Billions of EUR)"
    )
    portfolio_investment_equity_debit: Optional[float] = Field(
        default=None, description="Portfolio Investment Equity Debit (Billions of EUR)"
    )
    portfolio_investment_debt_instruments_credit: Optional[float] = Field(
        default=None,
        description="Portfolio Investment Debt Instruments Credit (Billions of EUR)",
    )
    portofolio_investment_debt_instruments_debit: Optional[float] = Field(
        default=None,
        description="Portfolio Investment Debt Instruments Debit (Billions of EUR)",
    )
    other_investment_credit: Optional[float] = Field(
        default=None, description="Other Investment Credit (Billions of EUR)"
    )
    other_investment_debit: Optional[float] = Field(
        default=None, description="Other Investment Debit (Billions of EUR)"
    )
    reserve_assets_credit: Optional[float] = Field(
        default=None, description="Reserve Assets Credit (Billions of EUR)"
    )


class ECBDirectInvestment(Data):
    """ECB Direct Investment Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    assets_total: Optional[float] = Field(
        default=None, description="Assets Total (Billions of EUR)"
    )
    assets_equity: Optional[float] = Field(
        default=None, description="Assets Equity (Billions of EUR)"
    )
    assets_debt_instruments: Optional[float] = Field(
        default=None, description="Assets Debt Instruments (Billions of EUR)"
    )
    assets_mfi: Optional[float] = Field(
        default=None, description="Assets MFIs (Billions of EUR)"
    )
    assets_non_mfi: Optional[float] = Field(
        default=None, description="Assets Non MFIs (Billions of EUR)"
    )
    assets_direct_investment_abroad: Optional[float] = Field(
        default=None, description="Assets Direct Investment Abroad (Billions of EUR)"
    )
    liabilities_total: Optional[float] = Field(
        default=None, description="Liabilities Total (Billions of EUR)"
    )
    liabilities_equity: Optional[float] = Field(
        default=None, description="Liabilities Equity (Billions of EUR)"
    )
    liabilities_debt_instruments: Optional[float] = Field(
        default=None, description="Liabilities Debt Instruments (Billions of EUR)"
    )
    liabilities_mfi: Optional[float] = Field(
        default=None, description="Liabilities MFIs (Billions of EUR)"
    )
    liabilities_non_mfi: Optional[float] = Field(
        default=None, description="Liabilities Non MFIs (Billions of EUR)"
    )
    liabilities_direct_investment_euro_area: Optional[float] = Field(
        default=None,
        description="Liabilities Direct Investment in Euro Area (Billions of EUR)",
    )


class ECBPortfolioInvestment(Data):
    """ECB Portfolio Investment Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    assets_total: Optional[float] = Field(
        default=None, description="Assets Total (Billions of EUR)"
    )
    assets_equity_and_fund_shares: Optional[float] = Field(
        default=None,
        description="Assets Equity and Investment Fund Shares (Billions of EUR)",
    )
    assets_equity_shares: Optional[float] = Field(
        default=None, description="Assets Equity Shares (Billions of EUR)"
    )
    assets_investment_fund_shares: Optional[float] = Field(
        default=None, description="Assets Investment Fund Shares (Billions of EUR)"
    )
    assets_debt_short_term: Optional[float] = Field(
        default=None, description="Assets Debt Short Term (Billions of EUR)"
    )
    assets_debt_long_term: Optional[float] = Field(
        default=None, description="Assets Debt Long Term (Billions of EUR)"
    )
    assets_resident_sector_eurosystem: Optional[float] = Field(
        default=None, description="Assets Resident Sector Eurosystem (Billions of EUR)"
    )
    assets_resident_sector_mfi_ex_eurosystem: Optional[float] = Field(
        default=None,
        description="Assets Resident Sector MFIs outside Eurosystem (Billions of EUR)",
    )
    assets_resident_sector_government: Optional[float] = Field(
        default=None, description="Assets Resident Sector Government (Billions of EUR)"
    )
    assets_resident_sector_other: Optional[float] = Field(
        default=None, description="Assets Resident Sector Other (Billions of EUR)"
    )
    liabilities_total: Optional[float] = Field(
        default=None, description="Liabilities Total (Billions of EUR)"
    )
    liabilities_equity_and_fund_shares: Optional[float] = Field(
        default=None,
        description="Liabilities Equity and Investment Fund Shares (Billions of EUR)",
    )
    liabilities_equity: Optional[float] = Field(
        default=None, description="Liabilities Equity (Billions of EUR)"
    )
    liabilities_investment_fund_shares: Optional[float] = Field(
        default=None, description="Liabilities Investment Fund Shares (Billions of EUR)"
    )
    liabilities_debt_short_term: Optional[float] = Field(
        default=None, description="Liabilities Debt Short Term (Billions of EUR)"
    )
    liabilities_debt_long_term: Optional[float] = Field(
        default=None, description="Liabilities Debt Long Term (Billions of EUR)"
    )
    liabilities_resident_sector_government: Optional[float] = Field(
        default=None,
        description="Liabilities Resident Sector Government (Billions of EUR)",
    )
    liabilities_resident_sector_other: Optional[float] = Field(
        default=None, description="Liabilities Resident Sector Other (Billions of EUR)"
    )


class ECBOtherInvestment(Data):
    """ECB Other Investment Balance of Payments Items."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    assets_total: Optional[float] = Field(
        default=None, description="Assets Total (Billions of EUR)"
    )
    assets_currency_and_deposits: Optional[float] = Field(
        default=None, description="Assets Currency and Deposits (Billions of EUR)"
    )
    assets_loans: Optional[float] = Field(
        default=None, description="Assets Loans (Billions of EUR)"
    )
    assets_trade_credit_and_advances: Optional[float] = Field(
        default=None, description="Assets Trade Credits and Advances (Billions of EUR)"
    )
    assets_eurosystem: Optional[float] = Field(
        default=None, description="Assets Eurosystem (Billions of EUR)"
    )
    assets_other_mfi_ex_eurosystem: Optional[float] = Field(
        default=None,
        description="Assets Other MFIs outside Eurosystem (Billions of EUR)",
    )
    assets_government: Optional[float] = Field(
        default=None, description="Assets Government (Billions of EUR)"
    )
    assets_other_sectors: Optional[float] = Field(
        default=None, description="Assets Other Sectors (Billions of EUR)"
    )
    liabilities_total: Optional[float] = Field(
        default=None, description="Liabilities Total (Billions of EUR)"
    )
    liabilities_currency_and_deposits: Optional[float] = Field(
        default=None, description="Liabilities Currency and Deposits (Billions of EUR)"
    )
    liabilities_loans: Optional[float] = Field(
        default=None, description="Liabilities Loans (Billions of EUR)"
    )
    liabilities_trade_credit_and_advances: Optional[float] = Field(
        default=None,
        description="Liabilities Trade Credits and Advances (Billions of EUR)",
    )
    liabilities_eurosystem: Optional[float] = Field(
        default=None, description="Liabilities Eurosystem (Billions of EUR)"
    )
    liabilities_other_mfi_ex_eurosystem: Optional[float] = Field(
        default=None,
        description="Liabilities Other MFIs outside Eurosystem (Billions of EUR)",
    )
    liabilities_government: Optional[float] = Field(
        default=None, description="Liabilities Government (Billions of EUR)"
    )
    liabilities_other_sectors: Optional[float] = Field(
        default=None, description="Liabilities Other Sectors (Billions of EUR)"
    )


class ECBCountry(Data):
    """ECB Balance of Payments Items by Country."""

    period: dateType = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    current_account_balance: Optional[float] = Field(
        default=None,
        description="Current Account Balance (Billions of EUR)",
    )
    current_account_credit: Optional[float] = Field(
        default=None,
        description="Current Account Credits (Billions of EUR)",
    )
    current_account_debit: Optional[float] = Field(
        default=None,
        description="Current Account Debits (Billions of EUR)",
    )
    goods_balance: Optional[float] = Field(
        default=None,
        description="Goods Balance (Billions of EUR)",
    )
    goods_credit: Optional[float] = Field(
        default=None,
        description="Goods Credits (Billions of EUR)",
    )
    goods_debit: Optional[float] = Field(
        default=None,
        description="Goods Debits (Billions of EUR)",
    )
    services_balance: Optional[float] = Field(
        default=None,
        description="Services Balance (Billions of EUR)",
    )
    services_credit: Optional[float] = Field(
        default=None,
        description="Services Credits (Billions of EUR)",
    )
    services_debit: Optional[float] = Field(
        default=None,
        description="Services Debits (Billions of EUR)",
    )
    primary_income_balance: Optional[float] = Field(
        default=None,
        description="Primary Income Balance (Billions of EUR)",
    )
    primary_income_credit: Optional[float] = Field(
        default=None,
        description="Primary Income Credits (Billions of EUR)",
    )
    primary_income_debit: Optional[float] = Field(
        default=None,
        description="Primary Income Debits (Billions of EUR)",
    )
    investment_income_balance: Optional[float] = Field(
        default=None,
        description="Investment Income Balance (Billions of EUR)",
    )
    investment_income_credit: Optional[float] = Field(
        default=None,
        description="Investment Income Credits (Billions of EUR)",
    )
    investment_income_debit: Optional[float] = Field(
        default=None,
        description="Investment Income Debits (Billions of EUR)",
    )
    secondary_income_balance: Optional[float] = Field(
        default=None,
        description="Secondary Income Balance (Billions of EUR)",
    )
    secondary_income_credit: Optional[float] = Field(
        default=None,
        description="Secondary Income Credits (Billions of EUR)",
    )
    secondary_income_debit: Optional[float] = Field(
        default=None,
        description="Secondary Income Debits (Billions of EUR)",
    )
    capital_account_balance: Optional[float] = Field(
        default=None,
        description="Capital Account Balance (Billions of EUR)",
    )
    capital_account_credit: Optional[float] = Field(
        default=None,
        description="Capital Account Credits (Billions of EUR)",
    )
    capital_account_debit: Optional[float] = Field(
        default=None,
        description="Capital Account Debits (Billions of EUR)",
    )
