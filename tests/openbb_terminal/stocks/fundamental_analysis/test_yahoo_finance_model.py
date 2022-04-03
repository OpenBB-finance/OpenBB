# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import yahoo_finance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func",
    [
        # "get_info",  CHECK HOW TO MOCK TIMEZONE
        "get_sustainability",
        "get_calendar_earnings",
        "get_website",
        "get_hq",
        "get_dividends",
        "get_splits",
    ],
)
def test_call_func(func, recorder):
    result = getattr(yahoo_finance_model, func)(ticker="AAPL")

    recorder.capture(result)


@pytest.mark.vcr
def test_get_shareholders(recorder):
    major_df, institutional_df, mutual_df = yahoo_finance_model.get_shareholders(
        ticker="AAPL"
    )
    result_list = [major_df, institutional_df, mutual_df]

    recorder.capture_list(result_list)


@pytest.mark.vcr
def test_get_mktcap(recorder):
    df_mktcap, currency = yahoo_finance_model.get_mktcap(
        ticker="AAPL",
    )
    result_list = [df_mktcap, currency]

    recorder.capture_list(result_list)
