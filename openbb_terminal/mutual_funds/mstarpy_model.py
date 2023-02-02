import logging

import mstarpy
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_carbon_metrics(loaded_funds: mstarpy.Funds) -> pd.DataFrame:
    """Search mstarpy for carbon metrics

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    Returns
    -------
        pd.DataFrame of carbon metrics
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
        pd.DataFrame of exclusion policy
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
        pd.DataFrame of funds holdings
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
    """
    field = ["SecId", "TenforeId", "LegalName"]
    try:
        return pd.DataFrame(
            mstarpy.search_funds(term, field, country=country, pageSize=pageSize)
        )
    except RuntimeError as e:
        logger.exception(str(e))
        return pd.DataFrame()
