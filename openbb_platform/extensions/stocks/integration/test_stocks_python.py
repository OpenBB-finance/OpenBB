"""Test stocks extension."""
import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 5})],
)
@pytest.mark.integration
def test_stocks_fa_balance(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.balance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_stocks_fa_balance_growth(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.balance_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 5})],
)
@pytest.mark.integration
def test_stocks_fa_cash(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.cash(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_stocks_fa_cash_growth(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.cash_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_comp(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.comp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_divs(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.divs(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_emp(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.emp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 30})],
)
@pytest.mark.integration
def test_stocks_fa_est(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.est(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 5})],
)
@pytest.mark.integration
def test_stocks_fa_income(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.income(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual"})],
)
@pytest.mark.integration
def test_stocks_fa_income_growth(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.income_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "transaction_type": ["P-Purchase"], "limit": 100})],
)
@pytest.mark.integration
def test_stocks_fa_ins(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.ins(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "date": "2023-01-01"})],
)
@pytest.mark.integration
def test_stocks_fa_ins_own(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.ins_own(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 100})],
)
@pytest.mark.integration
def test_stocks_fa_metrics(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.metrics(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_mgmt(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.mgmt(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_overview(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_pt(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.pt(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"}), ({"with_grade": True, "provider": "fmp", "symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_pta(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.pta(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 12})],
)
@pytest.mark.integration
def test_stocks_fa_ratios(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.ratios(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_stocks_fa_revgeo(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.revgeo(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_stocks_fa_revseg(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.revseg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 300}),
        ({"use_cache": True, "provider": "sec", "symbol": "AAPL", "limit": 300}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_filings(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.filings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_shrs(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.shrs(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_split(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.split(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "year": 1})],
)
@pytest.mark.integration
def test_stocks_fa_transcript(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.fa.transcript(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"date": "2023-01-01", "provider": "intrinio", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_options_chains(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.options.chains(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "delayed", "provider": "intrinio", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_options_unusual(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.options.unusual(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_gainers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.gainers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_losers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.losers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_active(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.active(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_undervalued_large_caps(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.undervalued_large_caps(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_aggressive_small_caps(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.aggressive_small_caps(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_stocks_disc_growth_tech_equities(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.growth_tech_equities(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"limit": 5})],
)
@pytest.mark.integration
def test_stocks_disc_top_retail(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.top_retail(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({}), ({"limit": 10, "provider": "seeking_alpha"})],
)
@pytest.mark.integration
def test_stocks_disc_upcoming_release_days(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.upcoming_release_days(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_dps_short_volume(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.dps.short_volume(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_dps_short_interest(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.dps.short_interest(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"tier": "T1", "is_ats": True, "provider": "finra", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_dps_otc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.dps.otc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbols": "AAPL,MSFT", "limit": 20}),
        (
            {
                "display": "full",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "sort": "created",
                "order": "desc",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        ({"order": "desc", "provider": "polygon", "symbols": "AAPL,MSFT", "limit": 20}),
    ],
)
@pytest.mark.integration
def test_stocks_news(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.news(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_price_performance(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.price_performance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
            }
        ),
        (
            {
                "status": "priced",
                "is_spo": True,
                "provider": "nasdaq",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_calendar_ipo(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.calendar_ipo(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06"})],
)
@pytest.mark.integration
def test_stocks_calendar_dividend(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.calendar_dividend(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({}), ({"market": "NASDAQ", "provider": "fmp"})],
)
@pytest.mark.integration
def test_stocks_market_snapshots(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.market_snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
