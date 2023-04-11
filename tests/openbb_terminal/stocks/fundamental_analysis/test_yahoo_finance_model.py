# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame

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


@pytest.mark.record_http
@pytest.mark.parametrize(
    "ticker, statement, ratios",
    [
        ("ABBV", "cash-flow", False),
        ("ABBV", "financials", False),
        ("ABBV", "balance-sheet", True),
    ],
)
def test_get_financials(ticker, statement, ratios, record):
    df = yahoo_finance_model.get_financials(
        symbol=ticker, statement=statement, ratios=ratios
    )

    record.add_verify(df)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.skip(reason="Yahoo Finance API is not working")
@pytest.mark.record_http
def test_get_calendar_earnings():
    df = yahoo_finance_model.get_calendar_earnings(symbol="AAPL")

    assert isinstance(df, DataFrame)
    assert not df.empty
