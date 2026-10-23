"""Definitions and helpers for the BPS ECB series."""

from typing import Any, Literal

BPS_FREQUENCIES = Literal["monthly", "quarterly"]
BPS_FREQUENCIES_DICT = {"monthly": "M", "quarterly": "Q"}
BPS_REPORT_TYPES = Literal[
    "main",
    "summary",
    "services",
    "investment_income",
    "direct_investment",
    "portfolio_investment",
    "other_investment",
]

BPS_COUNTRIES = Literal[
    "brazil",
    "canada",
    "china",
    "eu_ex_euro_area",
    "eu_institutions",
    "india",
    "japan",
    "russia",
    "switzerland",
    "united_kingdom",
    "united_states",
    "total",
]

BPS_COUNTRIES_DICT = {
    "brazil": "BR",
    "canada": "CA",
    "china": "CN",
    "eu_ex_euro_area": "K11",
    "eu_institutions": "4A",
    "india": "IN",
    "japan": "JP",
    "russia": "RU",
    "switzerland": "CH",
    "united_kingdom": "GB",
    "united_states": "US",
    "total": "W1",
}


# pylint: disable=inconsistent-return-statements
def generate_bps_series_ids(
    frequency: BPS_FREQUENCIES = "monthly",
    report_type: BPS_REPORT_TYPES = "main",
    country: BPS_COUNTRIES | None = None,
) -> Any:
    """Generate SDMX data keys for euro area balance of payments."""

    freq = (
        BPS_FREQUENCIES_DICT[frequency]
        if report_type in ["main", "summary"] and not country
        else "Q"
    )

    if country is not None and country in BPS_COUNTRIES_DICT:
        c = BPS_COUNTRIES_DICT[country]
        return dict(
            current_account_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.G._Z._Z._Z.EUR._T._X.N.ALL",
            services_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            investment_income_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.D4P._T.F._Z.EUR._T._X.N.ALL",
            investment_income_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.D4P._T.F._Z.EUR._T._X.N.ALL",
            investment_income_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.D4P._T.F._Z.EUR._T._X.N.ALL",
            secondary_income_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_balance=f"{freq}.N.I9.{c}.S1.S1.T.B.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_credit=f"{freq}.N.I9.{c}.S1.S1.T.C.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_debit=f"{freq}.N.I9.{c}.S1.S1.T.D.KA._Z._Z._Z.EUR._T._X.N.ALL",
        )

    if report_type == "main":
        return dict(
            current_account=f"{freq}.N.I9.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods=f"{freq}.N.I9.W1.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL",
            services=f"{freq}.N.I9.W1.S1.S1.T.B.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income=f"{freq}.N.I9.W1.S1.S1.T.B.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income=f"{freq}.N.I9.W1.S1.S1.T.B.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account=f"{freq}.N.I9.W1.S1.S1.T.B.KA._Z._Z._Z.EUR._T._X.N.ALL",
            net_lending_to_rest_of_world=f"{freq}.N.I9.W1.S1.S1.T.B.CKA._Z._Z._Z.EUR._T._X.N.ALL",
            financial_account=f"{freq}.N.I9.W1.S1.S1.T.N.FA._T.F._Z.EUR._T._X.N.ALL",
            direct_investment=f"{freq}.N.I9.W1.S1.S1.T.N.FA.D.F._Z.EUR._T._X.N.ALL",
            portfolio_investment=f"{freq}.N.I9.W1.S1.S1.T.N.FA.P.F._Z.EUR._T.M.N.ALL",
            financial_derivatives=f"{freq}.N.I9.W1.S1.S1.T.N.FA.F.F7.T.EUR._T.T.N.ALL",
            other_investment=f"{freq}.N.I9.W1.S1.S1.T.N.FA.O.F._Z.EUR._T._X.N.ALL",
            reserve_assets=f"{freq}.N.I9.W1.S121.S1.T.A.FA.R.F._Z.EUR.X1._X.N.ALL",
            errors_and_omissions=f"{freq}.N.I9.W1.S1.S1.T.N.EO._Z._Z._Z.EUR._T._X.N.ALL",
        )

    if report_type == "summary":
        return dict(
            current_account_credit=f"{freq}.N.I9.W1.S1.S1.T.C.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_debit=f"{freq}.N.I9.W1.S1.S1.T.D.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_balance=f"{freq}.N.I9.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods_credit=f"{freq}.N.I9.W1.S1.S1.T.C.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_debit=f"{freq}.N.I9.W1.S1.S1.T.D.G._Z._Z._Z.EUR._T._X.N.ALL",
            services_credit=f"{freq}.N.I9.W1.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_debit=f"{freq}.N.I9.W1.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_credit=f"{freq}.N.I9.W1.S1.S1.T.C.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_employee_compensation_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_debit=f"{freq}.N.I9.W1.S1.S1.T.D.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_employee_compensation_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D1._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_credit=f"{freq}.N.I9.W1.S1.S1.T.C.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_debit=f"{freq}.N.I9.W1.S1.S1.T.D.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_credit=f"{freq}.N.I9.W1.S1.S1.T.C.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_debit=f"{freq}.N.I9.W1.S1.S1.T.D.KA._Z._Z._Z.EUR._T._X.N.ALL",
        )

    if report_type == "services":
        return dict(
            services_total_credit=f"{freq}.N.I9.W1.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_total_debit=f"{freq}.N.I9.W1.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            transport_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SC._Z._Z._Z.EUR._T._X.N.ALL",
            transport_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SC._Z._Z._Z.EUR._T._X.N.ALL",
            travel_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SD._Z._Z._Z.EUR._T._X.N.ALL",
            travel_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SD._Z._Z._Z.EUR._T._X.N.ALL",
            financial_services_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SF+SG._Z._Z._Z.EUR._T._X.N.ALL",
            financial_services_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SF+SG._Z._Z._Z.EUR._T._X.N.ALL",
            communications_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SI._Z._Z._Z.EUR._T._X.N.ALL",
            communications_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SI._Z._Z._Z.EUR._T._X.N.ALL",
            other_business_services_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SJ._Z._Z._Z.EUR._T._X.N.ALL",
            other_business_services_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SJ._Z._Z._Z.EUR._T._X.N.ALL",
            other_services_credit=f"{freq}.N.I9.W1.S1.S1.T.C.SA+SB+SE+SH+SK+SL+SN._Z._Z._Z.EUR._T._X.N.ALL",
            other_services_debit=f"{freq}.N.I9.W1.S1.S1.T.D.SA+SB+SE+SH+SK+SL+SN._Z._Z._Z.EUR._T._X.N.ALL",
        )

    if report_type == "investment_income":
        return dict(
            investment_total_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D4P._T.F._Z.EUR._T._X.N.ALL",
            investment_total_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D4P._T.F._Z.EUR._T._X.N.ALL",
            equity_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D4S.D.F5._Z.EUR._T._X.N.ALL",
            equity_reinvested_earnings_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D43S.D.F5._Z.EUR._T._X.N.ALL",
            equity_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D4S.D.F5._Z.EUR._T._X.N.ALL",
            equity_reinvested_earnings_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D43S.D.F5._Z.EUR._T._X.N.ALL",
            debt_instruments_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D4Q.D.FL._Z.EUR._T._X.N.ALL",
            debt_instruments_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D4Q.D.FL._Z.EUR._T._X.N.ALL",
            portfolio_investment_equity_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D4S.P.F5._Z.EUR._T._X.N.ALL",
            portfolio_investment_equity_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D4S.P.F5._Z.EUR._T._X.N.ALL",
            portfolio_investment_debt_instruments_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D41.P.F3.T.EUR._T._X.N.ALL",
            portofolio_investment_debt_instruments_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D41.P.F3.T.EUR._T._X.N.ALL",
            other_investment_credit=f"{freq}.N.I9.W1.S1.S1.T.C.D4P.O.F._Z.EUR._T._X.N.ALL",
            other_investment_debit=f"{freq}.N.I9.W1.S1.S1.T.D.D4P.O.F._Z.EUR._T._X.N.ALL",
            reserve_assets_credit=f"{freq}.N.I9.W1.S121.S1.T.C.D4P.R.F._Z.EUR.X1._X.N.ALL",
        )

    if report_type == "direct_investment":
        return dict(
            assets_total=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_equity=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.D.F5._Z.EUR._T._X.N.ALL",
            assets_debt_instruments=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.D.FL._Z.EUR._T._X.N.ALL",
            assets_mfi=f"{freq}.N.I9.W1.S12K.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_non_mfi=f"{freq}.N.I9.W1.S1Q.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_direct_investment_abroad=f"{freq}.N.I9.W1.S1.S1.LE.NO.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_total=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_equity=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.D.F5._Z.EUR._T._X.N.ALL",
            liabilities_debt_instruments=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.D.FL._Z.EUR._T._X.N.ALL",
            liabilities_mfi=f"{freq}.N.I9.W1.S12K.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_non_mfi=f"{freq}.N.I9.W1.S1Q.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_direct_investment_euro_area=f"{freq}.N.I9.W1.S1.S1.LE.NI.FA.D.F._Z.EUR._T._X.N.ALL",
        )

    if report_type == "portfolio_investment":
        return dict(
            assets_total=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_equity_and_fund_shares=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F5._Z.EUR._T.M.N.ALL",
            assets_equity_shares=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F51._Z.EUR._T.M.N.ALL",
            assets_investment_fund_shares=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F52._Z.EUR._T.M.N.ALL",
            assets_debt_short_term=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F3.S.EUR._T.M.N.ALL",
            assets_debt_long_term=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F3.L.EUR._T.M.N.ALL",
            assets_resident_sector_eurosystem=f"{freq}.N.I9.W1.S121.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_mfi_ex_eurosystem=f"{freq}.N.I9.W1.S12T.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_government=f"{freq}.N.I9.W1.S13.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_other=f"{freq}.N.I9.W1.S1P.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_total=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_equity_and_fund_shares=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F5._Z.EUR._T.M.N.ALL",
            liabilities_equity=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F51._Z.EUR._T.M.N.ALL",
            liabilities_investment_fund_shares=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F52._Z.EUR._T.M.N.ALL",
            liabilities_debt_short_term=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F3.S.EUR._T.M.N.ALL",
            liabilities_debt_long_term=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F3.L.EUR._T.M.N.ALL",
            liabilities_resident_sector_government=f"{freq}.N.I9.W1.S13.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_resident_sector_other=f"{freq}.N.I9.W1.S1P.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
        )

    if report_type == "other_investment":
        return dict(
            assets_total=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_currency_and_deposits=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F2.T.EUR._T.N.N.ALL",
            assets_loans=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F4.T.EUR._T.N.N.ALL",
            assets_trade_credit_and_advances=f"{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F81.T.EUR._T._X.N.ALL",
            assets_eurosystem=f"{freq}.N.I9.W1.S121.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_other_mfi_ex_eurosystem=f"{freq}.N.I9.W1.S12T.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_government=f"{freq}.N.I9.W1.S13.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_other_sectors=f"{freq}.N.I9.W1.S1P.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_total=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_currency_and_deposits=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F2.T.EUR._T.N.N.ALL",
            liabilities_loans=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F4.T.EUR._T.N.N.ALL",
            liabilities_trade_credit_and_advances=f"{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F81.T.EUR._T._X.N.ALL",
            liabilities_eurosystem=f"{freq}.N.I9.W1.S121.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_other_mfi_ex_eurosystem=f"{freq}.N.I9.W1.S12T.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_government=f"{freq}.N.I9.W1.S13.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_other_sectors=f"{freq}.N.I9.W1.S1P.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
        )
