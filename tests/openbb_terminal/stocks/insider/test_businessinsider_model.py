# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.insider import businessinsider_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_get_insider_activity(recorder):
    result_df = businessinsider_model.get_insider_activity(ticker="TSLA")

    recorder.capture(result_df)
