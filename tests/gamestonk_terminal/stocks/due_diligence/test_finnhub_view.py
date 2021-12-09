# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finnhub_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ]
    }


@pytest.mark.default_cassette("test_rating_over_time_TSLA")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_rating_over_time():
    finnhub_view.rating_over_time(
        ticker="TSLA",
        num=10,
        raw=True,
        export=None,
    )


@pytest.mark.default_cassette("test_rating_over_time_TSLA")
@pytest.mark.vcr(mode="none")
def test_rating_over_time_plt(capsys, mocker):
    mock_show = mocker.Mock()
    mocker.patch(target="matplotlib.pyplot.show", new=mock_show)
    finnhub_view.rating_over_time(
        ticker="TSLA",
        num=10,
        raw=False,
        export=None,
    )

    capsys.readouterr()

    mock_show.assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_rating_over_time_invalid_ticker():
    finnhub_view.rating_over_time(
        ticker="INVALID_TICKER",
        num=10,
        raw=False,
        export=None,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_rating_over_time_invalid_token():
    finnhub_view.rating_over_time(
        ticker="TSLA",
        num=10,
        raw=False,
        export=None,
    )
