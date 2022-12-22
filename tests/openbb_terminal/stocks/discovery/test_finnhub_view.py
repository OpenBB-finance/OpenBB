# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import finnhub_model, finnhub_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("from", "MOCK_FROM"),
            ("to", "MOCK_TO"),
            ("token", "MOCK_TOKEN"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_past_ipo(mocker):
    ipo_df = finnhub_model.get_ipo_calendar(
        start_date="2021-12-01",
        end_date="2021-12-02",
    )

    mocker.patch(
        "openbb_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=ipo_df,
    )

    finnhub_view.past_ipo(
        num_days_behind=2, start_date="2021-12-01", limit=20, export=""
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_future_ipo(mocker):
    ipo_df = finnhub_model.get_ipo_calendar(
        start_date="2021-12-01",
        end_date="2021-12-02",
    )

    mocker.patch(
        "openbb_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=ipo_df,
    )

    finnhub_view.future_ipo(
        num_days_ahead=2, end_date="2021-12-02", limit=20, export=""
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_past_ipo_empty_df(mocker):
    mocker.patch(
        "openbb_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=pd.DataFrame(),
    )

    finnhub_view.past_ipo(
        num_days_behind=2, start_date="2021-12-01", limit=20, export=""
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_future_ipo_empty_df(mocker):
    mocker.patch(
        "openbb_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=pd.DataFrame(),
    )

    finnhub_view.future_ipo(
        num_days_ahead=2, end_date="2021-12-02", limit=20, export=""
    )
