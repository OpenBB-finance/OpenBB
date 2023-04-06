""" Seeking Alpha View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import seeking_alpha_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_eps_estimates(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
):
    """Display eps Estimates

    Parameters
    ----------
    symbol: str
        ticker of company
    """
    eps_estimates = seeking_alpha_model.get_estimates_eps(symbol)

    if not eps_estimates.empty:
        print_rich_table(
            eps_estimates,
            headers=list(eps_estimates.columns),
            show_index=False,
            title=f"{symbol.upper()} EPS History and Estimations",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "eps_estimates",
            eps_estimates,
            sheet_name,
        )
    else:
        console.print("No data found.")
        return


@log_start_end(log=logger)
def display_rev_estimates(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
):
    """Display rev Estimates

    Parameters
    ----------
    symbol: str
        ticker of company
    """

    rev_estimates = seeking_alpha_model.get_estimates_rev(symbol)

    if not rev_estimates.empty:
        print_rich_table(
            rev_estimates,
            headers=list(rev_estimates.columns),
            show_index=False,
            title=f"{symbol.upper()} Revenue History and Estimations",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rev_estimates",
            rev_estimates,
            sheet_name,
        )
    else:
        console.print("No data found.")
        return
