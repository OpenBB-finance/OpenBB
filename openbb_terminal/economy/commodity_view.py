import os
import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import commodity_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


def large_numbers(x: float) -> str:
    return f"{x:,}"


@log_start_end(log=logger)
def display_debt(export: str = "", limit: int = 20):
    """Displays national debt for given countries [Source: Yahoo Finance]

    Parameters
    ----------
    export : str
        The path to export to
    limit : int
        The number of countries to show

    Returns
    ----------
    Shows a table with national debt for various countries.
    """
    debt_df = commodity_model.get_debt()

    for col in ["Debt", "Per Capita"]:
        debt_df[col] = debt_df[col].apply(lambda x: large_numbers(x))

    print_rich_table(
        debt_df[:limit],
        show_index=True,
        headers=debt_df.columns,
        title="National Debt (USD)",
    )
    if export:
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "cdebt", debt_df
        )
