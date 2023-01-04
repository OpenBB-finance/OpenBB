# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import yfinance_view


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


@pytest.mark.default_cassette("test_plot_oi")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "calls_only, puts_only, min_sp, max_sp",
    [
        (False, False, 80.0, 90.0),
        (True, True, -1, -1),
    ],
)
def test_plot_oi(calls_only, max_sp, min_sp, mocker, puts_only):
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_oi(
        symbol="AAPL",
        expiry="2023-07-21",
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        export="",
    )


@pytest.mark.default_cassette("test_plot_vol")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "calls_only, puts_only, min_sp, max_sp",
    [
        (False, False, 80.0, 90.0),
        (True, True, -1, -1),
    ],
)
def test_plot_vol(calls_only, max_sp, min_sp, mocker, puts_only):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_vol(
        symbol="AAPL",
        expiry="2023-07-21",
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        export="",
    )


@pytest.mark.default_cassette("test_plot_volume_open_interest")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "min_sp, max_sp, min_vol",
    [
        (80.0, 90.0, 0.0),
        (-1, -1, -1),
    ],
)
def test_plot_volume_open_interest(max_sp, min_sp, min_vol, mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_volume_open_interest(
        symbol="AAPL",
        expiry="2023-07-21",
        min_sp=min_sp,
        max_sp=max_sp,
        min_vol=min_vol,
        export="",
    )


@pytest.mark.default_cassette("test_plot_plot")
@pytest.mark.vcr
def test_plot_plot(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_plot(
        symbol="AAPL",
        expiry="2023-07-21",
        put=True,
        x="c",
        y="v",
        custom="smile",
        export="jpg",
    )


@pytest.mark.default_cassette("test_plot_payoff")
@pytest.mark.vcr
def test_plot_payoff(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_payoff(
        current_price=95.0, options=[], underlying=0, symbol="AAPL", expiry="2023-07-21"
    )


@pytest.mark.default_cassette("test_show_parity")
@pytest.mark.vcr
def test_show_parity(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.show_parity(
        symbol="AAPL",
        expiry="2023-07-21",
        put=True,
        ask=True,
        mini=0.0,
        maxi=100.0,
        export="csv",
    )


@pytest.mark.default_cassette("test_risk_neutral_vals")
@pytest.mark.vcr
def test_risk_neutral_vals(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.risk_neutral_vals(
        symbol="AAPL",
        expiry="2023-07-21",
        put=True,
        data=pd.DataFrame(columns=["Price", "Chance"]),
        mini=None,
        maxi=None,
        risk=None,
    )


@pytest.mark.default_cassette("test_show_binom")
@pytest.mark.vcr
def test_show_binom(mocker):
    # MOCK CHARTS
    mocker.patch(
        target="openbb_terminal.stocks.options.yfinance_view.theme.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    # MOCK EXPORT_BINOMIAL_CALCS
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.Workbook.save")

    yfinance_view.show_binom(
        symbol="AAPL",
        expiry="2023-07-21",
        strike=90.0,
        put=True,
        europe=False,
        export=False,
        plot=True,
        vol=None,
    )


@pytest.mark.default_cassette("test_show_greeks")
@pytest.mark.vcr
def test_show_greeks():
    yfinance_view.show_greeks(symbol="AAPL", expiry="2023-07-21", div_cont=0)


@pytest.mark.default_cassette("test_display_chains")
@pytest.mark.vcr
def test_display_chains():
    yfinance_view.display_chains(
        symbol="AAPL", expiry="2023-07-21", min_sp=-1, max_sp=-1
    )
