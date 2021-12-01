# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import business_insider_view
from gamestonk_terminal.stocks.stocks_helper import load


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("period1", "1605481200"),
            ("period2", "1637103600"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_raw():
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
@pytest.mark.parametrize("start", ["14/07/2020", None])
@pytest.mark.parametrize("interval", ["1440min", "60"])
def test_price_target_from_analysts_plt(capsys, interval, mocker, start):
    mock_show = mocker.Mock()
    mocker.patch(target="matplotlib.pyplot.show", new=mock_show)

    other_args = ["TSLA"]
    ticker = "TSLA"
    stock = pd.DataFrame()
    _ticker, _start, _interval, stock = load(
        other_args=other_args,
        s_ticker=ticker,
        s_start=start,
        s_interval=interval,
        df_stock=stock,
    )
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

    mock_show.assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_estimates():
    business_insider_view.estimates(ticker="TSLA", export=None)
