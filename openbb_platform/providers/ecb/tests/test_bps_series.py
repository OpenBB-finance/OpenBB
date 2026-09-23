import pytest

from openbb_ecb.utils.bps_series import BPS_COUNTRIES_DICT, generate_bps_series_ids

REPORTS = [
    "main",
    "summary",
    "services",
    "investment_income",
    "direct_investment",
    "portfolio_investment",
    "other_investment",
]


@pytest.mark.parametrize("report_type", REPORTS)
def test_every_report_returns_keys(report_type):
    ids = generate_bps_series_ids("quarterly", report_type)
    assert ids and all(isinstance(v, str) for v in ids.values())


def test_corrected_keys_and_field_names():
    summary = generate_bps_series_ids("quarterly", "summary")
    assert summary["goods_debit"].split(".")[7:9] == ["D", "G"]

    services = generate_bps_series_ids("quarterly", "services")
    assert "SF+SG" in services["financial_services_credit"]
    assert "SA+SB+SE+SH+SK+SL+SN" in services["other_services_credit"]

    inv = generate_bps_series_ids("quarterly", "investment_income")
    assert "debt_instruments_credit" in inv
    assert "portofolio_investment_debt_instruments_debit" in inv

    portfolio = generate_bps_series_ids("quarterly", "portfolio_investment")
    assert "assets_equity_shares" in portfolio
    assert all(not v.startswith("BPS") for v in portfolio.values())

    other = generate_bps_series_ids("quarterly", "other_investment")
    assert "assets_trade_credit_and_advances" in other


def test_invalid_report_returns_none():
    assert generate_bps_series_ids("quarterly", "not_a_report") is None


def test_country_branch():
    country = generate_bps_series_ids("monthly", "main", country="united_states")
    code = BPS_COUNTRIES_DICT["united_states"]
    assert all(f".{code}." in v for v in country.values())


def test_frequency_logic():
    assert generate_bps_series_ids("monthly", "main")["goods"].startswith("M.")
    assert generate_bps_series_ids("monthly", "summary")["goods_credit"].startswith(
        "M."
    )
    assert generate_bps_series_ids("monthly", "services")[
        "transport_credit"
    ].startswith("Q.")
    assert generate_bps_series_ids("monthly", "main", country="japan")[
        "goods_balance"
    ].startswith("Q.")
