# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import yahoo_finance_model

pytest.skip("skipping broken tests", allow_module_level=True)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.parametrize(
    "func",
    [
        "get_info",
        "get_sustainability",
        "get_calendar_earnings",
        "get_website",
        "get_hq",
        "get_dividends",
    ],
)
def test_call_func(func, recorder):
    result = getattr(yahoo_finance_model, func)(ticker="GME")

    recorder.capture(result)


@pytest.mark.vcr
def test_get_shareholders(recorder):
    major_df, institutional_df, mutual_df = yahoo_finance_model.get_shareholders(
        ticker="GME"
    )
    result_list = [major_df, institutional_df, mutual_df]

    recorder.capture_list(result_list)
