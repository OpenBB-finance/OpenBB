"""Unit tests for ``openbb_ecb.utils.bps_series``."""

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
    """Every report returns a non-empty {field: key} dict of strings."""
    ids = generate_bps_series_ids("quarterly", report_type)
    assert ids and all(isinstance(v, str) for v in ids.values())


def test_corrected_keys_and_field_names():
    """The bug fixes are present in the generated keys/field names."""
    summary = generate_bps_series_ids("quarterly", "summary")
    assert summary["goods_debit"].split(".")[7:9] == ["D", "G"]  # was D.CA

    services = generate_bps_series_ids("quarterly", "services")
    assert "SF+SG" in services["financial_services_credit"]
    assert "SA+SB+SE+SH+SK+SL+SN" in services["other_services_credit"]

    inv = generate_bps_series_ids("quarterly", "investment_income")
    assert "debt_instruments_credit" in inv  # was debt_insruments
    assert "portofolio_investment_debt_instruments_debit" in inv  # match model

    portfolio = generate_bps_series_ids("quarterly", "portfolio_investment")
    assert "assets_equity_shares" in portfolio  # was assets_equity
    assert all(not v.startswith("BPS") for v in portfolio.values())  # flowRef dropped

    other = generate_bps_series_ids("quarterly", "other_investment")
    assert "assets_trade_credit_and_advances" in other  # was trade_credits


def test_invalid_report_returns_none():
    """An unrecognized report type falls through to None."""
    assert generate_bps_series_ids("quarterly", "not_a_report") is None


def test_country_branch():
    """The country branch embeds the country code."""
    country = generate_bps_series_ids("monthly", "main", country="united_states")
    code = BPS_COUNTRIES_DICT["united_states"]
    assert all(f".{code}." in v for v in country.values())


def test_frequency_logic():
    """Monthly is honored only for main/summary without a country; else forced to Q."""
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
