# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import barchart_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_get_options_info(recorder):
    result_df = barchart_model.get_options_info(ticker="PM")

    recorder.capture(result_df)
