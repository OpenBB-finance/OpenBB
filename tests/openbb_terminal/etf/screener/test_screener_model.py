# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf.screener import screener_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "preset_path",
    ["etf_config.ini"],
)
def test_etf_screener(recorder, preset_path):
    result = screener_model.etf_screener(preset_path)

    recorder.capture(result)
