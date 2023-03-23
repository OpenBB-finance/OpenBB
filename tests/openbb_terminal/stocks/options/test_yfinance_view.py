# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
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


@pytest.mark.default_cassette("test_plot_plot")
@pytest.mark.vcr
def test_plot_plot(mocker):
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
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.export_data")

    yfinance_view.plot_payoff(
        current_price=95.0, options=[], underlying=0, symbol="AAPL", expiry="2023-07-21"
    )


@pytest.mark.default_cassette("test_show_greeks")
@pytest.mark.vcr
def test_show_greeks():
    yfinance_view.show_greeks(symbol="AAPL", expiry="2023-07-21", div_cont=0)
