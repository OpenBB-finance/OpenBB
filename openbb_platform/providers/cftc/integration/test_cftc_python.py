import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        {
            "query": "grain",
            "report_type": "legacy",
            "futures_only": False,
            "category": None,
            "subcategory": None,
            "code": None,
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_cot_search(params, obb):
    result = obb.cftc.cot_search(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "code": "045601",
            "report_type": "legacy",
            "start_date": None,
            "end_date": None,
            "limit": 1,
            "futures_only": False,
            "measure": "all",
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_cot(params, obb):
    result = obb.cftc.cot(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"asset_class": "all", "provider": "cftc"},
        {"asset_class": "indices_bonds", "lookback_weeks": 26, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_index(params, obb):
    result = obb.cftc.cot_index(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    scores = [r.large_specs for r in result.results if r.large_specs is not None] + [
        r.commercials for r in result.results if r.commercials is not None
    ]
    assert scores
    assert all(0.0 <= score <= 100.0 for score in scores)


@pytest.mark.parametrize(
    "params",
    [
        {"asset_class": "all", "limit": 10, "provider": "cftc"},
        {"asset_class": "currencies", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_movers(params, obb):
    result = obb.cftc.cot_movers(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert len(result.results) <= params.get("limit", len(result.results))
    assert all(r.signal for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"code": "CFTC_088691", "provider": "cftc"},
        {"code": "CFTC_13874+", "lookback_weeks": 104, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_positioning(params, obb):
    result = obb.cftc.cot_positioning(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    dates = [r.report_date for r in result.results]
    assert dates == sorted(dates)

    scores = [
        r.large_specs_score for r in result.results if r.large_specs_score is not None
    ]
    assert all(0.0 <= score <= 100.0 for score in scores)


@pytest.mark.parametrize(
    "params",
    [
        {
            "jurisdiction": "cftc",
            "asset_class": "rates",
            "currency": "USD",
            "underlier": "SOFR",
            "action_type": "NEWT",
            "limit": 10,
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_swap_trades(params, obb):
    result = obb.cftc.swap_trades(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"currency": "USD", "provider": "cftc"},
        {
            "currency": "USD",
            "side": "receive",
            "min_notional": 50000000,
            "provider": "cftc",
        },
        {"currency": "GBP", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_swap_valuation(params, obb):
    result = obb.cftc.swap_valuation(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    periods = [r.period for r in result.results]
    assert periods == sorted(periods)
    assert all(r.discount_factor > 0.0 for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"currency": "USD", "provider": "cftc"},
        {"currency": "EUR", "side": "receive", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_swap_summary(params, obb):
    result = obb.cftc.swap_summary(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert all(r.metric and r.value for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"index": "SOFR", "provider": "cftc"},
        {"index": "EURIBOR", "provider": "cftc"},
        {
            "index": "SONIA",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_historical_fixings(params, obb):
    result = obb.cftc.historical_fixings(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    dates = [r.date for r in result.results]
    assert dates == sorted(dates)
    assert all(r.rate is not None for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {
            "index": None,
            "date": None,
            "tenor": None,
            "min_notional": None,
            "limit": 10,
            "provider": "cftc",
        },
        {
            "index": "CDX.NA.HY",
            "tenor": "5Y",
            "min_notional": 1000000,
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_cds_index_trades(params, obb):
    result = obb.cftc.cds_index_trades(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    assert all(
        row.coupon is not None
        or row.spread is not None
        or row.upfront_amount is not None
        for row in result.results
    )


@pytest.mark.parametrize(
    "params",
    [
        {"granularity": "benchmark", "provider": "cftc"},
        {"granularity": "observed", "min_trades": 1, "provider": "cftc"},
        {"source": "slice", "provider": "cftc"},
        {"overnight_anchor": True, "provider": "cftc"},
        {"currency": "CNY", "min_trades": 1, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_curve(params, obb):
    result = obb.cftc.ois_curve(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    factors = [
        r.discount_factor for r in result.results if r.discount_factor is not None
    ]
    assert all(a > b for a, b in zip(factors, factors[1:]))


@pytest.mark.parametrize(
    "params",
    [
        {"currency": ccy, "min_trades": 1, "provider": "cftc"}
        for ccy in (
            "USD",
            "EUR",
            "GBP",
            "JPY",
            "CAD",
            "CHF",
            "MXN",
            "SGD",
            "INR",
            "COP",
            "ZAR",
            "CLP",
        )
    ],
)
@pytest.mark.integration
def test_cftc_ois_curve_every_currency(params, obb):
    result = obb.cftc.ois_curve(**params)

    assert result
    assert len(result.results) > 0

    factors = [
        r.discount_factor for r in result.results if r.discount_factor is not None
    ]
    assert all(a > b for a, b in zip(factors, factors[1:]))
    assert all(r.staleness_days >= 0 for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cftc"},
        {"forward_tenor": "5Y", "forward_step": "1Y", "provider": "cftc"},
        {
            "currency": "GBP",
            "forward_tenor": "1Y",
            "forward_step": "1Y",
            "forward_count": 10,
            "provider": "cftc",
        },
    ],
)
@pytest.mark.integration
def test_cftc_ois_forward_curve(params, obb):
    result = obb.cftc.ois_forward_curve(**params)

    assert result
    assert len(result.results) > 0

    starts = [r.start_years for r in result.results]
    assert starts == sorted(starts)
    assert all(r.forward_rate is not None for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"pair": pair, "provider": "cftc"}
        for pair in (
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCHF",
            "USDCAD",
            "AUDUSD",
            "NZDUSD",
        )
    ],
)
@pytest.mark.integration
def test_cftc_fx_forward_points_every_pair(params, obb):
    result = obb.cftc.fx_forward_points(**params)

    assert result
    assert len(result.results) > 0
    assert result.results[0].tenor == "SPOT"


@pytest.mark.parametrize(
    "params",
    [
        {"tenor": "2Y,10Y", "provider": "cftc"},
        {"measure": "zero_rate", "pivot": False, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_curve_history(params, obb):
    result = obb.cftc.ois_curve_history(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"currency": "USD", "provider": "cftc"},
        {"currency": "EUR", "lookback_days": 30, "min_trades": 1, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_policy_path(params, obb):
    result = obb.cftc.ois_policy_path(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    starts = [r.start_date for r in result.results]
    assert starts == sorted(starts)
    assert all(r.num_trades >= 1 for r in result.results)
    assert all(r.staleness_days >= 0 for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"pair": "USDJPY", "provider": "cftc"},
        {"pair": "USDKRW", "provider": "cftc"},
        {"pair": "USDBRL", "source": "slice", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_forward_curve(params, obb):
    result = obb.cftc.fx_forward_curve(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    tenors = [r.tenor_days for r in result.results]
    assert tenors == sorted(tenors)
    assert all(r.rate > 0.0 and r.spot > 0.0 for r in result.results)


@pytest.mark.parametrize(
    "params",
    [
        {"pair": "EURUSD", "provider": "cftc"},
        {"pair": "USDJPY", "basis": "theoretical", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_implied_vol(params, obb):
    result = obb.cftc.fx_implied_vol(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0

    offsets = [r.strike_offset for r in result.results]
    assert offsets == sorted(offsets)
    assert any(
        getattr(row, column) is not None
        for row in result.results
        for column in ("vol_1w", "vol_1m", "vol_3m", "vol_6m", "vol_1y")
    )


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cftc"},
        {"pair": "EURUSD", "action_type": "NEWT", "provider": "cftc"},
        {"option_type": "Non-Deliverable", "provider": "cftc"},
        {"pair": "JPY", "min_notional": 50000000, "limit": 20, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_option_trades(params, obb):
    result = obb.cftc.fx_option_trades(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert len(result.results) <= params.get("limit", len(result.results))

    reported = [r.event_timestamp or r.execution_timestamp for r in result.results]
    assert reported == sorted(reported, reverse=True)


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "cftc"},
        {
            "product_type": "Non-Deliverable Forward",
            "action_type": "NEWT",
            "provider": "cftc",
        },
        {"settlement_currency": "USD", "provider": "cftc"},
        {"pair": "INR", "min_notional": 50000000, "limit": 20, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_forward_trades(params, obb):
    result = obb.cftc.fx_forward_trades(**params)

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert len(result.results) <= params.get("limit", len(result.results))

    reported = [r.event_timestamp or r.execution_timestamp for r in result.results]
    assert reported == sorted(reported, reverse=True)
