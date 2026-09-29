"""Tests for the SEC N-MFP money market fund parser."""

from openbb_sec.utils.nmfp import _to_float, parse_nmfp


def _filing(schedule, series_level=None, general=None):
    """Build a minimal N-MFP filing structure."""
    return {
        "edgarSubmission": {
            "formData": {
                "generalInfo": general
                if general is not None
                else {
                    "nameOfSeries": "Test MMF",
                    "seriesId": "S000000001",
                    "reportDate": "2026-05-31",
                },
                "seriesLevelInfo": series_level or {},
                "scheduleOfPortfolioSecuritiesInfo": schedule,
            }
        }
    }


def test_to_float():
    """Cover numeric coercion branches."""
    assert _to_float("1.5") == 1.5
    assert _to_float(2) == 2.0
    assert _to_float(None) is None
    assert _to_float("") is None
    assert _to_float("abc") is None


def test_parse_nmfp_holdings_and_metrics():
    """Parse a representative filing with holdings and series metrics."""
    holding = {
        "nameOfIssuer": "United States Treasury",
        "titleOfIssuer": "T-Bill",
        "CUSIPMember": "912796",
        "ISINId": "US912796",
        "LEIID": "LEI123",
        "investmentCategory": "Treasury Debt",
        "finalLegalInvestmentMaturityDate": "2026-06-30",
        "includingValueOfAnySponsorSupport": "1000000.00",
        "percentageOfMoneyMarketFundNetAssets": "0.05",
        "yieldOfTheSecurityAsOfReportingDate": "0.0421",
    }
    series_level = {
        "netAssetOfSeries": "20000000.00",
        "totalValuePortfolioSecurities": "20500000.00",
        "cash": "100.00",
        "averagePortfolioMaturity": "15",
        "averageLifeMaturity": "40",
        "sevenDayGrossYield": [
            {"sevenDayGrossYieldValue": "0.0530"},
            {"sevenDayGrossYieldValue": "0.0540"},
        ],
    }
    holdings, metadata = parse_nmfp(_filing([holding], series_level))

    assert len(holdings) == 1
    row = holdings[0]
    assert row["name"] == "United States Treasury"
    assert row["weight"] == 5.0
    assert row["annualized_return"] == 4.21
    assert row["value"] == 1000000.0
    assert row["currency"] == "USD"
    assert metadata["fund_name"] == "Test MMF"
    assert metadata["net_assets"] == 20000000.0
    assert metadata["total_assets"] == 20500000.0
    assert metadata["seven_day_gross_yield"] == 0.054
    assert metadata["weighted_average_maturity"] == 15.0
    assert metadata["weighted_average_life"] == 40.0


def test_parse_nmfp_single_dict_schedule_and_yield():
    """Schedule and seven-day yield reported as single dicts; null weight/yield."""
    holding = {
        "nameOfIssuer": "X",
        "percentageOfMoneyMarketFundNetAssets": None,
        "yieldOfTheSecurityAsOfReportingDate": None,
    }
    series_level = {"sevenDayGrossYield": {"sevenDayGrossYieldValue": "0.05"}}
    holdings, metadata = parse_nmfp(_filing(holding, series_level))

    assert len(holdings) == 1
    assert holdings[0]["weight"] is None
    assert holdings[0]["annualized_return"] is None
    assert metadata["seven_day_gross_yield"] == 0.05


def test_parse_nmfp_yield_as_string_list():
    """Seven-day yield reported as a list of plain strings."""
    series_level = {"sevenDayGrossYield": ["0.04", "0.06"]}
    _, metadata = parse_nmfp(_filing([{"nameOfIssuer": "X"}], series_level))
    assert metadata["seven_day_gross_yield"] == 0.06


def test_parse_nmfp_empty_schedule_and_non_dict_items():
    """No schedule yields no holdings; non-dict entries are skipped."""
    holdings, metadata = parse_nmfp(_filing(None))
    assert holdings == []
    assert metadata["seven_day_gross_yield"] is None

    holdings2, _ = parse_nmfp(_filing(["not-a-dict", {"nameOfIssuer": "Y"}]))
    assert len(holdings2) == 1
    assert holdings2[0]["name"] == "Y"


def test_parse_nmfp_missing_formdata():
    """A filing without formData returns empty holdings and null metadata."""
    holdings, metadata = parse_nmfp({})
    assert holdings == []
    assert metadata["fund_name"] is None
    assert metadata["net_assets"] is None
