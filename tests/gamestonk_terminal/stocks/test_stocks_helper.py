# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal import helper_funcs


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
            ("token", "MOCK_TOKEN"),
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
def test_quote():
    stocks_helper.quote(["GME"], "GME")


@pytest.mark.default_cassette("test_search")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_search(mocker, use_tab):
    mocker.patch.object(
        target=helper_funcs.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )
    stocks_helper.search(query="pharma", amount=5)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "interval, source",
    [
        (1440, "av"),
        (1440, "iex"),
        (1440, "yf"),
        (60, "yf"),
    ],
)
def test_load(interval, recorder, source):
    ticker = "GME"
    start = datetime.strptime("2021-12-01", "%Y-%m-%d")
    end = datetime.strptime("2021-12-02", "%Y-%m-%d")
    prepost = False
    result_df = stocks_helper.load(
        ticker=ticker,
        start=start,
        interval=interval,
        end=end,
        prepost=prepost,
        source=source,
    )
    recorder.capture(result_df)


@pytest.mark.default_cassette("test_display_candle")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "use_matplotlib",
    [True, False],
)
def test_display_candle(mocker, use_matplotlib):

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    mocker.patch("plotly.basedatatypes.BaseFigure.show")

    # LOAD DATA
    ticker = "GME"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    interval = 1440
    end = datetime.strptime("2020-12-08", "%Y-%m-%d")
    prepost = False
    source = "yf"
    df_stock = stocks_helper.load(
        ticker=ticker,
        start=start,
        interval=interval,
        end=end,
        prepost=prepost,
        source=source,
    )

    # PROCESS DATA
    df_stock = stocks_helper.process_candle(df_data=df_stock)

    # DISPLAY CANDLE
    s_ticker = "GME"
    intraday = False
    stocks_helper.display_candle(
        s_ticker=s_ticker,
        df_stock=df_stock,
        use_matplotlib=use_matplotlib,
        intraday=intraday,
    )


@pytest.mark.vcr
def test_load_ticker(recorder):
    ticker = "PM"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    end = datetime.strptime("2020-12-02", "%Y-%m-%d")
    result_df = stocks_helper.load_ticker(ticker=ticker, start_date=start, end_date=end)
    recorder.capture(result_df)
