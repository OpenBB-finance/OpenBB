"""Definitions and helpers for the BPS (Balance of Payments) ECB Series."""

from typing import Any, Literal, Optional

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
    None,
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


def generate_bps_series_ids(
    frequency: BPS_FREQUENCIES = "monthly",
    report_type: BPS_REPORT_TYPES = "main",
    country: Optional[BPS_COUNTRIES] = None,
) -> Any:
    """Generate series ids for EU area balance of payments reports."""

    freq = (
        BPS_FREQUENCIES_DICT[frequency]
        if report_type in ["main", "summary"] and not country
        else "Q"
    )

    if country is not None and country in BPS_COUNTRIES_DICT:
        country_items = dict(
            current_account_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.G._Z._Z._Z.EUR._T._X.N.ALL",
            services_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            investment_income_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.D4P._T.F._Z.EUR._T._X.N.ALL",  # noqa: E501
            investment_income_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.D4P._T.F._Z.EUR._T._X.N.ALL",  # noqa: E501
            investment_income_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.D4P._T.F._Z.EUR._T._X.N.ALL",
            secondary_income_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.IN2._Z._Z._Z.EUR._T._X.N.ALL",  # noqa: E501
            secondary_income_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.IN2._Z._Z._Z.EUR._T._X.N.ALL",  # noqa: E501
            secondary_income_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_balance=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.B.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_credit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.C.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_debit=f"BPS.{freq}.N.I9.{BPS_COUNTRIES_DICT[country]}.S1.S1.T.D.KA._Z._Z._Z.EUR._T._X.N.ALL",
        )
        return country_items

    if report_type == "main":
        main_items = dict(
            current_account=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL",
            services=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.KA._Z._Z._Z.EUR._T._X.N.ALL",
            net_lending_to_rest_of_world=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.CKA._Z._Z._Z.EUR._T._X.N.ALL",
            financial_account=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.FA._T.F._Z.EUR._T._X.N.ALL",
            direct_investment=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.FA.D.F._Z.EUR._T._X.N.ALL",
            portfolio_investment=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.FA.P.F._Z.EUR._T.M.N.ALL",
            financial_derivatives=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.FA.F.F7.T.EUR._T.T.N.ALL",
            other_investment=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.FA.O.F._Z.EUR._T._X.N.ALL",
            reserve_assets=f"BPS.{freq}.N.I9.W1.S121.S1.T.A.FA.R.F._Z.EUR.X1._X.N.ALL",
            errors_and_ommissions=f"BPS.{freq}.N.I9.W1.S1.S1.T.N.EO._Z._Z._Z.EUR._T._X.N.ALL",
        )
        return main_items

    if report_type == "summary":
        summary_items = dict(
            current_account_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.CA._Z._Z._Z.EUR._T._X.N.ALL",
            current_account_balance=f"BPS.{freq}.N.I9.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
            goods_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.G._Z._Z._Z.EUR._T._X.N.ALL",
            goods_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.CA._Z._Z._Z.EUR._T._X.N.ALL",
            services_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_employee_compensation_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.IN1._Z._Z._Z.EUR._T._X.N.ALL",
            primary_income_employee_compensation_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D1._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            secondary_income_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.IN2._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.KA._Z._Z._Z.EUR._T._X.N.ALL",
            capital_account_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.KA._Z._Z._Z.EUR._T._X.N.ALL",
        )
        return summary_items

    if report_type == "services":
        services_items = dict(
            services_total_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
            services_total_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
            transport_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SC._Z._Z._Z.EUR._T._X.N.ALL",
            transport_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SC._Z._Z._Z.EUR._T._X.N.ALL",
            travel_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SD._Z._Z._Z.EUR._T._X.N.ALL",
            travel_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SD._Z._Z._Z.EUR._T._X.N.ALL",
            financial_services_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SF._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SG._Z._Z._Z.EUR._T._X.N.ALL",  # noqa E501
            financial_services_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SF._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SG._Z._Z._Z.EUR._T._X.N.ALL",  # noqa E501
            communications_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SI._Z._Z._Z.EUR._T._X.N.ALL",
            communications_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SI._Z._Z._Z.EUR._T._X.N.ALL",
            other_business_services_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SJ._Z._Z._Z.EUR._T._X.N.ALL",
            other_business_services_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SJ._Z._Z._Z.EUR._T._X.N.ALL",
            other_services_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.SA._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SB._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SE._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SH._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SK._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SL._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.C.SN._Z._Z._Z.EUR._T._X.N.ALL",  # noqa E501
            other_services_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.SA._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SB._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SE._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SH._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SK._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SL._Z._Z._Z.EUR._T._X.N.ALL%20OR%20BPS.{freq}.N.I9.W1.S1.S1.T.D.SN._Z._Z._Z.EUR._T._X.N.ALL",  # noqa E501
        )
        return services_items

    if report_type == "investment_income":
        investment_income_items = dict(
            investment_total_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D4P._T.F._Z.EUR._T._X.N.ALL",
            investment_total_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D4P._T.F._Z.EUR._T._X.N.ALL",
            equity_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D4S.D.F5._Z.EUR._T._X.N.ALL",
            equity_reinvested_earnings_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D43S.D.F5._Z.EUR._T._X.N.ALL",
            equity_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D4S.D.F5._Z.EUR._T._X.N.ALL",
            equity_reinvested_earnings_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D43S.D.F5._Z.EUR._T._X.N.ALL",
            debt_insruments_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D4Q.D.FL._Z.EUR._T._X.N.ALL",
            debt_insruments_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D4Q.D.FL._Z.EUR._T._X.N.ALL",
            portfolio_investment_equity_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D4S.P.F5._Z.EUR._T._X.N.ALL",
            portfolio_investment_equity_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D4S.P.F5._Z.EUR._T._X.N.ALL",
            portfolio_investment_debt_instruments_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D41.P.F3.T.EUR._T._X.N.ALL",
            portfolio_investment_debt_instruments_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D41.P.F3.T.EUR._T._X.N.ALL",
            other_investment_credit=f"BPS.{freq}.N.I9.W1.S1.S1.T.C.D4P.O.F._Z.EUR._T._X.N.ALL",
            other_investment_debit=f"BPS.{freq}.N.I9.W1.S1.S1.T.D.D4P.O.F._Z.EUR._T._X.N.ALL",
            reserve_assets_credit=f"BPS.{freq}.N.I9.W1.S121.S1.T.C.D4P.R.F._Z.EUR.X1._X.N.ALL",
        )
        return investment_income_items

    if report_type == "direct_investment":
        direct_investment_items = dict(
            assets_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_equity=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.D.F5._Z.EUR._T._X.N.ALL",
            assets_debt_instruments=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.D.FL._Z.EUR._T._X.N.ALL",
            assets_mfi=f"BPS.{freq}.N.I9.W1.S12K.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_non_mfi=f"BPS.{freq}.N.I9.W1.S1Q.S1.LE.A.FA.D.F._Z.EUR._T._X.N.ALL",
            assets_direct_investment_abroad=f"BPS.{freq}.N.I9.W1.S1.S1.LE.NO.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_equity=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.D.F5._Z.EUR._T._X.N.ALL",
            liabilities_debt_instruments=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.D.FL._Z.EUR._T._X.N.ALL",
            liabilities_mfi=f"BPS.{freq}.N.I9.W1.S12K.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_non_mfi=f"BPS.{freq}.N.I9.W1.S1Q.S1.LE.L.FA.D.F._Z.EUR._T._X.N.ALL",
            liabilities_direct_investment_euro_area=f"BPS.{freq}.N.I9.W1.S1.S1.LE.NI.FA.D.F._Z.EUR._T._X.N.ALL",
        )
        return direct_investment_items

    if report_type == "portfolio_investment":
        portfolio_investment_items = dict(
            assets_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_equity_and_fund_shares=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F5._Z.EUR._T.M.N.ALL",
            assets_equity=f"BPS{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F51._Z.EUR._T.M.N.ALL",
            assets_investment_fund_shares=f"BPS{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F52._Z.EUR._T.M.N.ALL",
            assets_debt_short_term=f"BPS{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F3.S.EUR._T.M.N.ALL",
            assets_debt_long_term=f"BPS{freq}.N.I9.W1.S1.S1.LE.A.FA.P.F3.L.EUR._T.M.N.ALL",
            assets_resident_sector_eurosystem=f"BPS{freq}.N.I9.W1.S121.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_mfi_ex_eurosystem=f"BPS{freq}.N.I9.W1.S12T.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_government=f"BPS{freq}.N.I9.W1.S13.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_resident_sector_other=f"BPS{freq}.N.I9.W1.S1P.S1.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_issuer_sector_mfi=f"BPS{freq}.N.I9.W1.S1.S12K.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_issuer_sector_government=f"BPS{freq}.N.I9.W1.S1.S13.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            assets_issuer_sector_other=f"BPS{freq}.N.I9.W1.S1.S1P.LE.A.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_equity_and_fund_shares=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F5._Z.EUR._T.M.N.ALL",
            liabilities_equity=f"BPS{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F51._Z.EUR._T.M.N.ALL",
            liabilities_investment_fund_shares=f"BPS{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F52._Z.EUR._T.M.N.ALL",
            liabilities_debt_short_term=f"BPS{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F3.S.EUR._T.M.N.ALL",
            liabilities_debt_long_term=f"BPS{freq}.N.I9.W1.S1.S1.LE.L.FA.P.F3.L.EUR._T.M.N.ALL",
            liabilities_resident_sector_government=f"BPS{freq}.N.I9.W1.S13.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
            liabilities_resident_sector_other=f"BPS{freq}.N.I9.W1.S1P.S1.LE.L.FA.P.F._Z.EUR._T.M.N.ALL",
        )
        return portfolio_investment_items

    if report_type == "other_investment":
        other_investment_items = dict(
            assets_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_currency_and_deposits=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F2.T.EUR._T.N.N.ALL",
            assets_loans=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F4.T.EUR._T.N.N.ALL",
            assets_trade_credits_and_advances=f"BPS.{freq}.N.I9.W1.S1.S1.LE.A.FA.O.F81.T.EUR._T._X.N.ALL",
            assets_eurosystem=f"BPS.{freq}.N.I9.W1.S121.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_other_mfi_ex_eurosystem=f"BPS.{freq}.N.I9.W1.S12T.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_government=f"BPS.{freq}.N.I9.W1.S13.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            assets_other_sectors=f"BPS.{freq}.N.I9.W1.S1P.S1.LE.A.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_total=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_currency_and_deposits=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F2.T.EUR._T.N.N.ALL",
            liabilities_loans=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F4.T.EUR._T.N.N.ALL",
            liabilities_trade_credits_and_advances=f"BPS.{freq}.N.I9.W1.S1.S1.LE.L.FA.O.F81.T.EUR._T._X.N.ALL",
            liabilities_eurosystem=f"BPS.{freq}.N.I9.W1.S121.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_other_mfi_ex_eurosystem=f"BPS.{freq}.N.I9.W1.S12T.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_government=f"BPS.{freq}.N.I9.W1.S13.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
            liabilities_other_sectors=f"BPS.{freq}.N.I9.W1.S1P.S1.LE.L.FA.O.F._Z.EUR._T._X.N.ALL",
        )
        return other_investment_items
