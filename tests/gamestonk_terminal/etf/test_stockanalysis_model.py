# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import stockanalysis_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
def test_get_all_names_symbols(recorder):
    result = stockanalysis_model.get_all_names_symbols()

    recorder.capture_list(result)
