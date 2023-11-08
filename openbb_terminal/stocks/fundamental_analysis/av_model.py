"""Alpha Vantage Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, List

import numpy as np
import pandas as pd
from alpha_vantage.fundamentaldata import FundamentalData

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format, request
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import yahoo_finance_model
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index
from openbb_terminal.stocks.stocks_helper import clean_fraction

logger = logging.getLogger(__name__)


def check_premium_key(json_response: Dict) -> bool:
    """Checks if the response is the premium endpoint"""
    if json_response == {
        "Information": "Thank you for using Alpha Vantage! This is a premium endpoint. You may subscribe to "
        "any of the premium plans at https://www.alphavantage.co/premium/ to instantly unlock all premium endpoints"
    }:
        console.print(
            "This is a premium endpoint for AlphaVantage. Please use a premium key.\n"
        )
        return True
    return False


@log_start_end(log=logger)
def get_overview(symbol: str) -> pd.DataFrame:
    """Get alpha vantage company overview

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of fundamentals
    """
    # Request OVERVIEW data from Alpha Vantage API
    s_req = (
        f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey"
        f"={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )
    result = request(s_req, stream=True)
    result_json = result.json()

    df_fa = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in result_json:
        console.print(result_json["Error Message"])
    # check if json is empty
    elif not result_json:
        console.print("No data found from Alpha Vantage\n")
    # Parse json data to dataframe
    elif "Note" in result_json:
        console.print(result_json["Note"], "\n")
    else:
        df_fa = pd.json_normalize(result_json)

        # Keep json data sorting in dataframe
        df_fa = df_fa[list(result_json.keys())].T
        df_fa.iloc[5:] = df_fa.iloc[5:].applymap(lambda x: lambda_long_number_format(x))
        df_fa.columns = [" "]

    return df_fa


@log_start_end(log=logger)
def get_key_metrics(symbol: str) -> pd.DataFrame:
    """Get key metrics from overview

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of key metrics
    """
    # Request OVERVIEW data
    s_req = (
        f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}"
        f"&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )
    result = request(s_req, stream=True)
    result_json = result.json()

    # If the returned data was unsuccessful
    if "Error Message" in result_json:
        console.print(result_json["Error Message"])
    else:
        # check if json is empty
        if not result_json or len(result_json) < 2:
            console.print("No data found from Alpha Vantage\n")
            return pd.DataFrame()

        df_fa = pd.json_normalize(result_json)
        df_fa = df_fa[list(result_json.keys())].T

        if not get_current_user().preferences.USE_INTERACTIVE_DF:
            df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
        clean_df_index(df_fa)
        df_fa = df_fa.rename(
            index={
                "E b i t d a": "EBITDA",
                "P e ratio": "PE ratio",
                "P e g ratio": "PEG ratio",
                "E p s": "EPS",
                "Return on equity t t m": "Return on equity TTM",
                "Price to sales ratio t t m": "Price to sales ratio TTM",
            }
        )
        as_key_metrics = [
            "Market capitalization",
            "EBITDA",
            "EPS",
            "PE ratio",
            "PEG ratio",
            "Price to book ratio",
            "Return on equity TTM",
            "Price to sales ratio TTM",
            "Dividend yield",
            "50 day moving average",
            "Analyst target price",
            "Beta",
        ]
        return df_fa.loc[as_key_metrics]

    return pd.DataFrame()


@log_start_end(log=logger)
def get_income_statements(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get income statements for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        DataFrame of income statements
    """
    url = (
        f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}"
        f"&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url)
    response_json = r.json()
    if check_premium_key(response_json):
        return pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in response_json:
        console.print(response_json["Error Message"])
    # check if json is empty
    elif not response_json:
        console.print("No data found from Alpha Vantage, looking in Yahoo Finance\n")
        if (
            yahoo_finance_model.get_financials(symbol, statement="financials")
            is not None
        ):
            return yahoo_finance_model.get_financials(symbol, statement="financials")
    else:
        statements = response_json
        df_fa = pd.DataFrame()

        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        elif "annualReports" in statements:
            df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            console.print("No data found from Alpha Vantage\n")
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa[::-1].T

        df_fa = df_fa.replace("None", "0")
        df_fa.iloc[1:] = df_fa.iloc[1:].astype("float")

        df_fa_c = df_fa.iloc[:, -limit:].applymap(
            lambda x: lambda_long_number_format(x)
        )

        if ratios:
            df_fa_pc = df_fa.iloc[1:].pct_change(axis="columns").fillna(0)
            j = 0
            for i in list(range(1, 25)):
                df_fa.iloc[i] = df_fa_pc.iloc[j]
                j += 1

        df_fa = df_fa.iloc[:, 0:limit]

        return df_fa_c if not plot else df_fa
    return pd.DataFrame()


@log_start_end(log=logger)
def get_balance_sheet(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get balance sheets for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        DataFrame of the balance sheet
    """
    current_user = get_current_user()
    url = (
        f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&"
        f"apikey={current_user.credentials.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url)
    response_json = r.json()
    if check_premium_key(response_json):
        return pd.DataFrame()
    # If the returned data was unsuccessful
    if "Error Message" in response_json:
        console.print(response_json["Error Message"])

    # check if json is empty
    if not response_json:
        console.print("No data found from Alpha Vantage, looking in Yahoo Finance\n")
        if (
            yahoo_finance_model.get_financials(symbol, statement="balance-sheet")
            is not None
        ):
            return yahoo_finance_model.get_financials(symbol, statement="balance-sheet")
    else:
        statements = response_json
        df_fa = pd.DataFrame()

        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        elif "annualReports" in statements:
            df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            console.print("No data found from Alpha Vantage\n")
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa[::-1].T

        df_fa = df_fa.replace("None", "0")
        df_fa.iloc[1:] = df_fa.iloc[1:].astype("float")

        df_fa_c = df_fa.iloc[:, -limit:].applymap(
            lambda x: lambda_long_number_format(x)
        )

        if ratios:
            df_fa_pc = df_fa.iloc[1:].pct_change(axis="columns").fillna(0)
            j = 0
            for i in list(range(1, 37)):
                df_fa.iloc[i] = df_fa_pc.iloc[j]
                j += 1

            df_fa_c = df_fa.iloc[:, 0:limit].applymap(
                lambda x: lambda_long_number_format(x)
            )

        df_fa = df_fa.iloc[:, 0:limit]

        return df_fa_c if not plot else df_fa
    return pd.DataFrame()


@log_start_end(log=logger)
def get_cash_flow(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get cash flows for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of cash flow statements
    """
    url = (
        f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}"
        f"&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )
    r = request(url)
    response_json = r.json()
    if check_premium_key(response_json):
        return pd.DataFrame()
    # If the returned data was unsuccessful
    if "Error Message" in response_json:
        console.print(response_json["Error Message"])
    elif not response_json:
        console.print("No data found from Alpha Vantage, looking in Yahoo Finance\n")

        if (
            yahoo_finance_model.get_financials(symbol, statement="cash-flow")
            is not None
        ):
            return yahoo_finance_model.get_financials(symbol, statement="cash-flow")
    else:
        statements = response_json
        df_fa = pd.DataFrame()

        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        elif "annualReports" in statements:
            df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            console.print("No data found from Alpha Vantage\n")
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa[::-1].T

        df_fa = df_fa.replace("None", "0")
        df_fa.iloc[1:] = df_fa.iloc[1:].astype("float")

        df_fa_c = df_fa.iloc[:, -limit:].applymap(
            lambda x: lambda_long_number_format(x)
        )

        if ratios:
            df_fa_pc = df_fa.iloc[1:].pct_change(axis="columns").fillna(0)
            j = 0
            for i in list(range(1, 37)):
                df_fa.iloc[i] = df_fa_pc.iloc[j]
                j += 1

            df_fa_c = df_fa.iloc[:, 0:limit].applymap(
                lambda x: lambda_long_number_format(x)
            )

        df_fa = df_fa.iloc[:, 0:limit]

        return df_fa_c if not plot else df_fa
    return pd.DataFrame()


@log_start_end(log=logger)
def get_earnings(symbol: str, quarterly: bool = False) -> pd.DataFrame:
    """Get earnings calendar for ticker

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    quarterly : bool, optional
        Flag to get quarterly and not annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of earnings
    """
    # Request EARNINGS data from Alpha Vantage API
    s_req = (
        "https://www.alphavantage.co/query?function=EARNINGS&"
        f"symbol={symbol}&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )
    result = request(s_req, stream=True)
    result_json = result.json()
    df_fa = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in result_json:
        console.print(result_json["Error Message"])
    # check if json is empty
    elif not result_json or len(result_json) < 2:
        console.print("No data found from Alpha Vantage\n")
    else:
        df_fa = pd.json_normalize(result_json)

        if quarterly:
            df_fa = pd.DataFrame(df_fa["quarterlyEarnings"][0])
            df_fa = df_fa[
                [
                    "fiscalDateEnding",
                    "reportedDate",
                    "reportedEPS",
                    "estimatedEPS",
                    "surprise",
                    "surprisePercentage",
                ]
            ]
            df_fa = df_fa.rename(
                columns={
                    "fiscalDateEnding": "Fiscal Date Ending",
                    "reportedEPS": "Reported EPS",
                    "estimatedEPS": "Estimated EPS",
                    "reportedDate": "Reported Date",
                    "surprise": "Surprise",
                    "surprisePercentage": "Surprise Percentage",
                }
            )
        else:
            df_fa = pd.DataFrame(df_fa["annualEarnings"][0])
            df_fa = df_fa.rename(
                columns={
                    "fiscalDateEnding": "Fiscal Date Ending",
                    "reportedEPS": "Reported EPS",
                }
            )

    return df_fa


def df_values(
    df: pd.DataFrame, item: str, index: int = 0, length: int = 2
) -> List[int]:
    """Clean the values from the df

    Parameters
    ----------
    df : pd.DataFrame
        The Dataframe to use
    item : str
        The item to select
    index : int
        The number of row to display
    length : int
        The number of rows to return

    Returns
    -------
    values : List[int]
        The values for the dataframe
    """
    if index:
        df = df.iloc[index : index + length]
    selection = df[item]
    values = selection.apply(lambda x: 0 if (not x or x == "None") else int(x)).values
    return values.tolist()


def replace_df(name: str, row: pd.Series) -> pd.Series:
    """Replaces text in pandas row based on color functions

    Return
    ----------
    name : str
        The name of the row
    row : pd.Series
        The original row

    Parameters
    ----------
    new_row : pd.Series
        The new formatted row
    """
    for i, item in enumerate(row):
        if name == "Mscore":
            row[i] = color_mscore(item)
        elif name in ["Zscore", "McKee"]:
            row[i] = color_zscore_mckee(item)
        else:
            row[i] = str(round(float(item), 2)) if item != "nan" else "N/A"
    return row


def color_mscore(value: str) -> str:
    """Adds color to mscore dataframe values

    Parameters
    ----------
    value : str
        The string value

    Returns
    -------
    new_value : str
        The string formatted with rich color
    """
    if value == "nan":
        return "N/A"
    value_float = float(value)
    if value_float <= -2.22:
        return f"[green]{value_float:.2f}[/green]"
    if value_float <= -1.78:
        return f"[yellow]{value_float:.2f}[/yellow]"
    return f"[red]{value_float:.2f}[/red]"


def color_zscore_mckee(value: str) -> str:
    """Adds color to mckee or zscore dataframe values
    Parameters
    ----------
    value : str
        The string value

    Returns
    -------
    new_value : str
        The string formatted with rich color
    """
    if value == "nan":
        return "N/A"
    value_float = float(value)
    if value_float < 0.5:
        return f"[red]{value_float:.2f}[/red]"
    return f"[green]{value_float:.2f}[/green]"


@log_start_end(log=logger)
def get_fraud_ratios(symbol: str, detail: bool = False) -> pd.DataFrame:
    """Get fraud ratios based on fundamentals

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    detail : bool
        Whether to provide extra m-score details

    Returns
    -------
    metrics : pd.DataFrame
        The fraud ratios
    """

    try:
        fd = FundamentalData(
            key=get_current_user().credentials.API_KEY_ALPHAVANTAGE,
            output_format="pandas",
        )
        # pylint: disable=unbalanced-tuple-unpacking
        df_cf, _ = fd.get_cash_flow_annual(symbol=symbol)
        df_bs, _ = fd.get_balance_sheet_annual(symbol=symbol)
        df_is, _ = fd.get_income_statement_annual(symbol=symbol)

    except ValueError as e:
        if "premium endpoint" in str(e):
            console.print(
                "This is a premium endpoint for AlphaVantage. Please use a premium key.\n"
            )
        return pd.DataFrame()

    # pylint: disable=no-member
    df_cf = df_cf.set_index("fiscalDateEnding")
    df_bs = df_bs.set_index("fiscalDateEnding")
    df_is = df_is.set_index("fiscalDateEnding")
    fraud_years = pd.DataFrame()
    for i in range(len(df_cf) - 1):
        ar = df_values(df_bs, "currentNetReceivables", i)
        sales = df_values(df_is, "totalRevenue", i)
        cogs = df_values(df_is, "costofGoodsAndServicesSold", i)
        ni = df_values(df_is, "netIncome", i)
        ca = df_values(df_bs, "totalCurrentAssets", i)
        cl = df_values(df_bs, "totalCurrentLiabilities", i)
        ppe = df_values(df_bs, "propertyPlantEquipment", i)
        cash = df_values(df_bs, "cashAndCashEquivalentsAtCarryingValue", i)
        cash_and_sec = df_values(df_bs, "cashAndShortTermInvestments", i)
        sec = [y - x for (x, y) in zip(cash, cash_and_sec)]
        ta = df_values(df_bs, "totalAssets", i)
        dep = df_values(df_bs, "accumulatedDepreciationAmortizationPPE", i)
        sga = df_values(df_is, "sellingGeneralAndAdministrative", i)
        tl = df_values(df_bs, "totalLiabilities", i)
        icfo = df_values(df_is, "netIncomeFromContinuingOperations", i)
        cfo = df_values(df_cf, "operatingCashflow", i)

        ratios: Dict = {}
        try:
            ratios["DSRI"] = (ar[0] / sales[0]) / (ar[1] / sales[1])
            ratios["GMI"] = ((sales[1] - cogs[1]) / sales[1]) / (
                (sales[0] - cogs[0]) / sales[0]
            )
            ratios["AQI"] = (1 - ((ca[0] + ppe[0] + sec[0]) / ta[0])) / (
                1 - ((ca[1] + ppe[1] + sec[1]) / ta[1])
            )
            ratios["SGI"] = sales[0] / sales[1]
            ratios["DEPI"] = (dep[1] / (ppe[1] + dep[1])) / (dep[0] / (ppe[0] + dep[0]))
            ratios["SGAI"] = (sga[0] / sales[0]) / (sga[1] / sales[1])
            ratios["LVGI"] = (tl[0] / ta[0]) / (tl[1] / ta[1])
            ratios["TATA"] = (icfo[0] - cfo[0]) / ta[0]
            ratios["Mscore"] = (
                -4.84
                + (0.92 * ratios["DSRI"])
                + (0.58 * ratios["GMI"])
                + (0.404 * ratios["AQI"])
                + (0.892 * ratios["SGI"])
                + (0.115 * ratios["DEPI"] - (0.172 * ratios["SGAI"]))
                + (4.679 * ratios["TATA"])
                - (0.327 * ratios["LVGI"])
            )

            zscore = (
                -4.336
                - (4.513 * (ni[0] / ta[0]))
                + (5.679 * (tl[0] / ta[0]))
                + (0.004 * (ca[0] / cl[0]))
            )
            v1 = np.log(ta[0] / 1000)
            v2 = ni[0] / ta[0]
            v3 = cash[0] / cl[0]

            x = ((v1 + 0.85) * v2) - 0.85
            y = 1 + v3

            mckee = x**2 / (x**2 + y**2)
            ratios["Zscore"] = zscore
            ratios["McKee"] = mckee
        except ZeroDivisionError:
            for item in [
                "DSRI",
                "GMI",
                "AQI",
                "SGI",
                "DEPI",
                "SGAI",
                "LVGI",
                "TATA",
                "Mscore",
                "Zscore",
                "Mckee",
            ]:
                ratios[item] = np.nan
        if fraud_years.empty:
            fraud_years.index = ratios.keys()
        fraud_years[df_cf.index[i]] = ratios.values()
    fraud_years = fraud_years[sorted(fraud_years)]
    if not detail:
        details = ["DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA"]
        fraud_years = fraud_years.drop(details)

    return fraud_years


@log_start_end(log=logger)
def get_dupont(symbol: str) -> pd.DataFrame:
    """Get dupont ratios

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    dupont : pd.DataFrame
        The dupont ratio breakdown
    """

    try:
        fd = FundamentalData(
            key=get_current_user().credentials.API_KEY_ALPHAVANTAGE,
            output_format="pandas",
        )
        # pylint: disable=unbalanced-tuple-unpacking
        df_bs, _ = fd.get_balance_sheet_annual(symbol=symbol)
        df_is, _ = fd.get_income_statement_annual(symbol=symbol)

    except ValueError as e:
        if "premium endpoint" in str(e):
            console.print(
                "This is a premium endpoint for AlphaVantage. Please use a premium key.\n"
            )
        return pd.DataFrame()

    # pylint: disable=no-member
    df_bs = df_bs.set_index("fiscalDateEnding")
    df_is = df_is.set_index("fiscalDateEnding")
    dupont_years = pd.DataFrame()

    if len(df_bs) != len(df_is):
        console.print(
            "The fiscal dates in the balance sheet do not correspond to the fiscal dates in the income statement."
        )
        return pd.DataFrame()

    for i in range(len(df_bs)):
        ni = df_values(df_is, "netIncome", i, 1)
        pretax = df_values(df_is, "incomeBeforeTax", i, 1)
        ebit = df_values(df_is, "ebit", i, 1)
        sales = df_values(df_is, "totalRevenue", i, 1)
        assets = df_values(df_bs, "totalAssets", i, 1)
        equity = df_values(df_bs, "totalShareholderEquity", i, 1)

        ratios: Dict = {}
        try:
            ratios["Tax Burden"] = clean_fraction(ni[0], pretax[0])
            ratios["Interest Burden"] = clean_fraction(pretax[0], ebit[0])
            ratios["EBIT Margin"] = clean_fraction(ebit[0], sales[0])
            ratios["Asset Turnover"] = clean_fraction(sales[0], assets[0])
            ratios["Finance Leverage"] = clean_fraction(assets[0], equity[0])
            ratios["ROI"] = clean_fraction(ni[0], equity[0])
        except IndexError:
            pass

        if dupont_years.empty:
            dupont_years.index = ratios.keys()
        dupont_years[df_bs.index[i]] = ratios.values()
    dupont_years = dupont_years[sorted(dupont_years)]
    return dupont_years
