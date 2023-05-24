import logging
import os
from typing import Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import commodity_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


def format_large_numbers(num: float) -> str:
    """Converts floats into strings and adds commas to the number

    Parameters
    ----------
    num: float
        The number to convert

    Returns
    -------
    num: str
        The formatted number
    """
    return f"{num:,}"


@log_start_end(log=logger)
def display_debt(export: str = "", sheet_name: Optional[str] = None, limit: int = 20):
    """Displays external debt for given countries [Source: Wikipedia]

    Parameters
    ----------
    export : str
        The path to export to
    limit : int
        The number of countries to show
    """
    debt_df = commodity_model.get_debt()

    if not get_current_user().preferences.USE_INTERACTIVE_DF:
        for col in ["USD Debt", "USD Per Capita"]:
            debt_df[col] = debt_df[col].apply(lambda x: format_large_numbers(x))

    print_rich_table(
        debt_df,
        show_index=False,
        headers=debt_df.columns,
        title="External Debt (USD)",
        export=bool(export),
        limit=limit,
    )
    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cdebt",
            debt_df,
            sheet_name,
        )
