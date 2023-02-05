""" Seeking Alpha Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_estimates_eps(ticker: str) -> pd.DataFrame:
    """Takes the ticker, asks for seekingalphaID and gets eps estimates

    Parameters
    ----------
    ticker: str
        ticker of company
    Returns
    -------
    pd.DataFrame
        eps estimates for the next 10yrs
    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.fa.epsfc("AAPL")
    """

    url = "https://seekingalpha.com/api/v3/symbol_data/estimates"

    querystring = {
        "estimates_data_items": "eps_normalized_actual,eps_normalized_consensus_low,eps_normalized_consensus_mean,"
        "eps_normalized_consensus_high,eps_normalized_num_of_estimates",
        "period_type": "annual",
        "relative_periods": "-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11",
    }

    # add ticker_ids for the ticker
    seek_id = get_seekingalpha_id(ticker)
    querystring["ticker_ids"] = seek_id

    payload = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }

    # semi random user agent -- disabled and static user agent because it might be the reason for 403
    # headers["User-Agent"] = get_user_agent()

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    # init
    output = pd.DataFrame(
        columns=[
            "fiscalyear",
            "consensus_mean",
            "change %",
            "analysts",
            "actual",
            "consensus_low",
            "consensus_high",
        ]
    )

    # if no estimations exist, response is empty "reviews" and "reviews"
    # {"revisions":{},"estimates":{}}
    try:
        seek_object = response.json()["estimates"][str(seek_id)]

        items = len(seek_object["eps_normalized_num_of_estimates"].keys())

        for i in range(0, items - 3):
            # python_dict
            eps_estimates = {}
            eps_estimates["fiscalyear"] = seek_object[
                "eps_normalized_num_of_estimates"
            ][str(i)][0]["period"]["fiscalyear"]
            eps_estimates["analysts"] = seek_object["eps_normalized_num_of_estimates"][
                str(i)
            ][0]["dataitemvalue"]
            try:
                eps_estimates["actual"] = seek_object["eps_normalized_actual"][str(i)][
                    0
                ]["dataitemvalue"]
            except Exception:
                eps_estimates["actual"] = 0
            eps_estimates["consensus_low"] = seek_object[
                "eps_normalized_consensus_low"
            ][str(i)][0]["dataitemvalue"]
            eps_estimates["consensus_high"] = seek_object[
                "eps_normalized_consensus_high"
            ][str(i)][0]["dataitemvalue"]
            eps_estimates["consensus_mean"] = seek_object[
                "eps_normalized_consensus_mean"
            ][str(i)][0]["dataitemvalue"]

            try:
                this = float(eps_estimates["consensus_mean"])
                try:
                    prev = float(
                        seek_object["eps_normalized_actual"][str(i - 1)][0][
                            "dataitemvalue"
                        ]
                    )
                except Exception:
                    prev = float(
                        seek_object["eps_normalized_consensus_mean"][str(i - 1)][0][
                            "dataitemvalue"
                        ]
                    )

                percent = ((this / prev) - 1) * 100
            except Exception:
                percent = 0

            eps_estimates["change %"] = percent

            # format correction (before return, so calculation still works)
            eps_estimates["consensus_mean"] = lambda_long_number_format(
                float(eps_estimates["consensus_mean"])
            )
            eps_estimates["consensus_low"] = lambda_long_number_format(
                float(eps_estimates["consensus_low"])
            )
            eps_estimates["consensus_high"] = lambda_long_number_format(
                float(eps_estimates["consensus_high"])
            )
            eps_estimates["actual"] = lambda_long_number_format(
                float(eps_estimates["actual"])
            )

            # df append replacement
            new_row = pd.DataFrame(eps_estimates, index=[0])
            output = pd.concat([output, new_row])
    except Exception:
        return pd.DataFrame()

    return output


@log_start_end(log=logger)
def get_estimates_rev(ticker: str) -> pd.DataFrame:
    """Takes the ticker, asks for seekingalphaID and gets rev estimates

    Parameters
    ----------
    ticker: str
        ticker of company
    Returns
    -------
    pd.DataFrame
        rev estimates for the next 10yrs
    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.fa.revfc("AAPL")
    """

    url = "https://seekingalpha.com/api/v3/symbol_data/estimates"

    querystring = {
        "estimates_data_items": "revenue_actual,revenue_consensus_low,revenue_consensus_mean,"
        "revenue_consensus_high,revenue_num_of_estimates",
        "period_type": "annual",
        "relative_periods": "-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11",
    }

    # add ticker_ids for the ticker
    seek_id = get_seekingalpha_id(ticker)
    querystring["ticker_ids"] = seek_id

    payload = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
        "TE": "trailers",
    }

    # semi random user agent -- disabled and static user agent because it might be the reason for 403
    # headers["User-Agent"] = get_user_agent()

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    # init
    # pd.empty should deliver true if no data-rows are added
    output = pd.DataFrame(
        columns=[
            "fiscalyear",
            "consensus_mean",
            "change %",
            "analysts",
            "actual",
            "consensus_low",
            "consensus_high",
        ]
    )

    # if no estimations exist, response is empty "reviews" and "reviews"
    # {"revisions":{},"estimates":{}}
    try:
        seek_object = response.json()["estimates"][seek_id]

        items = len(seek_object["revenue_num_of_estimates"].keys())

        for i in range(0, items - 3):
            # python_dict
            revenue_estimates = {}
            revenue_estimates["fiscalyear"] = seek_object["revenue_num_of_estimates"][
                str(i)
            ][0]["period"]["fiscalyear"]
            revenue_estimates["consensus_mean"] = seek_object["revenue_consensus_mean"][
                str(i)
            ][0]["dataitemvalue"]

            revenue_estimates["analysts"] = seek_object["revenue_num_of_estimates"][
                str(i)
            ][0]["dataitemvalue"]
            if i < 1:
                revenue_estimates["actual"] = seek_object["revenue_actual"][str(i)][0][
                    "dataitemvalue"
                ]
            else:
                revenue_estimates["actual"] = 0
            revenue_estimates["consensus_low"] = seek_object["revenue_consensus_low"][
                str(i)
            ][0]["dataitemvalue"]
            revenue_estimates["consensus_high"] = seek_object["revenue_consensus_high"][
                str(i)
            ][0]["dataitemvalue"]

            try:
                this = float(revenue_estimates["consensus_mean"])
                # if actual revenue is available, take it for the calc
                try:
                    prev = float(
                        seek_object["revenue_actual"][str(i - 1)][0]["dataitemvalue"]
                    )
                except Exception:
                    prev = float(
                        seek_object["revenue_consensus_mean"][str(i - 1)][0][
                            "dataitemvalue"
                        ]
                    )

                percent = ((this / prev) - 1) * 100
            except Exception:
                percent = float(0)

            revenue_estimates["change %"] = percent

            # format correction (before return, so calculation still works)
            revenue_estimates["consensus_mean"] = lambda_long_number_format(
                float(revenue_estimates["consensus_mean"])
            )
            revenue_estimates["consensus_low"] = lambda_long_number_format(
                float(revenue_estimates["consensus_low"])
            )
            revenue_estimates["consensus_high"] = lambda_long_number_format(
                float(revenue_estimates["consensus_high"])
            )
            revenue_estimates["actual"] = lambda_long_number_format(
                float(revenue_estimates["actual"])
            )

            # df append replacement
            new_row = pd.DataFrame(revenue_estimates, index=[0])
            output = pd.concat([output, new_row])
    except Exception:
        return pd.DataFrame()

    return output


@log_start_end(log=logger)
def get_seekingalpha_id(ticker: str) -> str:
    """Takes the ticker, asks for seekingalphaID and returns it

    Parameters
    ----------
    ticker: str
        ticker of company
    Returns
    -------
    str:
        seekingalphaID - to be used for further API calls
    """

    url = "https://seekingalpha.com/api/v3/searches"

    querystring = {
        "filter[type]": "symbols",
        "filter[list]": "all",
        "page[size]": "1",
    }

    querystring["filter[query]"] = ticker
    payload = ""

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://seekingalpha.com/",
        "Connection": "keep-alive",
        # "TE": "trailers",
    }

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    try:
        seekingalphaID = str(response.json()["symbols"][0]["id"])
    except Exception:
        # for some reason no mapping possible
        seekingalphaID = "0"

    return seekingalphaID
