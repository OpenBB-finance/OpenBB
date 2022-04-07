# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf.discovery import wsj_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "sort_type",
    [
        "gainers",
        "decliners",
        "active",
        "wrong",
    ],
)
def test_get_etfs_by_name(recorder, sort_type):
    result = wsj_model.etf_movers(sort_type)

    recorder.capture(result)
