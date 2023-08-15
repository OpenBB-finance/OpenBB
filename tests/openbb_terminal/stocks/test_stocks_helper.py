# IMPORTATION STANDARD

import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user

# IMPORTATION INTERNAL
from openbb_terminal.stocks import stocks_helper, stocks_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
            ("token", "MOCK_TOKEN"),
            ("apikey", "MOCK_API_KEY"),
            ("apiKey", "MOCK_API_KEY2"),
            ("api_key", "MOCK_API_KEY3"),
        ]
    }


@pytest.mark.vcr
def test_quote():
    stocks_view.display_quote(["GME"])


@pytest.mark.vcr
def test_multi_quote() -> None:
    stocks_view.display_quote(["AAPL", "MSFT", "AMZN", "TSLA", "BTCUSD"])


@pytest.mark.vcr
def test_quote_bad_ticker() -> None:
    stocks_view.display_quote(["F", "GM", "RIVN", "VW", "69420"])


@pytest.mark.default_cassette("test_search")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_search(mocker, use_tab):
    preferences = PreferencesModel(USE_TABULATE_DF=use_tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    df = stocks_helper.search(
        query="microsoft",
        country="United_States",
        sector="",
        industry="",
        industry_group="",
        exchange="",
        exchange_country="",
        all_exchanges=False,
    )
    stocks_helper.print_rich_table(
        df, show_index=False, title="Company Search Results", headers=df.columns
    )


@pytest.mark.vcr
@pytest.mark.parametrize(
    "interval, source",
    [
        (1440, "AlphaVantage"),
        (1440, "Intrinio"),
        (1440, "YahooFinance"),
        (60, "YahooFinance"),
        # (1440, "Polygon"),
        # (60, "Polygon"),
    ],
)
def test_load(interval, recorder, source):
    ticker = "GME"
    start = datetime.strptime("2021-12-01", "%Y-%m-%d")
    end = datetime.strptime("2021-12-02", "%Y-%m-%d")
    prepost = False
    result_df = stocks_helper.load(
        symbol=ticker,
        start_date=start,
        interval=interval,
        end_date=end,
        prepost=prepost,
        source=source,
    )
    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="once")
@pytest.mark.parametrize(
    "source, weekly, monthly",
    [
        ("AlphaVantage", True, True),
        ("AlphaVantage", True, False),
        ("AlphaVantage", False, True),
        ("YahooFinance", True, True),
        ("YahooFinance", True, False),
        ("YahooFinance", False, True),
        ("Polygon", True, True),
        ("Polygon", True, False),
        ("Polygon", False, True),
    ],
)
def test_load_week_or_month(recorder, source, weekly, monthly):
    ticker = "AAPL"
    start = datetime.strptime("2019-12-01", "%Y-%m-%d")
    end = datetime.strptime("2021-12-02", "%Y-%m-%d")
    prepost = False
    result_df = stocks_helper.load(
        symbol=ticker,
        start_date=start,
        interval=1440,
        end_date=end,
        prepost=prepost,
        source=source,
        weekly=weekly,
        monthly=monthly,
    )
    recorder.capture(result_df)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "path",
    [os.path.join(os.path.join("random_folder", "test69.csv"))],
)
def test_load_custom_output_wrong_path(path):
    stocks_helper.load_custom(path)


@pytest.mark.default_cassette("test_display_candle")
@pytest.mark.vcr
def test_display_candle():
    # LOAD DATA
    ticker = "GME"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    interval = 1440
    end = datetime.strptime("2020-12-08", "%Y-%m-%d")
    prepost = False
    source = "YahooFinance"
    df_stock = stocks_helper.load(
        symbol=ticker,
        start_date=start,
        interval=interval,
        end_date=end,
        prepost=prepost,
        source=source,
    )

    # PROCESS DATA
    df_stock = stocks_helper.process_candle(data=df_stock)

    # DISPLAY CANDLE
    s_ticker = "GME"
    stocks_helper.display_candle(
        symbol=s_ticker,
        data=df_stock,
    )
