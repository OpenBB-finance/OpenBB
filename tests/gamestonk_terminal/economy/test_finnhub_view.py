# IMPORTATION STANDARD
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import finnhub_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


MOCK_ECONOMY_CALENDAR_EVENTS_DICT = json.loads(
    """
{
  "economicCalendar": [
    {
      "actual": 8.4,
      "country": "AU",
      "estimate": 6.9,
      "event": "Australia - Current Account Balance",
      "impact": "low",
      "prev": 1,
      "time": "2020-06-02 01:30:00",
      "unit": "AUD"
    },
    {
      "actual": 0.5,
      "country": "AU",
      "estimate": 0.4,
      "event": "Australia- Net Exports",
      "impact": "low",
      "prev": -0.1,
      "time": "2020-06-02 01:30:00",
      "unit": "%"
    }
  ]
}
"""
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_economy_calendar_events_empty(mocker):
    # MOCK GET_ECONOMY_CALENDAR_EVENTS
    attrs = {"empty": True}
    mock_empty_df = mocker.Mock(**attrs)
    mocker.patch(
        target="gamestonk_terminal.economy.finnhub_view.finnhub_model.get_economy_calendar_events",
        new=mock_empty_df,
    )

    finnhub_view.economy_calendar_events(
        country="MOCK_COUNTRY",
        num=1,
        impact="MOCK_IMPACT",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_economy_calendar_events_no_country(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": MOCK_ECONOMY_CALENDAR_EVENTS_DICT,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    finnhub_view.economy_calendar_events(
        country="MOCK_COUNTRY",
        num=1,
        impact="MOCK_IMPACT",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_economy_calendar_events_no_impact(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": MOCK_ECONOMY_CALENDAR_EVENTS_DICT,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    finnhub_view.economy_calendar_events(
        country="AU",
        num=1,
        impact="MOCK_IMPACT",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_economy_calendar_events(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": MOCK_ECONOMY_CALENDAR_EVENTS_DICT,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    finnhub_view.economy_calendar_events(
        country="AU",
        num=1,
        impact="low",
        export="",
    )
