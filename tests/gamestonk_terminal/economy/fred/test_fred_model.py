import pytest
import requests
from gamestonk_terminal.economy.fred import fred_model


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
    result_tuple = getattr(fred_model, func)(**kwargs_dict)
    assert result_tuple[0] is True
    assert "seriess" in result_tuple[1]
    recorder.capture(result_tuple[1]["seriess"])


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
    mock_response = requests.Response()
    mock_response.status_code = 500
    mocker.patch(
        target="requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    result_tuple = getattr(fred_model, func)(**kwargs_dict)
    assert result_tuple[0] is False
    assert bool(result_tuple[1]) is False


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [("get_series_data", {"series_id": "DGS10", "start": "2020-01-01"})],
)
def test_load_data(func, kwargs_dict, recorder):
    result_df = getattr(fred_model, func)(**kwargs_dict)

    assert not result_df.empty
    recorder.capture(result_df)
