# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.oss import runa_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
        ],
    }


@pytest.mark.vcr
def test_get_startups(recorder):
    df = runa_model.get_startups()
    recorder.capture(df)
