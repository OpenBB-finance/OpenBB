# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import coinmarketcap_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("X-CMC_PRO_API_KEY", "MOCK_X_CMC_PRO_API_KEY")],
    }


@pytest.mark.vcr
def test_get_cmc_top_n(recorder):
    result = coinmarketcap_model.get_cmc_top_n()
    recorder.capture(result)
