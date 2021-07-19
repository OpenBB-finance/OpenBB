""" FINRA View """
__docformat__ = "numpy"

import argparse
from typing import List, Tuple, Dict
import requests
from scipy import stats
import pandas as pd
from matplotlib import pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_positive,
)


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


def getFINRAdata(weekStartDate, tier, ticker, is_ats, offset):
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
        "offset": offset,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }

    return requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        headers=req_hdr,
        json=req_data,
    )


def getATSdata(num_tickers_to_filter: int) -> Tuple[pd.DataFrame, Dict]:
    """Get all FINRA ATS data, and parse most promising tickers based on linear regression

    Parameters
    ----------
    num_tickers_to_filter : int
        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity

    Returns
    ----------
    pd.DataFrame
        Dark Pools (ATS) Data
    Dict
        Tickers from Dark Pools with better regression slope
    """
    tiers = ["T1", "T2", "OTCE"]
    df_ats = pd.DataFrame()

    for tier in tiers:
        print(f"Processing Tier {tier} ...")
        for d_week in getFINRAweeks(tier, is_ats=True):
            offset = 0
            response = getFINRAdata(d_week["weekStartDate"], tier, "", True, offset)
            l_data = response.json()

            while len(response.json()) == 5000:
                offset += 5000
                response = getFINRAdata(d_week["weekStartDate"], tier, "", True, offset)
                l_data += response.json()

            df_ats_week = pd.DataFrame(l_data)
            df_ats_week["weekStartDate"] = d_week["weekStartDate"]

            if not df_ats_week.empty:
                df_ats = df_ats.append(df_ats_week, ignore_index=True)

    df_ats = df_ats.sort_values("weekStartDate")
    df_ats["weekStartDateInt"] = pd.to_datetime(df_ats["weekStartDate"]).apply(
        lambda x: x.timestamp()
    )

    print(f"Processing regression on {num_tickers_to_filter} promising tickers ...")

    d_ats_reg = {}
    # set(df_ats['issueSymbolIdentifier'].values) this would be iterating through all tickers
    # but that is extremely time consuming for little reward. A little filtering is done to
    # speed up search for best ATS tickers
    for symbol in list(
        df_ats.groupby("issueSymbolIdentifier")["totalWeeklyShareQuantity"]
        .sum()
        .sort_values()[-num_tickers_to_filter:]
        .index
    ):
        slope = stats.linregress(
            df_ats[df_ats["issueSymbolIdentifier"] == symbol][
                "weekStartDateInt"
            ].values,
            df_ats[df_ats["issueSymbolIdentifier"] == symbol][
                "totalWeeklyShareQuantity"
            ].values,
        )[0]
        d_ats_reg[symbol] = slope

    return df_ats, d_ats_reg


def plot_dark_pools(ats: pd.DataFrame, top_ats_tickers: List):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    top_ats_tickers : List
        List of tickers from most promising with better linear regression slope
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    for symbol in top_ats_tickers:
        plt.plot(
            pd.to_datetime(
                ats[ats["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            ats[ats["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"]
            / 1_000_000,
        )

    plt.legend(top_ats_tickers)
    plt.ylabel("Total Weekly Shares [Million]")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.title("Dark Pool (ATS) growing tickers")
    plt.gcf().autofmt_xdate()
    plt.xlabel("Weeks")

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def dark_pool(other_args: List[str]):
    """Display dark pool (ATS) data of tickers with growing trades activity

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="darkpool",
        description="Display dark pool (ATS) data of tickers with growing trades activity",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=1000,
        help="Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity.",
    )
    parser.add_argument(
        "-t",
        "--top",
        action="store",
        dest="n_top",
        type=check_positive,
        default=5,
        help="List of tickers from most promising with better linear regression slope.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_ats, d_ats_reg = getATSdata(ns_parser.n_num)

        top_ats_tickers = list(
            dict(
                sorted(d_ats_reg.items(), key=lambda item: item[1], reverse=True)
            ).keys()
        )[: ns_parser.n_top]

        plot_dark_pools(df_ats, top_ats_tickers)
        print("")

    except Exception as e:
        print(e, "\n")
