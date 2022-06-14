# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.sector_industry_analysis import sia_controller

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
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.switch",
        return_value=["quit"],
    )
    result_menu = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=queue
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

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
        target=sia_controller.obbff,
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

    result_menu = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=sia_controller.obbff,
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
        target=f"{path_controller}.SectorIndustryAnalysisController.switch",
        new=mock_switch,
    )

    result_menu = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
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
        (
            "r",
            [
                "quit",
                "quit",
                "reset",
                "stocks",
                "sia",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
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
            ["quit", "quit", "quit"],
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
                "sia",
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
                "sia",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=queue
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_mktcap",
            [
                "Small",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_exchange",
            [],
            "",
            [],
            dict(),
        ),
        (
            "call_clear",
            [
                "industry",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_clear",
            [
                "sector",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_clear",
            [
                "country",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_clear",
            [
                "mktcap",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_sama",
            [],
            "",
            [],
            dict(),
        ),
        (
            "call_cps",
            [
                "--max=1",
                "--min=0.1",
                "--raw",
                "--export=csv",
            ],
            "financedatabase_view.display_companies_per_sector_in_country",
            [
                "United States",
                "Large",
                True,
                "csv",
                True,
                1,
                0.1,
            ],
            dict(),
        ),
        (
            "call_cpic",
            [
                "--max=1",
                "--min=0.1",
                "--raw",
                "--export=csv",
            ],
            "financedatabase_view.display_companies_per_industry_in_country",
            [
                "United States",
                "Large",
                True,
                "csv",
                True,
                1,
                0.1,
            ],
            dict(),
        ),
        (
            "call_cpis",
            [
                "--max=1",
                "--min=0.1",
                "--raw",
                "--export=csv",
            ],
            "financedatabase_view.display_companies_per_industry_in_sector",
            [
                "Financial Services",
                "Large",
                True,
                "csv",
                True,
                1,
                0.1,
            ],
            dict(),
        ),
        (
            "call_cpcs",
            [
                "--max=1",
                "--min=0.1",
                "--raw",
                "--export=csv",
            ],
            "financedatabase_view.display_companies_per_country_in_sector",
            [
                "Financial Services",
                "Large",
                True,
                "csv",
                True,
                1,
                0.1,
            ],
            dict(),
        ),
        (
            "call_cpci",
            [
                "--max=1",
                "--min=0.1",
                "--raw",
                "--export=csv",
            ],
            "financedatabase_view.display_companies_per_country_in_industry",
            [
                "Financial Data & Stock Exchanges",
                "Large",
                True,
                "csv",
                True,
                1,
                0.1,
            ],
            dict(),
        ),
        (
            "call_ca",
            [],
            "",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = sia_controller.SectorIndustryAnalysisController(
            ticker=None, queue=None
        )
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = sia_controller.SectorIndustryAnalysisController(
            ticker=None, queue=None
        )
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_industry",
        "call_sector",
        "call_country",
        "call_mktcap",
        "call_exchange",
        "call_cps",
        "call_cpic",
        "call_cpis",
        "call_cpcs",
        "call_cpci",
        "call_sama",
        "call_metric",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        target="openbb_terminal.stocks.sector_industry_analysis.sia_controller"
        ".SectorIndustryAnalysisController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "countries, sectors, industries",
    [
        (["MOCK_COUNTRY"], ["MOCK_SECTOR"], ["MOCK_INDUSTRY"]),
        (["MOCK_COUN"], ["MOCK_SEC"], ["MOCK_INDUS"]),
    ],
)
def test_controller_init_summary_profile(countries, industries, mocker, sectors):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK OBBFF
    mocker.patch(
        target=f"{path_controller}.obbff.USE_PROMPT_TOOLKIT",
        new=True,
    )

    # MOCK SESSION
    mocker.patch(
        target=f"{path_controller}.session",
    )

    # MOCK GET_JSON
    mock_get_json = {
        "summaryProfile": {
            "country": "MOCK_COUNTRY",
            "sector": "MOCK_SECTOR",
            "industry": "MOCK_INDUSTRY",
        },
    }
    target = f"{path_controller}.financedatabase_model.yf.utils.get_json"
    mocker.patch(target=target, return_value=mock_get_json)

    # MOCK GET_COUNTRIES
    target = f"{path_controller}.financedatabase_model.get_countries"
    mocker.patch(target=target, return_value=countries)

    # MOCK GET_SECTORS
    target = f"{path_controller}.financedatabase_model.get_sectors"
    mocker.patch(target=target, return_value=sectors)

    # MOCK GET_INDUSTRIES
    target = f"{path_controller}.financedatabase_model.get_industries"
    mocker.patch(target=target, return_value=industries)

    sia_controller.SectorIndustryAnalysisController(ticker="MOCK_TICKER", queue=None)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "market_cap",
    [
        1,
        2_000_000_001,
        10_000_000_001,
    ],
)
def test_controller_init_market_cap(market_cap, mocker):
    # MOCK GET_JSON
    mock_get_json = {"price": {"marketCap": market_cap}}
    target = "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.yf.utils.get_json"
    mocker.patch(target=target, return_value=mock_get_json)

    sia_controller.SectorIndustryAnalysisController(ticker="MOCK_TICKER", queue=None)


@pytest.mark.vcr(record_mode="none")
def test_update_runtime_choices(mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK OBBFF
    mocker.patch(
        target=f"{path_controller}.obbff.USE_PROMPT_TOOLKIT",
        new=True,
    )

    # MOCK SESSION
    mocker.patch(
        target=f"{path_controller}.session",
    )

    # MOCK GET_COUNTRIES
    mock_get_countries = mocker.Mock(return_value=["MOCK_COUNTRY_1"])
    target = f"{path_controller}.financedatabase_model.get_countries"
    mocker.patch(target=target, new=mock_get_countries)

    # MOCK GET_SECTORS
    mock_get_sectors = mocker.Mock(return_value=["MOCK_SECTOR_1"])
    target = f"{path_controller}.financedatabase_model.get_sectors"
    mocker.patch(target=target, new=mock_get_sectors)

    # MOCK GET_INDUSTRIES
    mock_get_industries = mocker.Mock(return_value=["MOCK_INDUSTRY_1"])
    target = f"{path_controller}.financedatabase_model.get_industries"
    mocker.patch(target=target, new=mock_get_industries)

    # SETUP CONTROLLER
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None,
        queue=None,
    )
    country = controller.country
    sector = controller.sector
    industry = controller.industry

    controller.update_runtime_choices()

    # ASSERT
    mock_get_countries.assert_called_with(
        industry=industry,
        sector=sector,
    )
    mock_get_sectors.assert_called_with(
        industry=industry,
        country=country,
    )
    mock_get_industries.assert_called_with(
        country=country,
        sector=sector,
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "name",
    ["MOCK_INDUSTRY_1", "MOCK_INDUS"],
)
def test_call_industry(mocker, name):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    # MOCK GET_INDUSTRIES
    mock_get_industries = mocker.Mock(return_value=["MOCK_INDUSTRY_1"])
    mocker.patch(
        target=f"{path_controller}.financedatabase_model.get_industries",
        new=mock_get_industries,
    )

    # MOCK GET_SECTORS
    mock_get_sectors = mocker.Mock(return_value=["MOCK_SECTOR_1"])
    mocker.patch(
        target=f"{path_controller}.financedatabase_model.get_sectors",
        new=mock_get_sectors,
    )

    # SETUP CONTROLLER
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    country = controller.country
    sector = controller.sector

    other_args = [f"--name={name}"]
    controller.call_industry(other_args=other_args)

    # ASSERT
    mock_get_industries.assert_called_with(
        country=country,
        sector=sector,
    )
    mock_get_sectors.assert_called_with(
        industry="MOCK_INDUSTRY_1",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "sia"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "countries, sectors, industries",
    [
        (["MOCK_COUNTRY"], ["MOCK_SECTOR"], ["MOCK_INDUSTRY"]),
        (["MOCK_COUN"], ["MOCK_SEC"], ["MOCK_INDUS"]),
    ],
)
def test_call_load(countries, industries, mocker, sectors):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK LOAD
    target = f"{path_controller}.stocks_helper.load"
    mocker.patch(target=target, return_value=DF_STOCK)

    # MOCK GET_JSON
    mock_get_json = {
        "summaryProfile": {
            "country": "MOCK_COUNTRY",
            "sector": "MOCK_SECTOR",
            "industry": "MOCK_INDUSTRY",
        },
    }
    target = f"{path_controller}.financedatabase_model.yf.utils.get_json"
    mocker.patch(target=target, return_value=mock_get_json)

    # MOCK GET_COUNTRIES
    target = f"{path_controller}.financedatabase_model.get_countries"
    mocker.patch(target=target, return_value=countries)

    # MOCK GET_SECTORS
    target = f"{path_controller}.financedatabase_model.get_sectors"
    mocker.patch(target=target, return_value=sectors)

    # MOCK GET_INDUSTRIES
    target = f"{path_controller}.financedatabase_model.get_industries"
    mocker.patch(target=target, return_value=industries)

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )

    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--end=2021-12-18",
    ]
    controller.call_load(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "market_cap",
    [
        1,
        2_000_000_001,
        10_000_000_001,
    ],
)
def test_call_load_market_cap(market_cap, mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK LOAD
    target = f"{path_controller}.stocks_helper.load"
    mocker.patch(target=target, return_value=DF_STOCK)

    # MOCK GET_JSON
    mock_get_json = {"price": {"marketCap": market_cap}}
    target = f"{path_controller}.financedatabase_model.yf.utils.get_json"
    mocker.patch(target=target, return_value=mock_get_json)

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )

    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--end=2021-12-18",
    ]
    controller.call_load(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
def test_call_ca(mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK COMPARISONANALYSISCONTROLLER
    target = f"{path_controller}.ca_controller.ComparisonAnalysisController"
    mocker.patch(target=target)

    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    controller.tickers = ["MOCK_TICKER_1"]
    controller.call_ca([])


@pytest.mark.vcr(record_mode="none")
def test_call_metric(mocker):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK DISPLAY_BARS_FINANCIALS
    mock_display_bars_financials = (None, None)
    target = f"{path_controller}.financedatabase_view.display_bars_financials"
    mocker.patch(target=target, return_value=mock_display_bars_financials)

    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    other_args = [
        "roa",
        "--limit=1",
        "--raw",
        "--export=csv",
    ]
    controller.call_metric(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "name",
    ["MOCK_COUNTRY_1", "MOCK_COUNT"],
)
def test_call_country(mocker, name):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    # MOCK GET_COUNTRIES
    mock_get_countries = mocker.Mock(return_value=["MOCK_COUNTRY_1"])
    mocker.patch(
        target=f"{path_controller}.financedatabase_model.get_countries",
        new=mock_get_countries,
    )

    # SETUP CONTROLLER
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    industry = controller.industry
    sector = controller.sector

    other_args = [f"--name={name}"]
    controller.call_country(other_args=other_args)

    # ASSERT
    mock_get_countries.assert_called_with(
        industry=industry,
        sector=sector,
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "name",
    ["MOCK_SECTOR_1", "MOCK_SECT"],
)
def test_call_sector(mocker, name):
    path_controller = "openbb_terminal.stocks.sector_industry_analysis.sia_controller"

    # MOCK UPDATE_RUNTIME_CHOICES
    mocker.patch(
        target=f"{path_controller}.SectorIndustryAnalysisController.update_runtime_choices",
    )

    # MOCK GET_COUNTRIES
    mock_get_sectors = mocker.Mock(return_value=["MOCK_SECTOR_1"])
    mocker.patch(
        target=f"{path_controller}.financedatabase_model.get_sectors",
        new=mock_get_sectors,
    )

    # SETUP CONTROLLER
    controller = sia_controller.SectorIndustryAnalysisController(
        ticker=None, queue=None
    )
    industry = controller.industry
    country = controller.country

    other_args = [f"--name={name}"]
    controller.call_sector(other_args=other_args)

    # ASSERT
    mock_get_sectors.assert_called_with(industry, country)
