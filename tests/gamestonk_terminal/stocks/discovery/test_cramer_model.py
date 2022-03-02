# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import cramer_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "inverse",
    [True, False],
)
def test_get_orders(recorder, inverse):
    recommendations = cramer_model.get_cramer_daily(inverse=inverse)
    recorder.capture(recommendations)
