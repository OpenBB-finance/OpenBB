""" Finviz View """
__docformat__ = "numpy"

import difflib
import logging
import os
from typing import List, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener.finviz_model import get_screener_data
from openbb_terminal.terminal_helper import suppress_stdout

logger = logging.getLogger(__name__)

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
        "1W",
        "1M",
        "3M",
        "6M",
        "1Y",
        "YTD",
        "1W Volatility",
        "1M Volatility",
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


@log_start_end(log=logger)
def screener(
    loaded_preset: str = "top_gainers",
    data_type: str = "overview",
    limit: int = -1,
    ascend: bool = False,
    sortby: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
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
    sortby: str
        Column to sort table by
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    List[str]
        List of stocks that meet preset criteria
    """
    with suppress_stdout():
        df_screen = get_screener_data(
            preset_loaded=loaded_preset,
            data_type=data_type,
            limit=limit,
            ascend=ascend,
        )

    if isinstance(df_screen, pd.DataFrame):
        if df_screen.empty:
            return []

        df_screen = df_screen.dropna(axis="columns", how="all")

        if sortby:
            if sortby in d_cols_to_sort[data_type]:
                df_screen = df_screen.sort_values(
                    by=[sortby],
                    ascending=ascend,
                    na_position="last",
                )
            else:
                similar_cmd = difflib.get_close_matches(
                    sortby,
                    d_cols_to_sort[data_type],
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    console.print(
                        f"Replacing '{' '.join(sortby)}' by '{similar_cmd[0]}' so table can be sorted."
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
        df_original = df_screen.copy()
        df_screen = df_screen.fillna("")

        cols: List[str] = []
        data_type_cols = {
            "ownership": ["Market Cap", "Outstanding", "Float", "Avg Volume", "Volume"],
            "overview": ["Market Cap", "Volume"],
            "technical": ["Volume"],
            "valuation": ["Market Cap", "Volume"],
            "financial": ["Market Cap", "Volume"],
            "performance": ["Avg Volume", "Volume"],
        }
        cols = data_type_cols.get(data_type, [])

        if cols:
            df_screen[cols] = df_screen[cols].applymap(
                lambda x: lambda_long_number_format(x, 1)
            )

        if not get_current_user().preferences.USE_INTERACTIVE_DF:
            df_original = df_screen

        print_rich_table(
            df_original,
            headers=list(df_original.columns),
            show_index=False,
            title="Finviz Screener",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            data_type,
            df_original,
            sheet_name,
        )

        return df_screen.Ticker.tolist()

    console.print(
        "Error: The preset selected did not return results."
        "This might be a temporary error that is resolved by running the command again."
        "If no results continue to be returned, check the preset and expand the parameters."
    )
    return []
