import logging

import mstarpy
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


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
    country: str = "",
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
    pageSize=10,
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
    pageSize : int
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
            mstarpy.search_funds(term, field, country=country, pageSize=pageSize)
        )
    except RuntimeError as e:
        logger.exception(str(e))
        return pd.DataFrame()
