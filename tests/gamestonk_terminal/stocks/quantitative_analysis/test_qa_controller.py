# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.quantitative_analysis import qa_controller
from gamestonk_terminal import parent_classes

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

DF_STOCK = pd.DataFrame.from_dict(
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
EMPTY_DF = pd.DataFrame()
QA_CONTROLLER = qa_controller.QaController(
    ticker="MOCK_TICKER",
    start=datetime.strptime("2021-12-21", "%Y-%m-%d"),
    interval="MOCK_INTERVAL",
    stock=DF_STOCK.copy(),
)


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


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "gamestonk_terminal.stocks.quantitative_analysis.qa_controller."
            "QaController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = qa_controller.QaController(
        ticker="TSLA",
        start=datetime.strptime("2021-12-21", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK.copy(),
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session",
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=qa_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.quantitative_analysis.qa_controller.session",
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.quantitative_analysis.qa_controller.session.prompt",
        return_value="quit",
    )

    result_menu = qa_controller.QaController(
        ticker="TSLA",
        start=datetime.strptime("2021-12-21", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK.copy(),
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=qa_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.quantitative_analysis.qa_controller.session",
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
        target=(
            "gamestonk_terminal.stocks.quantitative_analysis.qa_controller."
            "QaController.switch"
        ),
        new=mock_switch,
    )

    result_menu = qa_controller.QaController(
        ticker="TSLA",
        start=datetime.strptime("2021-12-21", "%Y-%m-%d"),
        interval="1440min",
        stock=DF_STOCK.copy(),
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = qa_controller.QaController(
        ticker="",
        start="",
        interval="",
        stock=DF_STOCK.copy(),
    )
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
        ("r", ["quit", "quit", "reset", "stocks", "qa"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = qa_controller.QaController(
        ticker="",
        start="",
        interval="",
        stock=DF_STOCK.copy(),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = qa_controller.QaController(
        ticker="",
        start="",
        interval="",
        stock=DF_STOCK.copy(),
    )
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
            [
                "quit",
                "quit",
                "quit",
            ],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "qa",
                "pick returns",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "qa",
                "pick returns",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = qa_controller.QaController(
        ticker="MOCK_TICKER",
        start="",
        interval="",
        stock=DF_STOCK.copy(),
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_pick",
            [QA_CONTROLLER.target],
            "",
            [],
            dict(),
        ),
        (
            "call_raw",
            ["--limit=1", "--descend", "--export=csv"],
            "qa_view.display_raw",
            [QA_CONTROLLER.stock[QA_CONTROLLER.target]],
            dict(
                num=1,
                sort="",
                des=True,
                export="csv",
            ),
        ),
        (
            "call_summary",
            ["--export=csv"],
            "qa_view.display_summary",
            [],
            dict(
                df=QA_CONTROLLER.stock,
                export="csv",
            ),
        ),
        (
            "call_hist",
            ["--bins=1"],
            "qa_view.display_hist",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                bins=1,
            ),
        ),
        (
            "call_cdf",
            ["--export=csv"],
            "qa_view.display_cdf",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                export="csv",
            ),
        ),
        (
            "call_bw",
            ["--yearly"],
            "qa_view.display_bw",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                yearly=True,
            ),
        ),
        (
            "call_rolling",
            ["--window=1", "--export=csv"],
            "rolling_view.display_mean_std",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                window=1,
                export="csv",
            ),
        ),
        (
            "call_decompose",
            ["--multiplicative", "--export=csv"],
            "qa_view.display_seasonal",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                multiplicative=True,
                export="csv",
            ),
        ),
        (
            "call_cusum",
            ["--threshold=1", "--drift=2"],
            "qa_view.display_cusum",
            [],
            dict(
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                threshold=1,
                drift=2,
            ),
        ),
        (
            "call_acf",
            ["--lags=1"],
            "qa_view.display_acf",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                lags=1,
            ),
        ),
        (
            "call_spread",
            ["--window=1", "--export=csv"],
            "rolling_view.display_spread",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                window=1,
                export="csv",
            ),
        ),
        (
            "call_quantile",
            ["--window=1", "--quantile=0.1", "--export=csv"],
            "rolling_view.display_quantile",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                window=1,
                quantile=0.1,
                export="csv",
            ),
        ),
        (
            "call_skew",
            ["--window=1", "--export=csv"],
            "rolling_view.display_skew",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                window=1,
                export="csv",
            ),
        ),
        (
            "call_kurtosis",
            ["--window=1", "--export=csv"],
            "rolling_view.display_kurtosis",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                window=1,
                export="csv",
            ),
        ),
        (
            "call_normality",
            ["--export=csv"],
            "qa_view.display_normality",
            [],
            dict(
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                export="csv",
            ),
        ),
        (
            "call_qqplot",
            [],
            "qa_view.display_qqplot",
            [],
            dict(
                name=QA_CONTROLLER.ticker,
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
            ),
        ),
        (
            "call_unitroot",
            ["--fuller_reg=ctt", "--kps_reg=ct", "--export=csv"],
            "qa_view.display_unitroot",
            [],
            dict(
                df=QA_CONTROLLER.stock,
                target=QA_CONTROLLER.target,
                fuller_reg="ctt",
                kpss_reg="ct",
                export="csv",
            ),
        ),
        (
            "call_capm",
            ["--fuller_reg=ctt", "--kps_reg=ct", "--export=csv"],
            "capm_view",
            [QA_CONTROLLER.ticker],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            "gamestonk_terminal.stocks.quantitative_analysis.qa_controller."
            + mocked_func,
            new=mock,
        )

        getattr(QA_CONTROLLER, tested_func)(other_args=other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        getattr(QA_CONTROLLER, tested_func)(other_args=other_args)


@pytest.mark.vcr
def test_call_load(mocker):
    yf_download = parent_classes.stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)
    controller = qa_controller.QaController(
        ticker="MOCK_TICKER",
        start="MOCK_DATE",
        interval="MOCK_INTERVAL",
        stock=DF_STOCK.copy(),
    )
    other_args = [
        "TSLA",
        "--start=2021-12-17",
    ]
    old_stock = controller.stock
    controller.call_load(other_args=other_args)
    assert not controller.stock.empty
    assert not controller.stock.equals(old_stock)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "qa", "pick returns"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = qa_controller.QaController(
        ticker=None,
        start="MOCK_DATE",
        interval="MOCK_INTERVAL",
        stock=DF_STOCK.copy(),
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
