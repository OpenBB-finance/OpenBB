""" Market Watch Model """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

# pylint: disable=too-many-branches


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_sec_filings(symbol: str, limit: int = 20) -> pd.DataFrame:
    """Get SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        The number of filings to return

    Returns
    -------
    df_financials : pd.DataFrame
        SEC filings data
    """
    base_url = f"https://api.nasdaq.com/api/company/{symbol}/sec-filings"
    arguments = f"?limit={limit}&sortColumn=filed&sortOrder=desc&IsQuoteMedia=true"
    response = request(base_url + arguments)
    try:
        data = response.json()["data"]["rows"]
    except KeyError:
        return pd.DataFrame()
    final_df = pd.DataFrame(data)
    pd.set_option("display.max_colwidth", None)
    try:
        final_df["view"] = final_df["view"].apply(lambda x: x["htmlLink"])
    except KeyError:
        return pd.DataFrame()
    final_df = final_df.rename(
        columns={
            "companyName": "Company Name",
            "reportingOwner": "Reporting Owner",
            "formType": "Form Type",
            "filed": "Filed",
            "view": "View",
            "period": "Period",
        }
    )
    final_df = final_df.set_index("Filed")
    return final_df
