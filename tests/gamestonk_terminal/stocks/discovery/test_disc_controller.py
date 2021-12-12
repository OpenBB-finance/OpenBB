# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import disc_controller

# pylint: disable=E1101
# pylint: disable=W0603


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.discovery.disc_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.disc_controller.session.prompt",
        return_value="quit",
    )

    result_menu = disc_controller.menu()

    assert result_menu


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_system_exit(mocker):
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return True

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.discovery.disc_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.disc_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.disc_controller.DiscoveryController.switch",
        new=mock_switch,
    )

    disc_controller.menu()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    dd = disc_controller.DiscoveryController()
    dd.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    dd = disc_controller.DiscoveryController()
    result = dd.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    dd = disc_controller.DiscoveryController()
    result = dd.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    dd = disc_controller.DiscoveryController()
    result = dd.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    dd = disc_controller.DiscoveryController()
    other_args = list()
    result = dd.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    dd = disc_controller.DiscoveryController()
    other_args = list()
    result = dd.call_quit(other_args)

    assert result is True


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_active",
            "yahoofinance_view.display_active",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_arkord",
            "ark_view.ark_orders_view",
            ["--num=5", "--sortby=date", "--fund=ARKK", "--export=csv"],
            {
                "num": 5,
                "sort_col": ["date"],
                "ascending": False,
                "buys_only": False,
                "sells_only": False,
                "fund": "ARKK",
                "export": "csv",
            },
        ),
        (
            "call_asc",
            "yahoofinance_view.display_asc",
            [
                "--num=5",
                "--export=csv",
            ],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_cnews",
            "seeking_alpha_view.display_news",
            [
                "--type=technology",
                "--num=5",
                "--export=csv",
            ],
            {"news_type": "technology", "num": 5, "export": "csv"},
        ),
        (
            "call_fds",
            "financedatabase_view.show_equities",
            [
                "--country=MOCK_COUNTRY",
                "--sector=MOCK_SECTOR",
                "--industry=MOCK_INDUSTRY",
                "--name=MOCK_NAME",
                "--description=MOCK_DESCRIPTION",
                "--marketcap=Large",
                "--include_exchanges",
                "--amount=10",
                "--options=countries",
            ],
            {
                "country": ["MOCK_COUNTRY"],
                "sector": ["MOCK_SECTOR"],
                "industry": ["MOCK_INDUSTRY"],
                "name": ["MOCK_NAME"],
                "description": ["MOCK_DESCRIPTION"],
                "marketcap": ["Large"],
                "include_exchanges": False,
                "amount": 10,
                "options": "countries",
            },
        ),
        (
            "call_fipo",
            "finnhub_view.future_ipo",
            [
                "--num=5",
                "--export=csv",
            ],
            {"num_days_ahead": 5, "export": "csv"},
        ),
        (
            "call_ford",
            "fidelity_view.orders_view",
            [
                "--num=5",
                "--export=csv",
            ],
            {"num": 5, "export": "csv"},
        ),
        (
            "call_gainers",
            "yahoofinance_view.display_gainers",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_gtech",
            "yahoofinance_view.display_gtech",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_hotpenny",
            "shortinterest_view.hot_penny_stocks",
            ["--num=5", "--export=csv"],
            {"num": 5, "export": "csv"},
        ),
        (
            "call_losers",
            "yahoofinance_view.display_losers",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_lowfloat",
            "shortinterest_view.low_float",
            ["--num=5", "--export=csv"],
            {"num": 5, "export": "csv"},
        ),
        (
            "call_pipo",
            "finnhub_view.past_ipo",
            ["--num=5", "--export=csv"],
            {"num_days_behind": 5, "export": "csv"},
        ),
        (
            "call_rtat",
            "nasdaq_view.display_top_retail",
            ["--num=5", "--export=csv"],
            {"n_days": 5, "export": "csv"},
        ),
        (
            "call_rtearn",
            "geekofwallstreet_view.display_realtime_earnings",
            ["--export=csv"],
            ["csv"],
        ),
        (
            "call_trending",
            "seeking_alpha_view.news",
            [
                "--id=123",
                "--num=5",
                "--date=2020-12-02",
                "--export=csv",
            ],
            {
                "news_type": "trending",
                "article_id": 123,
                "num": 5,
                "start_date": datetime.strptime("2020-12-02", "%Y-%m-%d"),
                "export": "csv",
            },
        ),
        (
            "call_ugs",
            "yahoofinance_view.display_ugs",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_ulc",
            "yahoofinance_view.display_ulc",
            ["--num=5", "--export=csv"],
            {"num_stocks": 5, "export": "csv"},
        ),
        (
            "call_upcoming",
            "seeking_alpha_view.upcoming_earning_release_dates",
            ["--n_pages=10", "--num=5", "--export=csv"],
            {"num_pages": 10, "num_earnings": 5, "export": "csv"},
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.discovery." + mocked_func,
        new=mock,
    )
    fa = disc_controller.DiscoveryController()
    getattr(fa, tested_func)(other_args=other_args)

    if isinstance(called_with, dict):
        mock.assert_called_once_with(**called_with)
    elif isinstance(called_with, list):
        mock.assert_called_once_with(*called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_active",
        "call_arkord",
        "call_asc",
        "call_cnews",
        "call_fds",
        "call_fipo",
        "call_ford",
        "call_gainers",
        "call_gtech",
        "call_hotpenny",
        "call_losers",
        "call_lowfloat",
        "call_pipo",
        "call_rtat",
        "call_rtearn",
        "call_trending",
        "call_ugs",
        "call_ulc",
        "call_upcoming",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.disc_controller.parse_known_args_and_warn",
        return_value=None,
    )
    fa = disc_controller.DiscoveryController()

    func_result = getattr(fa, func)(other_args=list())
    assert func_result is None
    getattr(disc_controller, "parse_known_args_and_warn").assert_called_once()
