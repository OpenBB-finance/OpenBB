"""CoinMarketCap view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.discovery import coinmarketcap_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff

sort_map = {
    "Symbol": "Symbol",
    "CMC_Rank": "CMC_Rank",
    "LastPrice": "Last Price",
    "DayPctChange": "1 Day Pct Change",
    "MarketCap": "Market Cap ($B)",
}


def display_cmc_top_coins(top: int, sortby: str, descend: bool, export: str) -> None:
    """Shows top n coins. [Source: CoinMarketCap]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coinmarketcap_model.get_cmc_top_n()

    if df.empty:
        print("No Data Found\n")
        return

    df = df.sort_values(by=sort_map[sortby], ascending=descend)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.iloc[:top, :],
                headers=df.columns,
                showindex=False,
                tablefmt="fancy_grid",
                floatfmt=".2f",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cmctop",
        df,
    )
