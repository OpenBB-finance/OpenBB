import os
import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import commodity_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_debt(export: str = ""):
    """Displays national debt for given countries [Source: Yahoo Finance]

    Parameters
    ----------
    export : str
        The path to export to
    Returns
    ----------
    Shows a table with national debt for various countries.
    """
    debt_df = commodity_model.get_debt()

    print_rich_table(
        debt_df,
        headers=debt_df.columns,
        title="National Debt",
    )
    if export:
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "cdebt", debt_df
        )
