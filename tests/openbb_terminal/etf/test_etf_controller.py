# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf import etf_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


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


EMPTY_DF = pd.DataFrame()
DF_ETF = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Open": 75.69999694824219,
            "High": 76.08999633789062,
            "Low": 75.41999816894531,
            "Close": 75.75,
            "Adj Close": 71.90919494628906,
            "Volume": 5539100,
            "date_id": 1,
            "OC_High": 75.75,
            "OC_Low": 75.69999694824219,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Open": 76.0199966430664,
            "High": 77.12999725341797,
            "Low": 75.69000244140625,
            "Close": 77.02999877929688,
            "Adj Close": 73.1242904663086,
            "Volume": 6791700,
            "date_id": 2,
            "OC_High": 77.02999877929688,
            "OC_Low": 76.0199966430664,
        },
    },
    orient="index",
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.etf.etf_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ETFController.switch",
        return_value=["quit"],
    )
    result_menu = etf_controller.ETFController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.etf.etf_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="openbb_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session",
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=etf_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = etf_controller.ETFController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.etf.etf_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=etf_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target=f"{path_controller}.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

    # MOCK SWITCH
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return ["quit"]

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch(
        target=f"{path_controller}.ETFController.switch",
        new=mock_switch,
    )

    result_menu = etf_controller.ETFController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = etf_controller.ETFController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "reset",
                "etf",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = etf_controller.ETFController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = etf_controller.ETFController(queue=None)
    controller.call_cls([])

    assert controller.queue == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            ["quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "help"]),
        ("call_home", [], ["quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "reset",
                "etf",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "etf",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = etf_controller.ETFController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_search",
            ["--name", "oil", "--source", "FinanceDatabase"],
            "financedatabase_view.display_etf_by_name",
            [],
            dict(name="oil", limit=5, export=""),
        ),
        (
            "call_search",
            ["--name", "oil", "--source", "StockAnalysis"],
            "stockanalysis_view.display_etf_by_name",
            [],
            dict(name="oil", limit=5, export=""),
        ),
        (
            "call_search",
            ["--description", "oil"],
            "financedatabase_view.display_etf_by_description",
            [],
            dict(description="oil", limit=5, export=""),
        ),
        (
            "call_overview",
            [],
            "stockanalysis_view.view_overview",
            [],
            dict(symbol="MOCK_ETF_NAME", export=""),
        ),
        (
            "call_holdings",
            ["6"],
            "stockanalysis_view.view_holdings",
            [],
            dict(symbol="MOCK_ETF_NAME", limit=6, export=""),
        ),
        (
            "call_weights",
            ["--raw"],
            "yfinance_view.display_etf_weightings",
            [],
            dict(name="MOCK_ETF_NAME", raw=True, min_pct_to_display=5, export=""),
        ),
        (
            "call_summary",
            [],
            "yfinance_view.display_etf_description",
            [],
            dict(name="MOCK_ETF_NAME"),
        ),
        (
            "call_pir",
            ["ARKW,ARKF", "--filename=hello.xlsx", "--folder=world"],
            "create_ETF_report",
            [["ARKW", "ARKF"]],
            dict(filename="hello.xlsx", folder="world"),
        ),
        (
            "call_pir",
            ["--filename=hello.xlsx", "--folder=world"],
            "create_ETF_report",
            [["MOCK_ETF_NAME"]],
            dict(filename="hello.xlsx", folder="world"),
        ),
        (
            "call_compare",
            ["--etfs=ARKW,ARKF"],
            "stockanalysis_view.view_comparisons",
            [["ARKW", "ARKF"]],
            dict(export=""),
        ),
        (
            "call_ca",
            [],
            "ca_controller.ComparisonAnalysisController.menu",
            [],
            dict(),
        ),
        (
            "call_ta",
            [],
            "ETFController.load_class",
            [
                etf_controller.ta_controller.TechnicalAnalysisController,
                "MOCK_ETF_NAME",
                DF_ETF.index[0],
                DF_ETF,
                [],
            ],
            dict(),
        ),
        (
            "call_disc",
            [],
            "ETFController.load_class",
            [etf_controller.disc_controller.DiscoveryController, []],
            dict(),
        ),
        (
            "call_scr",
            [],
            "ETFController.load_class",
            [etf_controller.screener_controller.ScreenerController, []],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.etf.etf_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = etf_controller.ETFController(queue=None)
        controller.etf_name = "MOCK_ETF_NAME"
        controller.etf_data = DF_ETF
        controller.etf_holdings = ["MOCK", "HOLDINGS"]

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = etf_controller.ETFController(queue=None)
        controller.etf_name = "MOCK_ETF_NAME"
        controller.etf_data = DF_ETF
        controller.etf_holdings = ["MOCK", "HOLDINGS"]
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr
def test_call_load(mocker):
    # FORCE SINGLE THREADING
    yf_download = etf_controller.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    controller = etf_controller.ETFController(queue=None)
    other_args = ["ARKW", "--start=2021-12-15", "--end=2021-12-18", "--limit=5"]
    controller.call_load(other_args=other_args)


@pytest.mark.skip
def test_call_candle(mocker):
    # FORCE SINGLE THREADING
    yf_download = etf_controller.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    # MOCK CANDLE
    mocker.patch(target="openbb_terminal.stocks.stocks_helper.display_candle")

    controller = etf_controller.ETFController(queue=None)
    other_args = ["ARKW", "--start=2021-12-15", "--end=2021-12-18", "--limit=5"]
    controller.call_load(other_args=other_args)
    controller.call_candle(other_args=[])


@pytest.mark.vcr(record_mode="none")
def test_call_news(mocker):
    mocker.patch(
        target="openbb_terminal.etf.etf_controller.yf.Ticker",
    )
    mocker.patch(
        target="openbb_terminal.etf.etf_controller.yf.Ticker.info",
        return_value={"shortName": "ARK Next Generation Internet ET"},
    )
    mock_news = mocker.Mock()
    mocker.patch(
        target="openbb_terminal.etf.etf_controller.newsapi_view.display_news",
        new=mock_news,
    )

    controller = etf_controller.ETFController(queue=None)
    controller.etf_name = "MOCK_ETF_NAME"

    controller.call_news(other_args=["-l=3", "-s=bbc"])

    mock_news.assert_called_once()
