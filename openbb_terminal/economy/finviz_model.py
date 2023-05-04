""" Finviz Model """
__docformat__ = "numpy"

import logging
import webbrowser
from ast import literal_eval
from typing import List

import pandas as pd
from finvizfinance.group import performance, spectrum, valuation

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

# pylint: disable=unsupported-assignment-operation

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation

GROUPS = {
    "sector": "Sector",
    "industry": "Industry",
    "basic_materials": "Industry (Basic Materials)",
    "communication_services": "Industry (Communication Services)",
    "consumer_cyclical": "Industry (Consumer Cyclical)",
    "consumer_defensive": "Industry (Consumer Defensive)",
    "energy": "Industry (Energy)",
    "financial": "Industry (Financial)",
    "healthcare": "Industry (Healthcare)",
    "industrials": "Industry (Industrials)",
    "real_Estate": "Industry (Real Estate)",
    "technology": "Industry (Technology)",
    "utilities": "Industry (Utilities)",
    "country": "Country (U.S. listed stocks only)",
    "capitalization": "Capitalization",
}


@log_start_end(log=logger)
def get_performance_map(period: str = "1d", map_filter: str = "sp500"):
    """Opens Finviz map website in a browser. [Source: Finviz]

    Parameters
    ----------
    period : str
        Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y.
    scope : str
        Map filter. Available map filters are sp500, world, full, etf.
    """
    # Conversion from period and type, to fit url requirements
    d_period = {"1d": "", "1w": "w1", "1m": "w4", "3m": "w13", "6m": "w26", "1y": "w52"}
    d_type = {"sp500": "sec", "world": "geo", "full": "sec_all", "etf": "etf"}
    url = f"https://finviz.com/map.ashx?t={d_type[map_filter]}&st={d_period[period]}"
    webbrowser.open(url)


@log_start_end(log=logger)
def get_groups() -> List[str]:
    """Get group available"""
    return list(GROUPS.keys())


@log_start_end(log=logger)
def get_valuation_data(
    group: str = "sector", sortby: str = "Name", ascend: bool = True
) -> pd.DataFrame:
    """Get group (sectors, industry or country) valuation data. [Source: Finviz]

    Parameters
    ----------
    group : str
        Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

    Returns
    -------
    pd.DataFrame
        dataframe with valuation/performance data
    """

    if group not in GROUPS:
        console.print(
            f"[red]Group {group} not found. Check available groups through get_groups().[/red]\n"
        )
        return pd.DataFrame()

    try:
        group = GROUPS[group]
        df_group = valuation.Valuation().screener_view(group=group)
        df_group.columns = [col.replace(" ", "").strip() for col in df_group.columns]
        df_group = df_group.sort_values(by=sortby, ascending=ascend)
        df_group.fillna("", inplace=True)

        # Passing Raw data to Pandas DataFrame if using interactive mode
        if get_current_user().preferences.USE_INTERACTIVE_DF:
            return df_group
        print(df_group.head())
        df_group["MarketCap"] = df_group["MarketCap"].apply(
            lambda x: float(x.strip("B"))
            if x.endswith("B")
            else float(x.strip("M")) / 1000
        )
        df_group["Volume"] = df_group["Volume"] / 1_000_000
        df_group = df_group.rename(columns={"Volume": "Volume [1M]"})
        return df_group

    except IndexError:
        console.print("Data not found.\n")
        return pd.DataFrame()


@log_start_end(log=logger)
def get_performance_data(
    group: str = "sector", sortby: str = "Name", ascend: bool = True
) -> pd.DataFrame:
    """Get group (sectors, industry or country) performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
        Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

    Returns
    -------
    pd.DataFrame
        dataframe with performance data
    """

    if group not in GROUPS:
        console.print(
            f"[red]Group {group} not found. Check available groups through get_groups().[/red]\n"
        )
        return pd.DataFrame()

    try:
        group = GROUPS[group]
        df_group = performance.Performance().screener_view(group=group)
        df_group = df_group.rename(
            columns={
                "Perf Week": "Week",
                "Perf Month": "Month",
                "Perf Quart": "3Month",
                "Perf Half": "6Month",
                "Perf Year": "1Year",
                "Perf YTD": "YTD",
                "Avg Volume": "AvgVolume",
                "Rel Volume": "RelVolume",
            }
        )
        df_group.columns = [col.strip() for col in df_group.columns]
        df_group["Week"] = df_group["Week"].apply(lambda x: float(x.strip("%")) / 100)
        df_group = df_group.sort_values(by=sortby, ascending=ascend)
        df_group.fillna("", inplace=True)

        # Passing Raw data to Pandas DataFrame if using interactive mode
        if get_current_user().preferences.USE_INTERACTIVE_DF:
            return df_group

        df_group["Volume"] = df_group["Volume"] / 1_000_000
        df_group["AvgVolume"] = df_group["AvgVolume"] / 1_000_000
        df_group = df_group.rename(
            columns={"Volume": "Volume [1M]", "AvgVolume": "AvgVolume [1M]"}
        )
        return df_group

    except IndexError:
        console.print("Data not found.\n")
        return pd.DataFrame()


@log_start_end(log=logger)
def get_spectrum_data(group: str = "sector"):
    """Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
        Group by category. Available groups can be accessed through get_groups().
    """
    if group not in GROUPS:
        console.print(
            f"[red]Group {group} not found. Check available groups through get_groups().[/red]\n"
        )
        return

    group = GROUPS[group]
    spectrum.Spectrum().screener_view(group=group)


@log_start_end(log=logger)
def get_futures(
    future_type: str = "Indices", sortby: str = "ticker", ascend: bool = False
) -> pd.DataFrame:
    """Get futures data. [Source: Finviz]

    Parameters
    ----------
    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

    Returns
    -------
    pd.Dataframe
        Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    """
    source = request(
        "https://finviz.com/futures.ashx", headers={"User-Agent": get_user_agent()}
    ).text

    slice_source = source[
        source.find("var groups = ") : source.find(  # noqa: E203
            "\r\n\r\n                    groups.forEach(function(group) "
        )
    ]
    groups = literal_eval(
        slice_source[
            : slice_source.find("\r\n                    var tiles = ") - 1
        ].strip("var groups = ")
    )
    titles = literal_eval(
        slice_source[
            slice_source.find("\r\n                    var tiles = ") : -1  # noqa: E203
        ].strip("\r\n                    var tiles = ")
    )

    d_futures: dict = {}
    for future in groups:
        d_futures[future["label"]] = []
        for ticker in future["contracts"]:
            d_futures[future["label"]].append(titles[ticker["ticker"]])

    df = pd.DataFrame(d_futures[future_type])
    df = df.set_index("label")
    df = df.sort_values(by=sortby, ascending=ascend)

    df = df[["prevClose", "last", "change"]].fillna("")

    return df
