# IMPORTATION STANDARD
from datetime import date

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import seeking_alpha_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_get_next_earnings(recorder):
    df_earnings = seeking_alpha_model.get_next_earnings(1, start_date=date(2023, 3, 22))
    recorder.capture(df_earnings)


@pytest.mark.vcr
def test_get_trending_list(recorder):
    trending_list = seeking_alpha_model.get_trending_list(limit=2)
    recorder.capture(trending_list)


@pytest.mark.vcr
def test_get_news_html():
    seeking_alpha_model.get_news_html()
