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
@pytest.mark.parametrize("start", [datetime.strptime("05/12/2021", "%d/%m/%Y")])
@pytest.mark.parametrize("interval", [1440])
def test_price_target_from_analysts_plt(capsys, interval, mocker, start, monkeypatch):
    mock_show = mocker.Mock()
    mocker.patch(target="matplotlib.pyplot.show", new=mock_show)
    monkeypatch.setattr(business_insider_view.gtff, "USE_ION", False)

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

    mock_show.assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_estimates():
    business_insider_view.estimates(ticker="TSLA", export=None)
