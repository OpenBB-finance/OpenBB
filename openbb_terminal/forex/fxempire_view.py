"""FXEmpire view"""

import logging
import os
from openbb_terminal.forex import fxempire_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.helper_funcs import print_rich_table, export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_forward_rates(to_symbol: str, from_symbol: str, export: str = ""):
    """Display forward rates for currency pairs

    Parameters
    ----------
    to_symbol: str
        To currency
    from_symbol: str
        From currency
    export: str
        Format to export data
    """
    forward_rates = fxempire_model.get_forward_rates(to_symbol, from_symbol)
    if forward_rates.empty:
        console.print(
            f"[red]Forward rates not found for {to_symbol}/{from_symbol}.[/red]\n"
        )
        return

    print_rich_table(
        forward_rates,
        index_name="Expirations",
        show_index=True,
        headers=forward_rates.columns,
        title=f"Forward rates for {from_symbol}/{to_symbol}",
        floatfmt=".4f",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fwd",
        forward_rates,
    )
