"""Tests for standard model field validators."""

from datetime import date, datetime

import pytest

pd = pytest.importorskip("pandas")

from openbb_core.provider.standard_models.bond_indices import (
    BondIndicesQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.bond_reference import (  # noqa: E402
    BondReferenceQueryParams,
)
from openbb_core.provider.standard_models.bond_trades import (
    BondTradesQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.company_filings import (  # noqa: E402
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.country_profile import (
    CountryProfileQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.currency_historical import (  # noqa: E402
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.standard_models.currency_snapshots import (  # noqa: E402
    CurrencySnapshotsQueryParams,
)
from openbb_core.provider.standard_models.ecb_interest_rates import (  # noqa: E402
    EuropeanCentralBankInterestRatesParams,
)
from openbb_core.provider.standard_models.equity_ftd import EquityFtdData  # noqa: E402
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.esg_risk_rating import (  # noqa: E402
    ESGRiskRatingData,
    ESGRiskRatingQueryParams,
)
from openbb_core.provider.standard_models.etf_performance import (
    ETFPerformanceQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.ffrmc import (
    SelectedTreasuryConstantMaturityQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.financial_attributes import (
    FinancialAttributesQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.form_13FHR import Form13FHRData  # noqa: E402
from openbb_core.provider.standard_models.fred_release_table import (  # noqa: E402
    ReleaseTableQueryParams,
)
from openbb_core.provider.standard_models.futures_curve import (  # noqa: E402
    FuturesCurveQueryParams,
)
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,  # noqa: E402
)
from openbb_core.provider.standard_models.historical_attributes import (
    HistoricalAttributesQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.insider_trading import (  # noqa: E402
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.standard_models.latest_attributes import (
    LatestAttributesQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.reported_financials import (  # noqa: E402
    ReportedFinancialsData,
    ReportedFinancialsQueryParams,
)
from openbb_core.provider.standard_models.spot import SpotRateQueryParams  # noqa: E402
from openbb_core.provider.standard_models.tbffr import (
    SelectedTreasuryBillQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.tmc import (
    TreasuryConstantMaturityQueryParams,  # noqa: E402
)
from openbb_core.provider.standard_models.treasury_auctions import (  # noqa: E402
    USTreasuryAuctionsQueryParams,
)
from openbb_core.provider.standard_models.weather_bulletin_download import (  # noqa: E402
    WeatherBulletinDownloadQueryParams,
)
from openbb_core.provider.standard_models.world_news import (  # noqa: E402
    WorldNewsQueryParams,
)
from openbb_core.provider.standard_models.yield_curve import (  # noqa: E402
    YieldCurveData,
    YieldCurveQueryParams,
)

pytestmark = pytest.mark.requires_pandas


def test_yield_curve_query_date_string_passes_through():
    q = YieldCurveQueryParams(date="2024-01-15")
    assert q.date == "2024-01-15"


def test_yield_curve_query_date_dateobject_to_string():
    q = YieldCurveQueryParams(date=date(2024, 1, 15))
    assert q.date == "2024-01-15"


def test_yield_curve_query_date_list():
    q = YieldCurveQueryParams(date=["2024-01-15", "2024-02-15"])
    assert q.date == "2024-01-15,2024-02-15"


def test_yield_curve_query_date_csv_string():
    q = YieldCurveQueryParams(date="2024-01-15,2024-02-15")
    assert q.date == "2024-01-15,2024-02-15"


def test_yield_curve_query_date_none():
    q = YieldCurveQueryParams(date=None)
    assert q.date is None


def test_yield_curve_data_maturity_years_year_month():
    d = YieldCurveData(maturity="year_5_month_6")
    assert d.maturity_years == pytest.approx(5.5)


def test_yield_curve_data_maturity_years_month_only():
    d = YieldCurveData(maturity="month_6")
    assert d.maturity_years == pytest.approx(0.5)


def test_yield_curve_data_maturity_years_no_underscore():
    d = YieldCurveData(maturity="overnight")
    assert d.maturity_years is None


def test_futures_curve_symbol_uppercased():
    q = FuturesCurveQueryParams(symbol="cl")
    assert q.symbol == "CL"


def test_futures_curve_date_dateobject():
    q = FuturesCurveQueryParams(symbol="cl", date=date(2024, 1, 15))
    assert q.date == "2024-01-15"


def test_futures_curve_date_list():
    q = FuturesCurveQueryParams(symbol="cl", date=["2024-01-15"])
    assert q.date == "2024-01-15"


def test_release_table_date_dateobject():
    q = ReleaseTableQueryParams(release_id="123", date=date(2024, 1, 15))
    assert q.date == "2024-01-15"


def test_release_table_date_string():
    q = ReleaseTableQueryParams(release_id="123", date="2024-01-15")
    assert q.date == "2024-01-15"


def test_release_table_date_list():
    q = ReleaseTableQueryParams(release_id="123", date=["2024-01-15"])
    assert q.date == "2024-01-15"


def test_release_table_date_none():
    q = ReleaseTableQueryParams(release_id="123")
    assert q.date is None


def test_weather_bulletin_urls_csv_string():
    q = WeatherBulletinDownloadQueryParams(urls="a.url,b.url")
    assert q.urls == ["a.url", "b.url"]


def test_weather_bulletin_urls_single_string():
    q = WeatherBulletinDownloadQueryParams(urls="a.url")
    assert q.urls == ["a.url"]


def test_weather_bulletin_urls_dict_with_urls_key():
    q = WeatherBulletinDownloadQueryParams(urls={"urls": ["a", "b"]})
    assert q.urls == ["a", "b"]


def test_weather_bulletin_urls_list_passthrough():
    q = WeatherBulletinDownloadQueryParams(urls=["a", "b"])
    assert q.urls == ["a", "b"]


def test_weather_bulletin_urls_invalid_raises():
    with pytest.raises(Exception):
        WeatherBulletinDownloadQueryParams(urls=42)


def test_world_news_defaults_dates_when_missing():
    q = WorldNewsQueryParams(start_date=None, end_date=None)
    assert q.start_date is not None
    assert q.end_date is not None


def test_world_news_keeps_supplied_dates():
    q = WorldNewsQueryParams(start_date="2024-01-01", end_date="2024-01-15")
    assert str(q.start_date) == "2024-01-01"
    assert str(q.end_date) == "2024-01-15"


def test_treasury_auctions_defaults_dates_when_missing():
    q = USTreasuryAuctionsQueryParams()
    assert q.start_date is not None
    assert q.end_date is not None


def test_treasury_auctions_validate_dates_passthrough_non_dict():
    marker = object()
    assert USTreasuryAuctionsQueryParams.validate_dates(marker) is marker


def test_treasury_auctions_keeps_supplied_dates():
    q = USTreasuryAuctionsQueryParams(start_date="2024-01-01", end_date="2024-01-31")
    assert str(q.start_date) == "2024-01-01"
    assert str(q.end_date) == "2024-01-31"


def test_insider_trading_date_validate_datetime_branch():
    d = InsiderTradingData(filing_date="2024-01-01T12:30:00")
    assert str(d.filing_date).startswith("2024-01-01 12:30:00")


def test_insider_trading_date_validate_date_and_none_branches():
    d = InsiderTradingData(filing_date="2024-01-01", transaction_date=None)
    assert str(d.filing_date) == "2024-01-01"
    assert d.transaction_date is None


def test_insider_trading_query_symbol_to_upper():
    q = InsiderTradingQueryParams(symbol="aapl")
    assert q.symbol == "AAPL"


def test_bond_reference_uppercase_and_list_conversion():
    q = BondReferenceQueryParams(isin=["us123", "gb456"], currency=["usd", "eur"])
    assert q.isin == "US123,GB456"
    assert q.currency == "USD,EUR"


def test_bond_reference_uppercase_string_branch():
    q = BondReferenceQueryParams(lei="abc123")
    assert q.lei == "ABC123"


def test_bond_reference_none_passthrough():
    q = BondReferenceQueryParams(isin=None, currency=None, lei=None)
    assert q.isin is None
    assert q.currency is None
    assert q.lei is None


def test_currency_historical_symbol_list_and_set_conversion():
    q1 = CurrencyHistoricalQueryParams(symbol=["eur-usd", "gbp-usd"])
    q2 = CurrencyHistoricalQueryParams(symbol={"usd-jpy"})
    assert q1.symbol == "EURUSD,GBPUSD"
    assert q2.symbol == "USDJPY"


def test_currency_historical_symbol_string_branch():
    q = CurrencyHistoricalQueryParams(symbol="eur-usd")
    assert q.symbol == "EURUSD"


def test_currency_historical_date_validator_datetime_and_date_branches():
    d1 = CurrencyHistoricalData(date="2024-01-01T12:30:00", close=1.0)
    d2 = CurrencyHistoricalData(date="2024-01-01", close=1.0)
    assert str(d1.date).startswith("2024-01-01 12:30:00")
    assert str(d2.date) == "2024-01-01"


def test_currency_snapshots_counter_currency_conversion():
    q = CurrencySnapshotsQueryParams(base="usd", counter_currencies=["eur", "gbp"])
    assert q.base == "USD"
    assert q.counter_currencies == "EUR,GBP"


def test_currency_snapshots_counter_currency_none():
    q = CurrencySnapshotsQueryParams(base="usd", counter_currencies=None)
    assert q.counter_currencies is None


def test_esg_risk_rating_data_symbol_list_to_upper():
    d = ESGRiskRatingData(
        symbol=["aapl", "msft"],
        cik="1",
        company_name="c",
        industry="i",
        year=2024,
        esg_risk_rating="A",
        industry_rank="1",
    )
    assert d.symbol == "AAPL,MSFT"


def test_esg_risk_rating_query_and_data_string_to_upper():
    q = ESGRiskRatingQueryParams(symbol="aapl")
    d = ESGRiskRatingData(
        symbol="aapl",
        cik="1",
        company_name="c",
        industry="i",
        year=2024,
        esg_risk_rating="A",
        industry_rank="1",
    )
    assert q.symbol == "AAPL"
    assert d.symbol == "AAPL"


def test_company_filings_symbol_list_and_none_conversion():
    q1 = CompanyFilingsQueryParams(symbol=["aapl", "msft"])
    q2 = CompanyFilingsQueryParams(symbol=None)
    assert q1.symbol == "AAPL,MSFT"
    assert q2.symbol is None


def test_company_filings_symbol_string_branch():
    q = CompanyFilingsQueryParams(symbol="aapl")
    assert q.symbol == "AAPL"


def test_company_filings_convert_date_none_branch():
    assert CompanyFilingsData.convert_date(None) is None


def test_release_table_date_explicit_none_triggers_validator():
    q = ReleaseTableQueryParams(release_id="123", date=None)
    assert q.date is None


def test_futures_curve_date_none_and_csv_string():
    q_none = FuturesCurveQueryParams(symbol="cl", date=None)
    q_csv = FuturesCurveQueryParams(symbol="cl", date="2024-01-15,2024-01-16")
    assert q_none.date is None
    assert q_csv.date == "2024-01-15,2024-01-16"


def test_remaining_standard_model_validators():
    assert BondIndicesQueryParams(index_type="YIELD").index_type == "yield"
    assert BondTradesQueryParams(isin="us123").isin == "US123"
    assert CompanyNewsQueryParams(symbol="aapl").symbol == "AAPL"
    assert CountryProfileQueryParams(country="United States").country == "united_states"
    assert CryptoHistoricalQueryParams(symbol="btc-usd").symbol == "BTC-USD"
    assert (
        EuropeanCentralBankInterestRatesParams(
            interest_rate_type="LENDING"
        ).interest_rate_type
        == "lending"
    )
    assert EquityPerformanceQueryParams(sort="ASC").sort == "asc"
    assert ETFPerformanceQueryParams(sort="DESC").sort == "desc"
    assert SelectedTreasuryConstantMaturityQueryParams(maturity="10Y").maturity == "10y"
    q = FinancialAttributesQueryParams(
        symbol="AAPL", tag="revenue", period="ANNUAL", sort="ASC"
    )
    assert q.period == "annual"
    assert q.sort == "asc"
    assert IndexConstituentsQueryParams(symbol="spx").symbol == "spx"
    assert (
        IndexConstituentsQueryParams.__dict__["_to_upper"].__func__.__wrapped__(
            IndexConstituentsQueryParams, "spx"
        )
        == "SPX"
    )
    assert SpotRateQueryParams(category="energy").category == "energy"
    assert SelectedTreasuryBillQueryParams(maturity="6M").maturity == "6m"
    assert TreasuryConstantMaturityQueryParams(maturity="3M").maturity == "3m"


def test_remaining_collection_none_and_direct_classmethod_branches():
    q = HistoricalAttributesQueryParams(
        symbol="aapl", tag=["Revenue", "EPS"], frequency=None, sort=None
    )
    assert q.tag == "revenue,eps"
    assert q.frequency is None
    assert q.sort is None

    q2 = LatestAttributesQueryParams(symbol="aapl", tag={"Revenue", "EPS"})
    assert q2.tag in {"revenue,eps", "eps,revenue"}

    rq = ReportedFinancialsQueryParams(
        symbol="AAPL", period="ANNUAL", statement_type="INCOME"
    )
    assert rq.period == "annual"
    assert rq.statement_type == "income"

    assert str(EquityFtdData.date_validate(datetime(2024, 1, 1))) == "2024-01-01"
    assert Form13FHRData.validate_option_type("CALL") == "call"
    assert FuturesHistoricalData.date_validate("2024-01-01T00:00:00").year == 2024
    assert ReportedFinancialsData.replace_zero({"a": 0, "b": 1}) == {"a": None, "b": 1}
