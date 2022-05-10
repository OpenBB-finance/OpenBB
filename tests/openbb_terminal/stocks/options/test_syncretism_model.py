# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options.screen import syncretism_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "put",
    [True, False],
)
def test_get_historical_greeks(put, recorder):
    result_df = syncretism_model.get_historical_greeks(
        ticker="PM",
        expiry="2022-01-07",
        chain_id="",
        strike=90,
        put=put,
    )
    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_historical_greeks_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = syncretism_model.get_historical_greeks(
        ticker="PM",
        expiry="2022-01-07",
        chain_id="PM220107P00090000",
        strike=90,
        put=True,
    )

    assert result_df.empty


@pytest.mark.vcr
def test_get_screener_output(recorder):
    presets_path = os.path.join(
        os.path.dirname(syncretism_model.__file__), "..", "presets/"
    )
    result_tuple = syncretism_model.get_screener_output(
        preset="high_IV",
        presets_path=presets_path,
    )
    recorder.capture(result_tuple[0])


@pytest.mark.vcr(record_mode="none")
def test_get_screener_output_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    presets_path = os.path.join(
        os.path.dirname(syncretism_model.__file__), "..", "presets/"
    )
    result_tuple = syncretism_model.get_screener_output(
        preset="high_IV",
        presets_path=presets_path,
    )

    assert result_tuple[0].empty
