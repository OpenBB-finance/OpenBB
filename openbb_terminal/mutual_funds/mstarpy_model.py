import logging

import mstarpy
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def get_historical(
    loaded_funds: mstarpy.Funds,
    start_date: str,
    end_date: str,
    comparison: str = "",
) -> pd.DataFrame:
    """Get historical fund, category, index price

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds
    start_date: str
        start date of the historical data
    end_date: str
        end date of the historical data
    comparison: str
        can be index, category, both

    Returns
    -------
    pd.DataFrame
        Dataframe containing historical data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.historical(f, "2020-01-01", "2020-12-31")
    """
    try:
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
        if not comparison:
            data = loaded_funds.nav(start_date_dt, end_date_dt, frequency="daily")
            df = pd.DataFrame(data).set_index("date")
            df.index = pd.to_datetime(df.index)
        else:
            comparison_list = {
                "index": [
                    "fund",
                    "index",
                ],
                "category": ["fund", "category"],
                "both": ["fund", "index", "category"],
            }
            data = loaded_funds.historicalData()
            df_dict = {}
            for x in comparison_list[comparison]:
                df_dict[x] = pd.DataFrame(data["graphData"][x]).set_index("date")

            df = pd.concat(
                list(df_dict.values())[:], axis=1, keys=list(df_dict.keys())[:]
            )
            df.index = pd.to_datetime(df.index)
            df = df.loc[(df.index >= start_date_dt) & (df.index <= end_date_dt)]
            df = (df.pct_change().fillna(0) + 1).cumprod() * 100
            df.columns = [col[0] for col in df.columns]
    except Exception as e:
        console.print(f"Error: {e}")
        return pd.DataFrame()
    return df


@log_start_end(log=logger)
def get_sector(loaded_funds: mstarpy.Funds, asset_type: str = "equity"):
    """Get fund, category, index sector breakdown

    Parameters
    ----------
    loaded_funds: mstarpy.funds
        class mstarpy.Funds instantiated with selected funds
    asset_type: str
        can be equity or fixed income

    Returns
    -------
    pd.DataFrame
        Dataframe containing sector breakdown
    """
    key = "EQUITY" if asset_type == "equity" else "FIXEDINCOME"

    d = loaded_funds.sector()[key]

    if d:
        return pd.DataFrame(d)
    return pd.DataFrame()


@log_start_end(log=logger)
def load_carbon_metrics(loaded_funds: mstarpy.Funds) -> pd.DataFrame:
    """Search mstarpy for carbon metrics

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    Returns
    -------
    pd.DataFrame
        Dataframe containing carbon metrics

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.carbon(f)
    """
    carbonMetrics = loaded_funds.carbonMetrics()
    return pd.Series(carbonMetrics, name="carbonMetrics").reset_index()


@log_start_end(log=logger)
def load_exclusion_policy(loaded_funds: mstarpy.Funds) -> pd.DataFrame:
    """Search mstarpy exclusion policy in esgData

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    Returns
    -------
    pd.DataFrame
        Dataframe containing exclusion policy

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.exclusion(f)
    """
    esgData = loaded_funds.esgData()
    if "sustainabilityIntentionality" in esgData:
        return pd.Series(
            esgData["sustainabilityIntentionality"], name="exclusionPolicy"
        ).reset_index()
    return pd.DataFrame()


@log_start_end(log=logger)
def load_funds(
    term: str = "",
    country: str = "US",
) -> mstarpy.Funds:
    """Search mstarpy for matching funds

    Parameters
    ----------
    term : str
         String that will be searched for.  Can be name or isin
    country : str
        country where the funds is hosted

    Returns
    -------
    mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    """
    return mstarpy.Funds(term, country)


@log_start_end(log=logger)
def load_holdings(
    loaded_funds: mstarpy.Funds, holding_type: str = "all"
) -> pd.DataFrame:
    """Search mstarpy for holdings

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    holding_type : str
         type of holdings, can be all, equity, bond, other

    Returns
    -------
    pd.DataFrame
        Dataframe containing holdings

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.holdings(f)
    """
    holdings = loaded_funds.holdings(holding_type)
    if holdings.empty:
        return pd.DataFrame()
    return holdings[["isin", "securityName", "weighting", "country"]]


@log_start_end(log=logger)
def search_funds(
    term: str = "",
    country: str = "",
    limit=10,
) -> pd.DataFrame:
    """Search mstarpy for matching funds

    Parameters
    ----------
    term : str
         String that will be searched for.  Can be name or isin
    field : list
        list of field who will be displayed
    country : str
        country where the funds is hosted
    limit : int
        length of results to display

    Returns
    -------
    pd.DataFrame
        Dataframe containing matches

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.funds.search("Vanguard", "US")
    """
    field = ["SecId", "TenforeId", "LegalName"]
    try:
        return pd.DataFrame(
            mstarpy.search_funds(term, field, country=country, pageSize=limit)
        )
    except RuntimeError as e:
        logger.exception(str(e))
        return pd.DataFrame()
