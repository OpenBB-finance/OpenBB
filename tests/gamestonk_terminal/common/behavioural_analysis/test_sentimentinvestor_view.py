from datetime import datetime
import pytest

from gamestonk_terminal.common.behavioural_analysis import sentimentinvestor_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical(mocker):
    mocker.patch.object(
        target=sentimentinvestor_view.gtff, attribute="USE_ION", new=True
    )
    mocker.patch(
        target="gamestonk_terminal.common.behavioural_analysis.sentimentinvestor_view.plt.ion"
    )
    mocker.patch(
        target="gamestonk_terminal.common.behavioural_analysis.sentimentinvestor_view.plt.show"
    )
    sentimentinvestor_view.display_historical(
        ticker="AAPL", start="2021-12-12", end="2021-12-15", export="", raw=True
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_trending():
    sentimentinvestor_view.display_trending(
        start=datetime(2021, 12, 21),
        hour=9,
        number=10,
        limit=10,
        export="",
    )
