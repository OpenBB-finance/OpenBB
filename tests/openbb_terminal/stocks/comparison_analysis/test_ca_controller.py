# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.comparison_analysis import ca_controller

# pylint: disable=E1101
# pylint: disable=W0603

DF_EMPTY = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["historical", "help"], ["help"]),
        (["q", ".."], [".."]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "openbb_terminal.stocks.comparison_analysis.ca_controller."
            "ComparisonAnalysisController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = ca_controller.ComparisonAnalysisController(
        similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
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
        target=ca_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.stocks.comparison_analysis.ca_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.comparison_analysis.ca_controller.session.prompt",
        return_value="quit",
    )

    result_menu = ca_controller.ComparisonAnalysisController(
        similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["quit", " quit", "quit mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=ca_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="openbb_terminal.stocks.comparison_analysis.ca_controller.session",
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
            "openbb_terminal.stocks.comparison_analysis.ca_controller."
            "ComparisonAnalysisController.switch"
        ),
        new=mock_switch,
    )

    result_menu = ca_controller.ComparisonAnalysisController(
        similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = ca_controller.ComparisonAnalysisController()
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
        ("r", ["quit", "quit", "reset", "stocks", "ca"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = ca_controller.ComparisonAnalysisController()
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = ca_controller.ComparisonAnalysisController()
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
                "quit",
            ],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            ["quit", "quit", "reset", "stocks", "ca", "set MOCK_SIMILAR"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "ca", "set MOCK_SIMILAR", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = ca_controller.ComparisonAnalysisController(
        similar=["MOCK_SIMILAR"],
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_set",
            None,
            [
                "--similar=MOCK_TICKER_1,MOCK_TICKER_2",
            ],
            None,
        ),
        (
            "call_add",
            None,
            [
                "--similar=MOCK_TICKER_1,MOCK_TICKER_2",
            ],
            None,
        ),
        (
            "call_rmv",
            None,
            [
                "--similar=MOCK_TICKER_1,MOCK_TICKER_2",
            ],
            None,
        ),
        (
            "call_historical",
            "yahoo_finance_view.display_historical",
            [
                "--type=h",
                "--no-scale",
                "--start=2020-12-01",
                "--end=2022-12-11",
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                start_date="2020-12-01",
                end_date="2022-12-11",
                candle_type="h",
                normalize=False,
                export="csv",
            ),
        ),
        (
            "call_hcorr",
            "yahoo_finance_view.display_correlation",
            [
                "--type=h",
                "--start=2020-12-01",
                "--end=2022-12-11",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                start_date="2020-12-01",
                end_date="2022-12-11",
                candle_type="h",
                export="",
                display_full_matrix=False,
                raw=False,
            ),
        ),
        (
            "call_volume",
            "yahoo_finance_view.display_volume",
            [
                "--start=2020-12-01",
                "--end=2022-12-11",
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                start_date="2020-12-01",
                end_date="2022-12-11",
                export="csv",
            ),
        ),
        (
            "call_income",
            "marketwatch_view.display_income_comparison",
            [
                "--quarter",
                "--timeframe=MOCK_TIMEFRAME",
            ],
            dict(
                symbols=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                timeframe="MOCK_TIMEFRAME",
                quarter=True,
                export="",
            ),
        ),
        (
            "call_balance",
            "marketwatch_view.display_balance_comparison",
            [
                "--quarter",
                "--timeframe=MOCK_TIMEFRAME",
                "--export=csv",
            ],
            dict(
                symbols=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                timeframe="MOCK_TIMEFRAME",
                quarter=True,
                export="csv",
            ),
        ),
        (
            "call_cashflow",
            "marketwatch_view.display_cashflow_comparison",
            [
                "--quarter",
                "--timeframe=MOCK_TIMEFRAME",
                "--export=csv",
            ],
            dict(
                symbols=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                timeframe="MOCK_TIMEFRAME",
                quarter=True,
                export="csv",
            ),
        ),
        (
            "call_sentiment",
            "finbrain_view.display_sentiment_compare",
            [
                "--raw",
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_scorr",
            "finbrain_view.display_sentiment_correlation",
            [
                "--raw",
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_overview",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="overview",
                export="csv",
            ),
        ),
        (
            "call_valuation",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="valuation",
                export="csv",
            ),
        ),
        (
            "call_financial",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="financial",
                export="csv",
            ),
        ),
        (
            "call_ownership",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="ownership",
                export="csv",
            ),
        ),
        (
            "call_performance",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="performance",
                export="csv",
            ),
        ),
        (
            "call_technical",
            "finviz_compare_view.screener",
            [
                "--export=csv",
            ],
            dict(
                similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
                data_type="technical",
                export="csv",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            "openbb_terminal.stocks.comparison_analysis." + mocked_func,
            new=mock,
        )

        controller = ca_controller.ComparisonAnalysisController(
            similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
        )
        getattr(controller, tested_func)(other_args=other_args)

        if isinstance(called_with, dict):
            mock.assert_called_once_with(**called_with)
        elif isinstance(called_with, list):
            mock.assert_called_once_with(*called_with)
        else:
            mock.assert_called_once()
    else:
        controller = ca_controller.ComparisonAnalysisController(
            similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
        )
        getattr(controller, tested_func)(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_ticker",
        "call_get",
        "call_set",
        "call_add",
        "call_rmv",
        "call_historical",
        "call_hcorr",
        "call_volume",
        "call_income",
        "call_balance",
        "call_cashflow",
        "call_sentiment",
        "call_scorr",
        "call_overview",
        "call_valuation",
        "call_financial",
        "call_ownership",
        "call_performance",
        "call_technical",
        "call_tsne",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.comparison_analysis.ca_controller.ComparisonAnalysisController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = ca_controller.ComparisonAnalysisController(
        similar=["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"]
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_call_ticker(mocker):
    similar = ["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"]
    mock = mocker.Mock(return_value=pd.DataFrame())
    target = "yfinance.download"
    mocker.patch(target=target, new=mock)

    controller = ca_controller.ComparisonAnalysisController(similar=similar)
    controller.call_ticker(other_args=["MOCK_TICKER"])
    mock.assert_called_once_with("MOCK_TICKER", progress=False)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args",
    [
        (
            "call_get",
            "finviz_compare_model.get_similar_companies",
            ["--nocountry", "--source=Finviz"],
        ),
        (
            "call_get",
            "polygon_model.get_similar_companies",
            ["--us_only", "--source=Polygon"],
        ),
        (
            "call_get",
            "finnhub_model.get_similar_companies",
            ["--source=Finnhub"],
        ),
    ],
)
def test_func_calling_get_similar_companies(
    tested_func, mocked_func, other_args, mocker
):
    similar = ["MOCK_SIMILAR_" + str(i) for i in range(11)]
    mock = mocker.Mock(return_value=similar)
    target = "openbb_terminal.stocks.comparison_analysis." + mocked_func
    mocker.patch(target=target, new=mock)

    controller = ca_controller.ComparisonAnalysisController(similar=["MOCK_SIMILAR"])
    getattr(controller, tested_func)(other_args=other_args)
    mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_call_tsne(mocker):
    similar = ["MOCK_SIMILAR"]
    mock = mocker.Mock(return_value=pd.DataFrame())
    target = "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_sp500_comps_tsne"
    mocker.patch(target=target, new=mock)

    controller = ca_controller.ComparisonAnalysisController(similar=similar)
    controller.call_tsne(
        other_args=[
            "--learnrate=100",
            "--limit=5",
            "--no_plot",
        ]
    )
    mock.assert_called_once_with(
        symbol="MOCK_SIMILAR",
        lr=100,
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "similar, expected",
    [
        (None, []),
        (
            ["MOCK_SIMILAR_1", "MOCK_SIMILAR_2"],
            ["stocks", "ca", "set MOCK_SIMILAR_1,MOCK_SIMILAR_2"],
        ),
    ],
)
def test_custom_reset(expected, similar):
    controller = ca_controller.ComparisonAnalysisController(
        similar=None,
        queue=None,
    )
    controller.similar = similar

    result = controller.custom_reset()

    assert result == expected
