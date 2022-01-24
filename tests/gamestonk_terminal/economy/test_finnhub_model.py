# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import finnhub_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


@pytest.mark.vcr(record_mode="none")
def test_get_economy_calendar_events(mocker):
    # MOCK JSON
    mock_json = pd.DataFrame()
    mock_json["economicCalendar"] = ["MOCK_ROW_1", "MOCK_ROW_2"]

    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": mock_json,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = finnhub_model.get_economy_calendar_events()

    assert not result_df.empty


@pytest.mark.vcr(record_mode="none")
def test_get_economy_calendar_events_no_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = finnhub_model.get_economy_calendar_events()

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty
