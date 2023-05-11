""" Financial Modeling Prep Model"""
__docformat__ = "numpy"
import logging
import warnings
from datetime import datetime
from typing import Any, Dict, Optional

import fundamentalanalysis as fa  # Financial Modeling Prep
import pandas as pd
import valinvest
from requests.exceptions import HTTPError

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format, request
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

logger = logging.getLogger(__name__)

# pylint: disable=protected-access


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_score(symbol: str, years: int) -> Dict[str, Any]:
    """Gets value score from fmp

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    years : int
        The amount of years to use to calculate the score

    Returns
    -------
    np.number
        Value score
    """

    current_user = get_current_user()

    scores = {}

    try:
        valstock = valinvest.Fundamental(
            symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
        )
        warnings.filterwarnings("ignore", category=FutureWarning)
        scores = {
            "Beta Score": 100 * (valstock.beta_score() / 9),
            "CROIC Score": 100
            * (valstock._score(valstock.croic_growth, years=years) / 9),
            "Debt Cost Score": 100
            * (valstock._score(valstock.debt_cost_growth, years=years) / 9),
            "EBITDA Cover Score": 100
            * (valstock._score(valstock.ebitda_cover_growth, years=years) / 9),
            "EBITDA Score": 100
            * (valstock._score(valstock.ebitda_growth, years=years) / 9),
            "EPS Score": 100 * (valstock._score(valstock.eps_growth, years=years) / 9),
            "Equity Buyback Score": 100
            * (valstock._score(valstock.eq_buyback_growth, years=years) / 9),
            "Revenue Score": 100
            * (valstock._score(valstock.revenue_growth, years=years) / 9),
            "ROIC Score": 100
            * (valstock._score(valstock.roic_growth, years=years) / 9),
        }

        # This resembles the same methodology as valstock.fscore
        scores["Total Score"] = sum(scores.values())
        warnings.filterwarnings("ignore", category=FutureWarning)
    except KeyError:
        console.print("[red]Invalid API Key[/red]\n")
    # Invalid ticker (Ticker should be a NASDAQ 100 ticker or SP 500 ticker)
    except ValueError as e:
        console.print(e, "\n")
    return scores


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_profile(symbol: str) -> pd.DataFrame:
    """Get ticker profile from FMP

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of ticker profile
    """

    current_user = get_current_user()

    df = pd.DataFrame()

    try:
        df = fa.profile(symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError:
        console.print("[red]Invalid API Key[/red]\n")
    # Premium feature, API plan is not authorized
    except HTTPError:
        console.print("[red]API Key not authorized for Premium feature[/red]\n")
    return df


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_enterprise(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    quarterly: bool = False,
) -> pd.DataFrame:
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    start_date : str
        Start date of data
    end_date : str
        End date of data
    quarterly: bool
        Flag to get quarterly data

    Returns
    -------
    pd.DataFrame
        Dataframe of enterprise information
    """
    if start_date is None:
        # Set data far in the past to ensure all data is returned
        start_date_year = 1900
    elif isinstance(start_date, str):
        start_date_year = datetime.strptime(start_date, "%Y-%m-%d").year
    else:
        start_date_year = start_date.year

    if end_date is None:
        end_date_year = datetime.now().year
    elif isinstance(end_date, str):
        end_date_year = datetime.strptime(end_date, "%Y-%m-%d").year
    else:
        end_date_year = end_date.year  # type: ignore

    # There is a margin of 3 added to ensure that the start date is included
    limit = datetime.now().year - start_date_year + 3

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.enterprise(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.enterprise(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

            start_date_position = (
                df_fa.columns.get_loc(str(start_date_year))
                if str(start_date_year) in df_fa.columns
                else 0
            )
            end_date_position = (
                df_fa.columns.get_loc(str(end_date_year))
                if str(end_date_year) in df_fa.columns
                else 0
            )

            # Select the right portion of the data
            if start_date_position:
                df_fa = df_fa.iloc[:, end_date_position : start_date_position + 1]
            elif end_date_position:
                df_fa = df_fa.iloc[:, end_date_position:]

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    if not df_fa.empty:
        df_fa = clean_metrics_df(df_fa, num=limit, mask=False)

    # Transpose the dataframe to make it easier to read
    df_fa = df_fa.T
    df_fa = df_fa.sort_index(ascending=True)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_dcf(symbol: str, limit: int = 5, quarterly: bool = False) -> pd.DataFrame:
    """Get stocks dcf from FMP

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of dcf data
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.discounted_cash_flow(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.discounted_cash_flow(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )
        df_fa = clean_metrics_df(df_fa, num=limit, mask=False)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_income(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get income statements

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of the income statements
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.income_statement(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.income_statement(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)
    df_fa.index = df_fa_c.index

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_balance(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get balance sheets

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of balance sheet
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.balance_sheet_statement(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.balance_sheet_statement(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)
    df_fa.index = df_fa_c.index

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_cash(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get cash flow

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of company cash flow
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.cash_flow_statement(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.cash_flow_statement(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)
    df_fa.index = df_fa_c.index

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_key_metrics(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get key metrics

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of key metrics
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.key_metrics(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.key_metrics(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=limit)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_key_ratios(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get key ratios

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of key ratios
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.financial_ratios(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.financial_ratios(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=limit)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_financial_growth(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get financial statement growth

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of financial statement growth
    """

    current_user = get_current_user()

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.financial_statement_growth(
                symbol,
                current_user.credentials.API_KEY_FINANCIALMODELINGPREP,
                period="quarter",
            )
        else:
            df_fa = fa.financial_statement_growth(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=limit)

        df_fa = df_fa[df_fa.columns[::-1]]
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def clean_metrics_df(data: pd.DataFrame, num: int, mask: bool = False) -> pd.DataFrame:
    """Clean metrics data frame

    Parameters
    ----------
    data : pd.DataFrame
        Metrics data frame
    num : int
        Number of columns to clean
    mask : bool, optional
        Apply mask, by default True

    Returns
    -------
    pd.DataFrame
        Cleaned metrics data frame
    """
    # iloc will fail if number is greater than number of columns
    num = min(num, data.shape[1])
    data = data.iloc[:, 0:num]

    if mask:
        data = data.mask(data.astype(object).eq(num * ["None"])).dropna()
        data = data.mask(data.astype(object).eq(num * ["0"])).dropna()

    date_rows = {
        "calendarYear": "%Y",
        "fillingDate": "%Y-%m-%d",
        "acceptedDate": "%Y-%m-%d %H:%M:%S",
    }
    for row, dt_type in date_rows.items():
        if row in data.index:
            data.loc[row] = pd.to_datetime(data.loc[row], format=dt_type)
    # we dont want to format this going to pywry window
    if not get_current_user().preferences.USE_INTERACTIVE_DF:
        data = data.applymap(lambda x: lambda_long_number_format(x))
    clean_df_index(data)
    data.columns.name = "Fiscal Date Ending"
    data = data.rename(
        index={
            "Enterprise value over e b i t d a": "Enterprise value over EBITDA",
            "Net debt to e b i t d a": "Net debt to EBITDA",
            "D c f": "DCF",
            "Net income per e b t": "Net income per EBT",
        }
    )

    return data


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_rating(symbol: str) -> pd.DataFrame:
    """Get ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Rating data
    """
    current_user = get_current_user()
    if current_user.credentials.API_KEY_FINANCIALMODELINGPREP:
        try:
            df = fa.rating(
                symbol, current_user.credentials.API_KEY_FINANCIALMODELINGPREP
            )
            l_recoms = [col for col in df.columns if "Recommendation" in col]
            l_recoms_show = [
                recom.replace("rating", "")
                .replace("Details", "")
                .replace("Recommendation", "")
                for recom in l_recoms
            ]
            l_recoms_show[0] = "Rating"
            df = df[l_recoms]
            df.columns = l_recoms_show
        except ValueError as e:
            console.print(f"[red]{e}[/red]\n")
            logger.exception(str(e))
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    return df


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_price_targets(symbol: str) -> pd.DataFrame:
    """Get price targets for a company [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Symbol to get data for

    Returns
    -------
    pd.DataFrame
        DataFrame of price targets
    """
    current_user = get_current_user()

    url = (
        "https://financialmodelingprep.com/api/v4/price-target?"
        f"symbol={symbol}&apikey={current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"
    )
    response = request(url)

    # Check if response is valid
    if response.status_code != 200 or "Error Message" in response.json():
        message = f"Error, Status Code: {response.status_code}."
        message = (
            message
            if "Error Message" not in response.json()
            else message + "\n" + response.json()["Error Message"] + ".\n"
        )
        console.print(message)
        return pd.DataFrame()

    return pd.DataFrame(response.json())


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_filings(
    pages: int = 1,
) -> pd.DataFrame:
    """Get SEC Filings RSS feed, disseminated by FMP
    Parameters
    ----------
    pages: range = 1
        The range of most-rececnt pages to get entries from (1000 per page; maximum of 30 pages)
    Returns
    -------
    df: pd.DataFrame
        Dataframe of results
    Examples
    --------
    df = openbb.stocks.filings()
    df = openbb.stocks.filings(pages=30)
    """
    current_user = get_current_user()
    temp = []
    try:
        for i in range(pages):
            temp.append(
                pd.read_json(
                    "https://financialmodelingprep.com/api/v3/rss_feed?&page="
                    f"{i}"
                    "&apikey="
                    f"{current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"
                )
            )
        df = pd.concat(temp)
        df = df.rename(
            columns={
                "title": "Title",
                "date": "Date",
                "link": "URL",
                "cik": "CIK",
                "form_type": "Form Type",
                "ticker": "Ticker",
            },
        )
        df_columns = ["Date", "Ticker", "CIK", "Form Type", "Title", "URL"]
        df = (
            pd.DataFrame(df, columns=df_columns)
            .set_index(keys=["Date"])
            .copy()
            .sort_index(ascending=False)
        )

        # Invalid API Keys
    except ValueError as e:
        console.print(e)
        df = pd.DataFrame()
        # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        df = pd.DataFrame()

    return df
