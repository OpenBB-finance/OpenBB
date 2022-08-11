import os
import logging

from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import debt_clock_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_debt(
    export: str = "",
):
    """Displays national debt information for various countries. [Source: UsDebtClock.org]

    Parameters
    ----------
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df_group = debt_clock_model.get_debt()

    if df_group.empty:
        return

    print_rich_table(
        df_group.fillna(""),
        show_index=False,
        headers=df_group.columns,
        title="National Debt",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cdebt",
        df_group,
    )
