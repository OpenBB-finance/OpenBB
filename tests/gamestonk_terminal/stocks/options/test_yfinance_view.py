# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import yfinance_view


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
    # MOCK CHARTS
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_oi(
        ticker="PM",
        expiry="2022-01-07",
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
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_vol(
        ticker="PM",
        expiry="2022-01-07",
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
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_volume_open_interest(
        ticker="PM",
        expiry="2022-01-07",
        min_sp=min_sp,
        max_sp=max_sp,
        min_vol=min_vol,
        export="",
    )


@pytest.mark.default_cassette("test_plot_plot")
@pytest.mark.vcr
def test_plot_plot(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_plot(
        ticker="PM",
        expiration="2022-01-07",
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
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_payoff(
        current_price=95.0,
        options=[],
        underlying=0,
        ticker="PM",
        expiration="2022-01-07",
    )


@pytest.mark.skip
@pytest.mark.default_cassette("test_show_parity")
@pytest.mark.vcr
def test_show_parity(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.show_parity(
        ticker="PM",
        exp="2022-01-07",
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
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.risk_neutral_vals(
        ticker="PM",
        exp="2022-01-07",
        put=True,
        df=pd.DataFrame(columns=["Price", "Chance"]),
        mini=None,
        maxi=None,
        risk=None,
    )


@pytest.mark.skip
@pytest.mark.default_cassette("test_show_binom")
@pytest.mark.vcr
def test_show_binom(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=yfinance_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.export_data")

    # MOCK EXPORT_BINOMIAL_CALCS
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.Workbook.save")

    yfinance_view.show_binom(
        ticker="PM",
        expiration="2022-01-07",
        strike=90.0,
        put=True,
        europe=False,
        export=False,
        plot=True,
        vol=None,
    )
