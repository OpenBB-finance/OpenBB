""" Financial Modeling Prep Model"""
__docformat__ = "numpy"
import logging

import pandas as pd
from requests.exceptions import HTTPError

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


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

    temp = []
    try:
        for i in range(pages):
            temp.append(
                pd.read_json(
                    "https://financialmodelingprep.com/api/v3/rss_feed?&page="
                    f"{i}"
                    "&apikey="
                    f"{cfg.API_KEY_FINANCIALMODELINGPREP}"
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
