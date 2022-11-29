# IMPORTATION STANDARD
import os
import datetime

# IMPORTATION THIRDPARTY
import pytest
import pandas as pd
from pandas import Timestamp

# IMPORTATION INTERNAL
from openbb_terminal.economy import economy_controller


# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111
# pylint: disable=C0302

# These are for the MACRO tests
MOCK_DF = pd.DataFrame.from_dict(
    {
        ("United Kingdom", "CPI"): {
            Timestamp("2022-08-01 00:00:00"): 123.1,
            Timestamp("2022-09-01 00:00:00"): 123.8,
        },
        ("United States", "CPI"): {
            Timestamp("2022-08-01 00:00:00"): 295.6,
            Timestamp("2022-09-01 00:00:00"): 296.8,
        },
    }
)
MOCK_UNITS = {"United States": {"CPI": "Index"}, "United Kingdom": {"CPI": "Index"}}

MOCK_FRED_NOTES = pd.DataFrame.from_dict(
    {
        "id": {0: "UNRATE"},
        "realtime_start": {0: "2022-11-04"},
        "realtime_end": {0: "2022-11-04"},
        "title": {0: "Unemployment Rate"},
        "observation_start": {0: "1948-01-01"},
        "observation_end": {0: "2022-10-01"},
        "frequency": {0: "Monthly"},
        "frequency_short": {0: "M"},
        "units": {0: "Percent"},
        "units_short": {0: "%"},
        "seasonal_adjustment": {0: "Seasonally Adjusted"},
        "seasonal_adjustment_short": {0: "SA"},
        "last_updated": {0: "2022-11-04 07:44:03-05"},
        "popularity": {0: 94},
        "group_popularity": {0: 94},
        "notes": {0: "The unemployment rate represents the number of unemployed"},
    }
)

MOCK_CHECK_IDS2 = {
    "realtime_start": "2022-11-04",
    "realtime_end": "2022-11-04",
    "seriess": [
        {
            "id": "DGS5",
            "realtime_start": "2022-11-04",
            "realtime_end": "2022-11-04",
            "title": "Market Yield on U.S. Treasury Securities at 5-Year Cons",
            "observation_start": "1962-01-02",
            "observation_end": "2022-11-03",
            "frequency": "Daily",
            "frequency_short": "D",
            "units": "Percent",
            "units_short": "%",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "seasonal_adjustment_short": "NSA",
            "last_updated": "2022-11-04 15:18:14-05",
            "popularity": 79,
            "notes": "For further information regarding treasury con",
        }
    ],
}

MOCK_CHECK_IDS1 = {
    "realtime_start": "2022-11-04",
    "realtime_end": "2022-11-04",
    "seriess": [
        {
            "id": "DGS2",
            "realtime_start": "2022-11-04",
            "realtime_end": "2022-11-04",
            "title": "Market Yield on U.S. Treasury Securities at 2-Year Constant Masis",
            "observation_start": "1976-06-01",
            "observation_end": "2022-11-03",
            "frequency": "Daily",
            "frequency_short": "D",
            "units": "Percent",
            "units_short": "%",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "seasonal_adjustment_short": "NSA",
            "last_updated": "2022-11-04 15:18:11-05",
            "popularity": 82,
            "notes": "For further information regarding treasury constant maturity data, please refer to ",
        }
    ],
}

MOCK_FRED_AGG = pd.DataFrame.from_dict(
    {
        "dgs2": {
            Timestamp("2022-11-02 00:00:00"): 4.61,
            Timestamp("2022-11-03 00:00:00"): 4.71,
        },
        "dgs5": {
            Timestamp("2022-11-02 00:00:00"): 4.3,
            Timestamp("2022-11-03 00:00:00"): 4.36,
        },
    }
)

MOCK_DETAIL = {
    "dgs2": {
        "title": "Market Yield on U.S. Treasury Securities at 2-Year Constant M",
        "units": "%",
    },
    "dgs5": {
        "title": "Market Yield on U.S. Treasury Securities at 5-Year Constant ",
        "units": "%",
    },
}


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.EconomyController.switch",
        return_value=["quit"],
    )
    result_menu = economy_controller.EconomyController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

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
        target=economy_controller.obbff,
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

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=economy_controller.obbff,
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

    assert result_menu == ["help"]


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
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
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
            "call_overview",
            [
                "--type=indices",
                "--export=csv",
            ],
            "wsj_view.display_indices",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_overview",
            [
                "--type=usbonds",
                "--export=csv",
            ],
            "wsj_view.display_usbonds",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_overview",
            [
                "--type=glbonds",
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
            "call_overview",
            [
                "--type=currencies",
                "--export=csv",
            ],
            "wsj_view.display_currencies",
            [],
            dict(
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--commodity=energy",
                "--source=Finviz",
                "--sortby=ticker",
                "-r",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Energy",
                sortby="ticker",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--commodity=metals",
                "--source=Finviz",
                "--sortby=ticker",
                "--reverse",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Metals",
                sortby="ticker",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--commodity=meats",
                "--source=Finviz",
                "--sortby=ticker",
                "-r",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Meats",
                sortby="ticker",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--commodity=grains",
                "--sortby=ticker",
                "--source=Finviz",
                "--reverse",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Grains",
                sortby="ticker",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_futures",
            [
                "--commodity=softs",
                "--sortby=ticker",
                "--source=Finviz",
                "-r",
                "--export=csv",
            ],
            "finviz_view.display_future",
            [],
            dict(
                future_type="Softs",
                sortby="ticker",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_valuation",
            [
                "sector",
                "--sortby=MarketCap",
                "--reverse",
                "--export=csv",
            ],
            "finviz_view.display_valuation",
            [],
            dict(
                group="sector",
                sortby="MarketCap",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_valuation",
            [
                "basic_materials",
                "--sortby=P/E",
                "-r",
                "--export=csv",
            ],
            "finviz_view.display_valuation",
            [],
            dict(
                group="basic_materials",
                sortby="P/E",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_performance",
            [
                "--g=sector",
                "--sortby=Name",
                "--reverse",
                "--export=csv",
            ],
            "finviz_view.display_performance",
            [],
            dict(
                group="sector",
                sortby="Name",
                ascend=True,
                export="csv",
            ),
        ),
        (
            "call_spectrum",
            [
                "--g=sector",
                "--export=png",
            ],
            "finviz_view.display_spectrum",
            [],
            dict(
                group="sector",
            ),
        ),
        (
            "call_map",
            [
                "--period=1w",
                "--type=world",
            ],
            "finviz_view.display_performance_map",
            [],
            dict(
                period="1w",
                map_filter="world",
            ),
        ),
        # TODO: Add `Investing` to sources again when `investpy` is fixed
        # (
        #     "call_ycrv",
        #     ["--country=portugal", "--export=csv", "--source=Investing"],
        #     "investingcom_view.display_yieldcurve",
        #     [],
        #     dict(country="portugal", export="csv", raw=False),
        # ),
        (
            "call_spread",
            [
                "--countries=United states, United Kingdom, France",
                "--export=csv",
            ],
            "investingcom_view.display_spread_matrix",
            [],
            dict(
                countries=["united states", "united kingdom", "france"],
                maturity="10Y",
                change=False,
                color="openbb",
                raw=False,
                export="csv",
            ),
        ),
        (
            "call_spread",
            ["--group=EZ", "--color=binary", "--maturity=5Y", "--change=True"],
            "investingcom_view.display_spread_matrix",
            [],
            dict(
                countries="EZ",
                maturity="5Y",
                change=True,
                color="binary",
                raw=False,
                export="",
            ),
        ),
        (
            "call_events",
            [
                "--export=csv",
                "--country=united_states",
                "--start=2022-10-20",
                "--end=2022-10-21",
                "--limit=10",
            ],
            "nasdaq_view.display_economic_calendar",
            [],
            dict(
                country=["United States"],
                start_date="2022-10-20",
                end_date="2022-10-21",
                export="csv",
                limit=10,
            ),
        ),
        (
            "call_events",
            [
                "--export=csv",
                "--country=united_states",
                "--date=2023-10-20",
                "--limit=10",
            ],
            "nasdaq_view.display_economic_calendar",
            [],
            dict(
                country=["United States"],
                start_date="2023-10-20",
                end_date="2023-10-20",
                export="csv",
                limit=10,
            ),
        ),
        (
            "call_edebt",
            [
                "--export=csv",
                "--limit=20",
            ],
            "commodity_view.display_debt",
            [],
            dict(
                export="csv",
                limit=20,
            ),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.economy.economy_controller"

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
    path_controller = "openbb_terminal.economy.economy_controller"

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
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK READ_CSV
    mocker.patch(
        target=f"{path_controller}.nasdaq_model.check_country_code_type",
        return_value=["VNM"],
    )

    # MOCK DISPLAY_BIG_MAC_INDEX
    mock_print = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.nasdaq_view.display_big_mac_index",
        new=mock_print,
    )

    controller = economy_controller.EconomyController(queue=None)
    other_args = [
        "--countries=VNM",
        "--raw",
        "--export=csv",
    ]
    controller.call_bigmac(other_args=other_args)

    mock_print.assert_called_with(
        country_codes=["VNM"],
        raw=True,
        export="csv",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "other_args, mocked_func, called_args, called_kwargs",
    [
        (
            [],
            "econdb_view.show_macro_data",
            [],
            dict(
                parameters=["CPI"],
                countries=["united_states"],
                transform="",
                start_date=None,
                end_date=None,
                symbol=False,
                raw=False,
                export="",
            ),
        ),
        (
            ["--countries=united_states,united_kingdom,CANADA"],
            "econdb_view.show_macro_data",
            [],
            dict(
                parameters=["CPI"],
                countries=["united_states", "united_kingdom", "canada"],
                transform="",
                start_date=None,
                end_date=None,
                symbol=False,
                raw=False,
                export="",
            ),
        ),
        (
            [
                "--countries=united_states,united_kingdom",
                "-s=2022-01-01",
                "-p=GDP,PPI",
                "-e=2022-10-10",
                "--export=csv",
                "--raw",
            ],
            "econdb_view.show_macro_data",
            [],
            dict(
                parameters=["GDP", "PPI"],
                countries=["united_states", "united_kingdom"],
                transform="",
                start_date="2022-01-01",
                end_date="2022-10-10",
                symbol=False,
                raw=True,
                export="csv",
            ),
        ),
    ],
)
def test_call_macro(mocked_func, other_args, called_args, called_kwargs, mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")
    # MOCK the econdb.get_aggregated_macro_data
    mocker.patch(
        target=f"{path_controller}.econdb_model.get_aggregated_macro_data",
        return_value=(MOCK_DF, MOCK_UNITS, "MOCK_NOTHINGS"),
    )
    mocker.patch(
        target="openbb_terminal.feature_flags.ENABLE_EXIT_AUTO_HELP",
        new=False,
    )

    mock = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.{mocked_func}",
        new=mock,
    )

    controller = economy_controller.EconomyController(queue=None)
    controller.choices = {}
    controller.call_macro(other_args)
    assert "macro" in controller.DATASETS
    assert not controller.DATASETS["macro"].empty
    if called_args or called_kwargs:
        mock.assert_called_once_with(*called_args, **called_kwargs)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_call_fred_query(mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    mocker.patch(
        target=f"{path_controller}.fred_model.get_series_notes",
        return_value=MOCK_FRED_NOTES,
    )

    mock = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.fred_view.notes",
        new=mock,
    )

    controller = economy_controller.EconomyController(queue=None)
    controller.choices = {}
    controller.call_fred(["--query", "MOCK_QUERY", "--limit", "1"])
    mock.assert_called_once_with(**dict(search_query="MOCK_QUERY", limit=1))


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "other_args, mocked_func, called_args, called_kwargs",
    [
        (
            ["--parameter=dgs2,dgs5"],
            "fred_view.display_fred_series",
            [],
            dict(
                series_ids=["DGS2", "DGS5"],
                start_date=None,
                end_date=None,
                limit=100,
                raw=False,
                export="",
                get_data=True,
            ),
        ),
        (
            ["--parameter=DgS2,dgs5", "--export=csv", "--raw"],
            "fred_view.display_fred_series",
            [],
            dict(
                series_ids=["DGS2", "DGS5"],
                start_date=None,
                end_date=None,
                limit=100,
                raw=True,
                export="csv",
                get_data=True,
            ),
        ),
        (
            ["--parameter=DgS2,dgs5", "--export=csv", "--start=2022-10-10"],
            "fred_view.display_fred_series",
            [],
            dict(
                series_ids=["DGS2", "DGS5"],
                start_date=datetime.datetime(2022, 10, 10, 0, 0),
                end_date=None,
                limit=100,
                raw=False,
                export="csv",
                get_data=True,
            ),
        ),
    ],
)
def test_call_fred_params(mocked_func, other_args, called_args, called_kwargs, mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    # MOCK the fred functions used
    mocker.patch(
        target=f"{path_controller}.fred_model.check_series_id",
        side_effect=[MOCK_CHECK_IDS1, MOCK_CHECK_IDS2],
    )
    mocker.patch(
        target=f"{path_controller}.fred_model.get_aggregated_series_data",
        return_value=(MOCK_FRED_AGG, MOCK_DETAIL),
    )
    mocker.patch(
        target="openbb_terminal.feature_flags.ENABLE_EXIT_AUTO_HELP",
        new=False,
    )

    mock = mocker.Mock(return_value=(MOCK_FRED_AGG, MOCK_DETAIL))
    mocker.patch(
        target=f"{path_controller}.{mocked_func}",
        new=mock,
    )

    controller = economy_controller.EconomyController(queue=None)
    controller.choices = {}
    controller.call_fred(other_args)
    assert "fred" in controller.DATASETS
    assert not controller.DATASETS["fred"].empty
    if called_args or called_kwargs:
        mock.assert_called_once_with(*called_args, **called_kwargs)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_show_indices():
    controller = economy_controller.EconomyController(queue=None)
    controller.call_index(["--show"])


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_show_treasury():
    controller = economy_controller.EconomyController(queue=None)
    controller.call_treasury(["--show"])


MOCK_INDEX = pd.DataFrame.from_dict(
    {
        Timestamp("2022-11-02 00:00:00"): 3759.68994140625,
        Timestamp("2022-11-03 00:00:00"): 3719.889892578125,
        Timestamp("2022-11-04 00:00:00"): 3770.550048828125,
    },
    orient="index",
)


@pytest.mark.vcr(record_mode="none")
def test_call_index(mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    # MOCK the fred functions used
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_index",
        return_value=MOCK_INDEX,
    )

    mocker.patch(
        target="openbb_terminal.feature_flags.ENABLE_EXIT_AUTO_HELP",
        new=False,
    )

    mock = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.yfinance_view.show_indices",
        new=mock,
    )

    controller = economy_controller.EconomyController(queue=None)
    controller.choices = {}
    controller.call_index(["-i", "SP500,DOW_DJUS", "-s", "2022-10-01"])

    mock.assert_called_once_with(
        **dict(
            indices=["SP500", "DOW_DJUS"],
            start_date="2022-10-01",
            end_date=None,
            raw=False,
            export="",
            interval="1d",
            column="Adj Close",
            returns=False,
        )
    )


MOCK_TREASURY_DEFAULT = pd.DataFrame.from_dict(
    {
        "Nominal_3-month": {"2022-10-01": 3.87},
        "Nominal_10-year": {"2022-10-01": 3.87},
        "Long-term average_Longer than 10-year": {"2022-10-01": 1.9},
    },
    orient="index",
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "other_args, mocked_func, called_args, called_kwargs",
    [
        (
            ["-m=3m,10y", "-t=nominal,average", "-e=2022-11-04"],
            "econdb_view.show_treasuries",
            [],
            dict(
                maturities=["3m", "10y"],
                instruments=["nominal", "average"],
                frequency="monthly",
                start_date="1934-01-31",
                end_date="2022-11-04",
                raw=False,
                export="",
            ),
        )
    ],
)
def test_call_treasury(mocked_func, other_args, called_args, called_kwargs, mocker):
    path_controller = "openbb_terminal.economy.economy_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")
    # MOCK the econdb.get_aggregated_macro_data
    mocker.patch(
        target=f"{path_controller}.econdb_model.get_treasuries",
        return_value=MOCK_TREASURY_DEFAULT,
    )
    mocker.patch(
        target="openbb_terminal.feature_flags.ENABLE_EXIT_AUTO_HELP",
        new=False,
    )

    mock = mocker.Mock()
    mocker.patch(
        target=f"{path_controller}.{mocked_func}",
        new=mock,
    )

    controller = economy_controller.EconomyController(queue=None)
    controller.choices = {}
    controller.call_treasury(other_args)
    assert "treasury" in controller.DATASETS
    assert not controller.DATASETS["treasury"].empty
    if called_args or called_kwargs:
        mock.assert_called_once_with(*called_args, **called_kwargs)
    else:
        mock.assert_called_once()
