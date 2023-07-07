# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import fred_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [("check_series_id", {"series_id": "DGS5"})],
)
def test_output(func, kwargs_dict, recorder):
    payload = getattr(fred_model, func)(**kwargs_dict)
    assert len(payload) > 0
    assert "seriess" in payload
    recorder.capture(payload["seriess"])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        ("get_series_notes", {"search_query": "finance"}),
        ("get_series_data", {"series_id": "DGS10", "start_date": "2020-01-01"}),
    ],
)
def test_check_output(func, kwargs_dict, recorder):
    result_df = getattr(fred_model, func)(**kwargs_dict)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        ("check_series_id", {"series_id": "DGS5"}),
    ],
)
def test_invalid_response_status(func, kwargs_dict, mocker):
    # MOCK GET
    attrs = {
        "status_code": 400,
        "json.return_value": {"error_message": "mock error message"},
    }

    mock_response = mocker.Mock(**attrs)

    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    payload = getattr(fred_model, func)(**kwargs_dict)
    assert len(payload) == 0


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [("get_series_data", {"series_id": "DGS10", "start_date": "2020-01-01"})],
)
def test_load_data(func, kwargs_dict, recorder):
    result_df = getattr(fred_model, func)(**kwargs_dict)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        ("get_cpi", {"countries": ["united kingdom"]}),
        ("get_cpi", {"countries": ["united kingdom", "united_states"]}),
        ("get_cpi", {"countries": ["united kingdom", "united_states", "belgium"]}),
        (
            "get_cpi",
            {"countries": ["united kingdom", "united_states"], "frequency": "monthly"},
        ),
        (
            "get_cpi",
            {
                "countries": ["united kingdom", "united_states"],
                "units": "growth_previous",
            },
        ),
        (
            "get_cpi",
            {"countries": ["united kingdom", "united_states"], "harmonized": True},
        ),
        (
            "get_cpi",
            {
                "countries": ["united kingdom", "united_states"],
                "units": "growth_previous",
            },
        ),
    ],
)
def test_get_cpi(func, kwargs_dict, recorder):
    result_df = getattr(fred_model, func)(**kwargs_dict)

    assert isinstance(result_df, pd.DataFrame)
    recorder.capture(result_df)


@pytest.mark.vcr
def test_EQUITY_INDICES(recorder):
    assert isinstance(fred_model.EQUITY_INDICES, dict)
    recorder.capture(fred_model.EQUITY_INDICES)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_usd_liquidity_BAD_SYMBOL():
    fred_model.get_usd_liquidity("BAD_SYMBOL")
