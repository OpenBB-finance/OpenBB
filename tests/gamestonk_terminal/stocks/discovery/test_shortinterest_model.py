# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import shortinterest_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
def test_get_low_float(recorder):
    df_low_float = shortinterest_model.get_low_float()
    recorder.capture(df_low_float)


@pytest.mark.vcr()
def test_get_today_hot_penny_stocks(recorder):
    df_penny = shortinterest_model.get_today_hot_penny_stocks()
    recorder.capture(df_penny)
