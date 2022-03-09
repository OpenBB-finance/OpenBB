# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.behavioural_analysis import cramer_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "inverse",
    [True, False],
)
def test_get_orders(inverse):
    cramer_view.display_cramer_daily(inverse=inverse)


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize("raw", [True, False])
def test_cramer_ticker(raw):
    cramer_view.display_cramer_ticker("AAPL", raw=raw)
