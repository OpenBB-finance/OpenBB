# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import yahoo_finance_view


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
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "display_shareholders",
        "display_dividends",
        "display_splits",
        "display_mktcap",
    ],
)
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_call_func(func):
    getattr(yahoo_finance_view, func)(symbol="PM")


@pytest.mark.vcr
def test_display_info():
    yahoo_finance_view.display_info(symbol="TSLA")


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_dividends", "get_dividends"),
        ("display_splits", "get_splits"),
        ("display_earnings", "get_earnings_history"),
    ],
)
def test_call_func_empty_df(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(),
    )
    if func == "display_earnings":
        getattr(yahoo_finance_view, func)(symbol="PM", limit=1)
    else:
        getattr(yahoo_finance_view, func)(symbol="PM")


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_shareholders", "get_shareholders"),
    ],
)
def test_display_shareholders(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(
            data=[
                ["Insider", 100, "2021-01-01", 0.1, 1000],
                ["Insider", 120, "2021-01-01", 0.12, 1200],
                ["Insider", 140, "2021-01-01", 0.14, 1400],
            ],
        ),
    )
    getattr(yahoo_finance_view, func)(symbol="PM")


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_dividends", "get_dividends"),
    ],
)
def test_display_dividends(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(
            data=[
                ["2021-01-01", 0.1, 1000],
                ["2021-01-01", 0.12, 1200],
                ["2021-01-01", 0.14, 1400],
            ],
            columns=["Date", "Dividends", "Stock Splits"],
        ),
    )
    getattr(yahoo_finance_view, func)(symbol="MSFT", limit=1)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_splits", "get_splits"),
    ],
)
def test_display_splits(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(
            data=[
                [1, 2],
                [2, 3],
                [3, 4],
            ],
            index=pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-01"]),
        ),
    )
    getattr(yahoo_finance_view, func)(symbol="TSLA")


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_mktcap", "get_mktcap"),
    ],
)
def test_display_mktcap(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=(
            pd.Series(
                data=[7.709558e11, 7.765971e11, 7.986450e11],
                index=pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"]),
            ),
            "USD",
        ),
    )

    getattr(yahoo_finance_view, func)(
        symbol="TSLA", start_date="2021-01-01", end_date="2021-01-07"
    )


@pytest.mark.skip
@pytest.mark.record_verify_screen
def test_display_fundamentals_balance_sheet(mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + "get_financials",
        return_value=pd.DataFrame(
            data=[
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    29,
                    30,
                ],
                [
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    27,
                    28,
                    29,
                    30,
                    31,
                ],
                [
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                ],
            ],
            index=pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-01"]),
            columns=[
                "Cash and cash equivalents",
                "Other short-term investments",
                "Total cash",
                "Net receivables",
                "Inventory",
                "Other current assets",
                "Total current assets",
                "Gross property plant and equipment",
                "Accumulated depreciation",
                "Net property plant and equipment",
                # "Goodwill",
                # "Intangible assets",
                "Other long-term assets",
                "Total non-current assets",
                "Total assets",
                "Current debt",
                "Accounts payable",
                # "Accrued liabilities",
                "Deferred revenues",
                "Other current liabilities",
                "Total current liabilities",
                "Long-term debt",
                "Deferred tax liabilities",
                "Deferred revenues",
                "Other long-term liabilities",
                "Total non-current liabilities",
                "Total liabilities",
                "Common stock",
                "Retained earnings",
                "Accumulated other comprehensive income",
                "Total stockholders' equity",
                "Total liabilities and stockholders' equity",
            ],
        ).T,
    )
    yahoo_finance_view.display_fundamentals(
        symbol="TSLA", statement="balance-sheet", ratios=True
    )


@pytest.mark.record_verify_screen
def test_display_fundamentals_cash_flow(mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + "get_financials",
        return_value=pd.DataFrame(
            data=[
                [
                    2,
                    29,
                ],
                [
                    2,
                    6,
                ],
                [
                    4,
                    11,
                ],
            ],
            index=pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-01"]),
            columns=[
                "Inventory",
                "Accounts payable",
            ],
        ).T,
    )
    yahoo_finance_view.display_fundamentals(
        symbol="TSLA", statement="cash-flow", plot=["Inventory"]
    )


@pytest.mark.skip
@pytest.mark.record_verify_screen
def test_display_fundamentals_financials(mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + "get_financials",
        return_value=pd.DataFrame(
            data=[
                [
                    24,
                    22,
                    23,
                    34,
                    23,
                    5,
                ],
                [
                    23,
                    22,
                    23,
                    34,
                    12,
                    5,
                ],
                [
                    14,
                    22,
                    23,
                    23,
                    15,
                    3,
                ],
            ],
            index=pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-01"]),
            columns=[
                "Total Revenue",
                "Cost Of Revenue",
                "Gross Profit",
                "Interest Expense",
                "Income before tax",
                "Income tax expense",
            ],
        ).T,
    )
    yahoo_finance_view.display_fundamentals(symbol="TSLA", statement="financials")


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_earnings", "get_earnings_history"),
    ],
)
def test_display_earnings(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(
            data=[
                ["2021-01-01", 0.1, 1000],
                ["2021-01-01", 0.12, 1200],
                ["2021-01-01", 0.14, 1400],
            ],
        ),
    )
    getattr(yahoo_finance_view, func)(symbol="TSLA", limit=1)
