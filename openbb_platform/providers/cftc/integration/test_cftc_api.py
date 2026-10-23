import pytest
import requests

BASE_URL = "http://localhost:8000/api/v1/cftc"


def _get(path: str, params: dict, headers: dict, timeout: int = 30):
    query = {
        p: str(v).lower() if isinstance(v, bool) else v
        for p, v in params.items()
        if v is not None
    }

    return requests.get(
        f"{BASE_URL}/{path}", params=query, headers=headers, timeout=timeout
    )


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
def test_cftc_cot_search(params, headers):
    result = _get("cot_search", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_cftc_cot(params, headers):
    result = _get("cot", params, headers)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"asset_class": "all", "provider": "cftc"},
        {"asset_class": "indices_bonds", "lookback_weeks": 26, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_index(params, headers):
    result = _get("cot_index", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"asset_class": "all", "limit": 10, "provider": "cftc"},
        {"asset_class": "currencies", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_movers(params, headers):
    result = _get("cot_movers", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"code": "CFTC_088691", "provider": "cftc"},
        {"code": "CFTC_13874+", "lookback_weeks": 104, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_cot_positioning(params, headers):
    result = _get("cot_positioning", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_swap_trades(params, headers):
    result = _get("swap_trades", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_cftc_swap_valuation(params, headers):
    result = _get("swap_valuation", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"currency": "USD", "provider": "cftc"},
        {"currency": "EUR", "side": "receive", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_swap_summary(params, headers):
    result = _get("swap_summary", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_historical_fixings(params, headers):
    result = _get("historical_fixings", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_cds_index_trades(params, headers):
    result = _get("cds_index_trades", params, headers, timeout=120)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"granularity": "benchmark", "provider": "cftc"},
        {"granularity": "observed", "min_trades": 1, "provider": "cftc"},
        {"source": "slice", "provider": "cftc"},
        {"currency": "CHF", "lookback_days": 30, "min_trades": 1, "provider": "cftc"},
        {"overnight_anchor": True, "provider": "cftc"},
        {"currency": "CNY", "min_trades": 1, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_curve(params, headers):
    result = _get("ois_curve", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_ois_forward_curve(params, headers):
    result = _get("ois_forward_curve", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"tenor": "2Y,10Y", "provider": "cftc"},
        {"measure": "zero_rate", "pivot": False, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_curve_history(params, headers):
    result = _get("ois_curve_history", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"pair": "EURUSD", "provider": "cftc"},
        {"pair": "USDJPY", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_forward_points(params, headers):
    result = _get("fx_forward_points", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"currency": "USD", "provider": "cftc"},
        {"currency": "EUR", "lookback_days": 30, "min_trades": 1, "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_ois_policy_path(params, headers):
    result = _get("ois_policy_path", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"pair": "USDJPY", "provider": "cftc"},
        {"pair": "USDKRW", "provider": "cftc"},
        {"pair": "USDBRL", "source": "slice", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_forward_curve(params, headers):
    result = _get("fx_forward_curve", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize(
    "params",
    [
        {"pair": "EURUSD", "provider": "cftc"},
        {"pair": "USDJPY", "basis": "theoretical", "provider": "cftc"},
    ],
)
@pytest.mark.integration
def test_cftc_fx_implied_vol(params, headers):
    result = _get("fx_implied_vol", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_fx_option_trades(params, headers):
    result = _get("fx_option_trades", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


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
def test_cftc_fx_forward_trades(params, headers):
    result = _get("fx_forward_trades", params, headers, timeout=300)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.parametrize("path", ["cot_choices", "ppd_date_choices", "apps.json"])
@pytest.mark.integration
def test_cftc_choice_endpoints(path, headers):
    result = _get(path, {}, headers, timeout=60)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
