""" FINRA View """
__docformat__ = "numpy"

import argparse
from typing import List, Tuple
import requests
import pandas as pd
from matplotlib import pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale


def getFINRAweeks(tier, is_ats) -> List:
    """Get FINRA weeks

    Parameters
    ----------
    tier : str
        Stock tier between T1, T2, or OTCE
    is_ats : bool
        ATS data if true, NON-ATS otherwise

    Returns
    ----------
    List
        List of response data
    """
    req_hdr = {"Accept": "application/json", "Content-Type": "application/json"}

    req_data = {
        "compareFilters": [
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
            },
            {
                "compareType": "EQUAL",
                "fieldName": "tierIdentifier",
                "fieldValue": tier,
            },
        ],
        "delimiter": "|",
        "fields": ["weekStartDate"],
        "limit": 27,
        "quoteValues": False,
        "sortFields": ["-weekStartDate"],
    }

    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails",
        headers=req_hdr,
        json=req_data,
    )

    return response.json() if response.status_code == 200 else list()


def getFINRAdata(
    weekStartDate: str, tier: str, ticker: str, is_ats: bool
) -> Tuple[int, List]:
    """Get FINRA data

    Parameters
    ----------
    weekStartDate : str
        Weekly data to get FINRA data
    tier : str
        Stock tier between T1, T2, or OTCE
    ticker : str
        Stock ticker to get data from
    is_ats : bool
        ATS data if true, NON-ATS otherwise

    Returns
    ----------
    str
        Status code from request
    List
        List of response data
    """
    req_hdr = {"Accept": "application/json", "Content-Type": "application/json"}

    l_cmp_filters = [
        {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": weekStartDate,
        },
        {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
        {
            "compareType": "EQUAL",
            "description": "",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
        },
    ]

    if ticker:
        l_cmp_filters.append(
            {
                "compareType": "EQUAL",
                "fieldName": "issueSymbolIdentifier",
                "fieldValue": ticker,
            }
        )

    req_data = {
        "compareFilters": l_cmp_filters,
        "delimiter": "|",
        "fields": [
            "issueSymbolIdentifier",
            "totalWeeklyShareQuantity",
            "totalWeeklyTradeCount",
            "lastUpdateDate",
        ],
        "limit": 5000,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }

    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        headers=req_hdr,
        json=req_data,
    )

    return (
        response.status_code,
        response.json() if response.status_code == 200 else list(),
    )


def getTickerFINRAdata(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get all FINRA data associated with a ticker

    Parameters
    ----------
    ticker : str
        Stock ticker to get data from

    Returns
    ----------
    pd.DataFrame
        Dark Pools (ATS) Data
    pd.DataFrame
        OTC (Non-ATS) Data
    """
    tiers = ["T1", "T2", "OTCE"]

    l_data = list()
    for tier in tiers:
        for d_week in getFINRAweeks(tier, is_ats=True):
            status_code, response = getFINRAdata(
                d_week["weekStartDate"], tier, ticker, True
            )
            if status_code == 200:
                if response:
                    d_data = response[0]
                    d_data.update(d_week)
                    l_data.append(d_data)
                else:
                    break

    df_ats = pd.DataFrame(l_data)
    if not df_ats.empty:
        df_ats = df_ats.sort_values("weekStartDate")
        df_ats = df_ats.set_index("weekStartDate")

    l_data = list()
    for tier in tiers:
        for d_week in getFINRAweeks(tier, is_ats=False):
            status_code, response = getFINRAdata(
                d_week["weekStartDate"], tier, ticker, False
            )
            if status_code == 200:
                if response:
                    d_data = response[0]
                    d_data.update(d_week)
                    l_data.append(d_data)
                else:
                    break

    df_otc = pd.DataFrame(l_data)
    if not df_otc.empty:
        df_otc = df_otc.sort_values("weekStartDate")
        df_otc = df_otc.set_index("weekStartDate")

    return df_ats, df_otc


def plot_dark_pools(ticker: str, ats: pd.DataFrame, otc: pd.DataFrame):
    """Plots ATS and NON-ATS data

    Parameters
    ----------
    ticker : str
        Stock ticker to get data from
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    otc : pd.DataFrame
        OTC (Non-ATS) Data
    """
    _, _ = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    plt.subplot(3, 1, (1, 2))
    if not ats.empty and not otc.empty:
        plt.bar(
            ats.index,
            (ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"])
            / 1_000_000,
            color="tab:orange",
        )
        plt.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color="tab:blue"
        )
        plt.legend(["ATS", "OTC"])

    elif not ats.empty:
        plt.bar(
            ats.index,
            ats["totalWeeklyShareQuantity"] / 1_000_000,
            color="tab:orange",
        )
        plt.legend(["ATS"])

    elif not otc.empty:
        plt.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color="tab:blue"
        )
        plt.legend(["OTC"])

    plt.ylabel("Total Weekly Shares [Million]")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.title(f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}")

    plt.subplot(313)
    if not ats.empty:
        plt.plot(
            ats.index,
            ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
            color="tab:orange",
        )
        plt.legend(["ATS"])

        if not otc.empty:
            plt.plot(
                otc.index,
                otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                color="tab:blue",
            )
            plt.legend(["ATS", "OTC"])

    else:
        plt.plot(
            otc.index,
            otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
            color="tab:blue",
        )
        plt.legend(["OTC"])

    plt.ylabel("Shares per Trade")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Weeks")

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def dark_pool(other_args: List[str], ticker: str):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="dp",
        description="Display barchart of dark pool (ATS) and OTC (Non ATS) data [Source: FINRA]",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_ats, df_otc = getTickerFINRAdata(ticker)

        if df_ats.empty and df_otc.empty:
            print("No ticker data found!")

        plot_dark_pools(ticker, df_ats, df_otc)
        print("")

    except Exception as e:
        print(e, "\n")
