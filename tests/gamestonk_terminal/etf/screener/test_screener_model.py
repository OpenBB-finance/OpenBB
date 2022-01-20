# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf.screener import screener_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "preset",
    [
        "etf_config",
    ],
)
def test_etf_screener(recorder, preset):
    result = screener_model.etf_screener(preset)

    recorder.capture(result)
