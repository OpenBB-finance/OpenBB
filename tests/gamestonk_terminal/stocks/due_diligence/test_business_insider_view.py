# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import business_insider_view
from gamestonk_terminal.stocks.stocks_helper import load


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_raw(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    business_insider_view.price_target_from_analysts(
        ticker="TSLA",
        start=None,
        interval=None,
        stock=None,
        num=None,
        raw=True,
        export=None,
    )


@pytest.mark.default_cassette("test_price_target_from_analysts_TSLA")
@pytest.mark.vcr
@pytest.mark.parametrize("start", [datetime.strptime("2021-12-05", "%Y-%m-%d")])
@pytest.mark.parametrize("interval", [1440])
def test_price_target_from_analysts_plt(capsys, interval, mocker, start):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    ticker = "TSLA"
    stock = load(ticker=ticker, start=start, interval=interval)

    business_insider_view.price_target_from_analysts(
        ticker=ticker,
        start=start,
        interval=interval,
        stock=stock,
        num=None,
        raw=False,
        export=None,
    )
    capsys.readouterr()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_estimates():
    business_insider_view.estimates(ticker="TSLA", export=None)
