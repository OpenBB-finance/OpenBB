# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import finnhub_view, finnhub_model


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
@pytest.mark.parametrize("func", ["past_ipo", "future_ipo"])
def test_past_ipo(func, mocker):
    ipo_df = finnhub_model.get_ipo_calendar(
        from_date="2021-12-01",
        to_date="2021-12-02",
    )

    mocker.patch(
        "gamestonk_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=ipo_df,
    )

    getattr(finnhub_view, func)(2, "")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize("func", ["past_ipo", "future_ipo"])
def test_func_empty_df(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.finnhub_view.finnhub_model.get_ipo_calendar",
        return_value=pd.DataFrame(),
    )

    getattr(finnhub_view, func)(2, "")
