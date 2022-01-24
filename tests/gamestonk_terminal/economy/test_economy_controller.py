# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import economy_controller
from gamestonk_terminal.economy.fred.fred_controller import FredController

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "gamestonk_terminal.economy.economy_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.EconomyController.switch",
        return_value=["quit"],
    )
    result_menu = economy_controller.EconomyController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.economy.economy_controller"

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
        target=economy_controller.gtff,
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

    result_menu = economy_controller.EconomyController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.economy.economy_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=economy_controller.gtff,
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
        target=f"{path_controller}.EconomyController.switch",
        new=mock_switch,
    )

    result_menu = economy_controller.EconomyController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = economy_controller.EconomyController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["quit", "help"]),
        ("help/help", ["help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "reset",
                "economy",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = economy_controller.EconomyController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = economy_controller.EconomyController(queue=None)
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
                "economy",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "economy",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = economy_controller.EconomyController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_feargreed",
            [
                "jbd",
                "--export=png",
            ],
            "cnn_view.fear_and_greed_index",
            [],
            dict(
                indicator="jbd",
                export="png",
            ),
        ),
        (
            "call_overview",
            [
                "--export=csv",
            ],
            "wsj_view.display_overview",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_indices",
            [
                "--export=csv",
            ],
            "wsj_view.display_indices",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--export=csv",
            ],
            "wsj_view.display_futures",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_usbonds",
            [
                "--export=csv",
            ],
            "wsj_view.display_usbonds",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_glbonds",
            [
                "--export=csv",
            ],
            "wsj_view.display_glbonds",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--export=csv",
            ],
            "wsj_view.display_futures",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_currencies",
            [
                "--export=csv",
            ],
            "wsj_view.display_currencies",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_energy",
            [
                "--sortby=ticker",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Energy",
                sort_col="ticker",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_metals",
            [
                "--sortby=ticker",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Metals",
                sort_col="ticker",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_meats",
            [
                "--sortby=ticker",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Meats",
                sort_col="ticker",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_grains",
            [
                "--sortby=ticker",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Grains",
                sort_col="ticker",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_softs",
            [
                "--sortby=ticker",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Softs",
                sort_col="ticker",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_valuation",
            [
                "sector",
                "--sortby=MarketCap",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_valuation",
            [],
            dict(
                s_group="Sector",
                sort_col="MarketCap",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_performance",
            [
                "sector",
                "--sortby=Name",
                "-a",
                "--export=csv",
            ],
            "finviz_view.display_performance",
            [],
            dict(
                s_group="Sector",
                sort_col="Name",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_spectrum",
            [
                "sector",
                "--export=png",
            ],
            "finviz_view.display_spectrum",
            [],
            dict(
                s_group="Sector",
            ),
        ),
        (
            "call_map",
            [
                "--period=1w",
                "--type=world",
            ],
            "finviz_view.map_sp500_view",
            [],
            dict(
                period="1w",
                map_type="world",
            ),
        ),
        (
            "call_rtps",
            [
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.realtime_performance_sector",
            [],
            dict(
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_gdp",
            [
                "quarter",
                "--start=2011",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_real_gdp",
            [],
            dict(
                interval="q",
                start_year=2011,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_gdpc",
            [
                "--start=2011",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_gdp_capita",
            [],
            dict(
                start_year=2011,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_inf",
            [
                "--start=2011",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_inflation",
            [],
            dict(
                start_year=2011,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_cpi",
            [
                "--interval=monthly",
                "--start=2011",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_cpi",
            [],
            dict(
                interval="m",
                start_year=2011,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_tyld",
            [
                "10y",
                "--interval=monthly",
                "--start=2010-01-01",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_treasury_yield",
            [],
            dict(
                interval="m",
                maturity="10y",
                start_date=datetime.strptime("2010-01-01", "%Y-%m-%d"),
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_unemp",
            [
                "--start=2011",
                "--raw",
                "--export=csv",
            ],
            "alphavantage_view.display_unemployment",
            [],
            dict(
                start_year=2011,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_fred",
            [],
            "EconomyController.load_class",
            [FredController, []],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = economy_controller.EconomyController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = economy_controller.EconomyController(queue=None)
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
def test_call_bigmac_codes(mocker):
    path_controller = "gamestonk_terminal.economy.economy_controller"

    # MOCK CHECK_COUNTRY_CODE_TYPE
    mocker.patch(
        target=f"{path_controller}.nasdaq_model.check_country_code_type",
        return_value=["MOCK_COUNTRY_CODE"],
    )

    # MOCK READ_CSV
    mocker.patch(target=f"{path_controller}.pd.read_csv")

    # MOCK PRINT
    mock_print = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.console.print",
        new=mock_print,
    )

    controller = economy_controller.EconomyController(queue=None)
    other_args = [
        "--codes",
    ]
    controller.call_bigmac(other_args=other_args)

    mock_print.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_call_bigmac_countries(mocker):
    path_controller = "gamestonk_terminal.economy.economy_controller"

    # MOCK READ_CSV
    mocker.patch(
        target=f"{path_controller}.nasdaq_model.check_country_code_type",
        return_value=["MOCK_COUNTRY_CODE"],
    )

    # MOCK DISPLAY_BIG_MAC_INDEX
    mock_print = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.nasdaq_view.display_big_mac_index",
        new=mock_print,
    )

    controller = economy_controller.EconomyController(queue=None)
    other_args = [
        "--countries=MOCK_COUNTRY_CODE",
        "--raw",
        "--export=csv",
    ]
    controller.call_bigmac(other_args=other_args)

    mock_print.assert_called_with(
        country_codes=["MOCK_COUNTRY_CODE"],
        raw=True,
        export="csv",
    )
