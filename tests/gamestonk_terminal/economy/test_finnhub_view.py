# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import finnhub_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


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
