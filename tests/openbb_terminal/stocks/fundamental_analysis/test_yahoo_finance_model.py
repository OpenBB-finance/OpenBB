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
    result = getattr(yahoo_finance_model, func)(symbol="AAPL")

    recorder.capture(result)


@pytest.mark.vcr
def test_get_shareholders(recorder):
    df = yahoo_finance_model.get_shareholders(symbol="AAPL", holder="major")
    result_list = [df]

    recorder.capture_list(result_list)


@pytest.mark.vcr
def test_get_mktcap(recorder):
    df_mktcap, currency = yahoo_finance_model.get_mktcap(
        symbol="AAPL",
    )
    result_list = [df_mktcap, currency]

    recorder.capture_list(result_list)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, statement",
    [("ABBV", "cash-flow"), ("ABBV", "financials"), ("ABBV", "balance-sheet")],
)
def test_get_financials(ticker, statement, recorder):
    df = yahoo_finance_model.get_financials(symbol=ticker, statement=statement)

    recorder.capture(df)
