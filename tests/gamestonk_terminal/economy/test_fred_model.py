# IMPORTATION STANDARD
import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import fred_model


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
        ("get_series_notes", {"series_term": "finance"}),
        ("get_series_data", {"series_id": "DGS10", "start": "2020-01-01"}),
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
        target="requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    payload = getattr(fred_model, func)(**kwargs_dict)
    assert len(payload) == 0


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [("get_series_data", {"series_id": "DGS10", "start": "2020-01-01"})],
)
def test_load_data(func, kwargs_dict, recorder):
    result_df = getattr(fred_model, func)(**kwargs_dict)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr
@pytest.mark.parametrize("date", [datetime.datetime(2022, 3, 21, 0, 0)])
def test_yield_curve(date, recorder):
    result_df, returned_date = fred_model.get_yield_curve(date)
    assert date.strftime("%Y-%m-%d") == returned_date.strftime("%Y-%m-%d")
    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr
@pytest.mark.parametrize("date", [datetime.datetime(2021, 7, 17, 0, 0)])
def test_yield_curve_weekend(date):
    result_df, returned_date = fred_model.get_yield_curve(date)
    assert date.strftime("%Y-%m-%d") == returned_date
    assert result_df.empty


@pytest.mark.vcr
@pytest.mark.parametrize("date", [None])
def test_yield_curve_none(date, recorder):
    result_df, returned_date = fred_model.get_yield_curve(date)
    assert returned_date.strftime("%Y-%m-%d") == "2022-03-21"
    assert not result_df.empty
    recorder.capture(result_df)
