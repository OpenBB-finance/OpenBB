""" Nasdaq Model """
__docformat__ = "numpy"

import logging
from typing import Optional

import pandas as pd
from requests.exceptions import ReadTimeout

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    request,
)
from openbb_terminal.rich_config import console

# pylint: disable=too-many-branches


logger = logging.getLogger(__name__)

FORM_GROUP = {
    "annual": "Annual%20Reports",
    "quarterly": "Quarterly%20Reports",
    "proxies": "Proxies%20and%20Info%20Statements",
    "insiders": "Insider%20Transactions",
    "8-K": "8-K%20Related",
    "registrations": "Registration%20Statements",
    "comments": "Comment%20Letters",
}


@log_start_end(log=logger)
def get_sec_filings(
    symbol: str,
    limit: int = 20,
    year: Optional[int] = None,
    form_group: Optional[str] = None,
) -> pd.DataFrame:
    """Get SEC filings for a given stock ticker. [Source: Nasdaq]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        The number of filings to return
    year: Optional[int]
        The year to grab from. The year will be ignored if form_group is not specified
    form_group: Optional[str]
        The form type to filter for:
        Choose from: annual, quarterly, proxies, insiders, 8-K, registrations, comments

    Returns
    -------
    df_financials : pd.DataFrame
        SEC filings data
    """
    base_url = f"https://api.nasdaq.com/api/company/{symbol}/sec-filings"
    arguments = f"?limit={limit}&sortColumn=filed&sortOrder=desc&IsQuoteMedia=true"
    valid_form_group = False
    if form_group in FORM_GROUP:
        arguments = f"{arguments}&formGroup={FORM_GROUP[form_group]}"
        valid_form_group = True
    if year and valid_form_group:
        arguments = f"{arguments}&Year={year}"
    elif year:
        console.print("Year will be ignored if form_group is not specified")
    try:
        response = request(base_url + arguments)
    except ReadTimeout:
        return pd.DataFrame()
    try:
        data = response.json()["data"]["rows"]
    except KeyError:
        return pd.DataFrame()
    final_df = pd.DataFrame(data)
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
