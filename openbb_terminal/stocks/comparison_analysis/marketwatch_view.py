""" Comparison Analysis Marketwatch View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_financials_colored_values,
    patch_pandas_text_adjustment,
    print_rich_table,
)
from openbb_terminal.stocks.comparison_analysis import marketwatch_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_income_comparison(
    symbols: List[str],
    timeframe: str = str(datetime.now().year - 1),
    quarter: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display income data. [Source: Marketwatch].

    Parameters
    ----------
    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
        You can also get a list of comparable peers with
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        What year to look at
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
    """
    df_financials_compared = marketwatch_model.get_income_comparison(
        symbols, timeframe, quarter
    )

    if len(df_financials_compared) == 0 or df_financials_compared.empty:
        return

    # Export data before the color
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "income",
        df_financials_compared,
        sheet_name,
    )

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df_financials_compared = df_financials_compared.applymap(
            lambda_financials_colored_values
        )
        patch_pandas_text_adjustment()

    if not quarter:
        df_financials_compared.index.name = timeframe

    print_rich_table(
        df_financials_compared,
        headers=list(df_financials_compared.columns),
        show_index=True,
        title="Income Data",
        export=bool(export),
    )


@log_start_end(log=logger)
def display_balance_comparison(
    symbols: List[str],
    timeframe: str = str(datetime.now().year - 1),
    quarter: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Compare balance between companies. [Source: Marketwatch]

    Parameters
    ----------
    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
        You can also get a list of comparable peers with
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        What year to look at
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
    """
    df_financials_compared = marketwatch_model.get_financial_comparisons(
        symbols, "balance", timeframe, quarter
    )

    if len(df_financials_compared) == 0 or df_financials_compared.empty:
        return

    # Export data before the color
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance",
        df_financials_compared,
        sheet_name,
    )

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df_financials_compared = df_financials_compared.applymap(
            lambda_financials_colored_values
        )
        patch_pandas_text_adjustment()

    if not quarter:
        df_financials_compared.index.name = timeframe

    print_rich_table(
        df_financials_compared,
        headers=list(df_financials_compared.columns),
        show_index=True,
        title="Company Comparison",
        export=bool(export),
    )


@log_start_end(log=logger)
def display_cashflow_comparison(
    symbols: List[str],
    timeframe: str = str(datetime.now().year - 1),
    quarter: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Compare cashflow between companies. [Source: Marketwatch]

    Parameters
    ----------
    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
        You can also get a list of comparable peers with
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        What year/quarter to look at
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
    """
    df_financials_compared = marketwatch_model.get_financial_comparisons(
        symbols, "cashflow", timeframe, quarter
    )

    if len(df_financials_compared) == 0 or df_financials_compared.empty:
        return

    # Export data before the color
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cashflow",
        df_financials_compared,
        sheet_name,
    )

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df_financials_compared = df_financials_compared.applymap(
            lambda_financials_colored_values
        )
        patch_pandas_text_adjustment()

    if not quarter:
        df_financials_compared.index.name = timeframe

    if any(isinstance(col, tuple) for col in df_financials_compared.columns):
        df_financials_compared.columns = [
            " ".join(col) for col in df_financials_compared.columns
        ]

    print_rich_table(
        df_financials_compared,
        headers=list(df_financials_compared.columns),
        show_index=True,
        title="Cashflow Comparison",
        export=bool(export),
    )
