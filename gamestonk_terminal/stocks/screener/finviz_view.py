""" Finviz View """
__docformat__ = "numpy"

from typing import List
import os
import difflib
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from gamestonk_terminal.stocks.screener.finviz_model import (
    get_screener_data,
)
from gamestonk_terminal.rich_config import console


d_cols_to_sort = {
    "overview": [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ],
    "valuation": [
        "Ticker",
        "Market Cap",
        "P/E",
        "Fwd P/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPS this Y",
        "EPS next Y",
        "EPS past 5Y",
        "EPS next 5Y",
        "Sales past 5Y",
        "Price",
        "Change",
        "Volume",
    ],
    "financial": [
        "Ticker",
        "Market Cap",
        "Dividend",
        "ROA",
        "ROE",
        "ROI",
        "Curr R",
        "Quick R",
        "LTDebt/Eq",
        "Debt/Eq",
        "Gross M",
        "Oper M",
        "Profit M",
        "Earnings",
        "Price",
        "Change",
        "Volume",
    ],
    "ownership": [
        "Ticker",
        "Market Cap",
        "Outstanding",
        "Float",
        "Insider Own",
        "Insider Trans",
        "Inst Own",
        "Inst Trans",
        "Float Short",
        "Short Ratio",
        "Avg Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "performance": [
        "Ticker",
        "Perf Week",
        "Perf Month",
        "Perf Quart",
        "Perf Half",
        "Perf Year",
        "Perf YTD",
        "Volatility W",
        "Volatility M",
        "Recom",
        "Avg Volume",
        "Rel Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "technical": [
        "Ticker",
        "Beta",
        "ATR",
        "SMA20",
        "SMA50",
        "SMA200",
        "52W High",
        "52W Low",
        "RSI",
        "Price",
        "Change",
        "from Open",
        "Gap",
        "Volume",
    ],
}


def screener(
    loaded_preset: str,
    data_type: str,
    limit: int = 10,
    ascend: bool = False,
    sort: str = "",
    export: str = "",
) -> List[str]:
    """Screener one of the following: overview, valuation, financial, ownership, performance, technical.

    Parameters
    ----------
    loaded_preset: str
        Preset loaded to filter for tickers
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical
    limit : int
        Limit of stocks to display
    ascend : bool
        Order of table to ascend or descend
    sort: str
        Column to sort table by
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    List[str]
        List of stocks that meet preset criteria
    """
    df_screen = get_screener_data(
        loaded_preset,
        data_type,
        0,
        ascend,
    )

    if isinstance(df_screen, pd.DataFrame):
        if df_screen.empty:
            return []

        df_screen = df_screen.dropna(axis="columns", how="all")

        if sort:
            if " ".join(sort) in d_cols_to_sort[data_type]:
                df_screen = df_screen.sort_values(
                    by=[" ".join(sort)],
                    ascending=ascend,
                    na_position="last",
                )
            else:
                similar_cmd = difflib.get_close_matches(
                    " ".join(sort),
                    d_cols_to_sort[data_type],
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    console.print(
                        f"Replacing '{' '.join(sort)}' by '{similar_cmd[0]}' so table can be sorted."
                    )
                    df_screen = df_screen.sort_values(
                        by=[similar_cmd[0]],
                        ascending=ascend,
                        na_position="last",
                    )
                else:
                    console.print(
                        f"Wrong sort column provided! Provide one of these: {', '.join(d_cols_to_sort[data_type])}"
                    )

        df_screen = df_screen.fillna("")

        print_rich_table(
            df_screen.head(n=limit),
            headers=list(df_screen.columns),
            show_index=False,
            title="Finzin Screener",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            data_type,
            df_screen,
        )

        return list(df_screen.head(n=limit)["Ticker"].values)

    console.print("")
    return []
