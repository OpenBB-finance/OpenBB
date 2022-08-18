""" Financial Modeling Prep View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.due_diligence import fmp_model

logger = logging.getLogger(__name__)


def add_color(value: str) -> str:
    if "buy" in value.lower():
        value = f"[green]{value}[/green]"
    elif "sell" in value.lower():
        value = f"[red]{value}[/red]"
    return value


@log_start_end(log=logger)
def rating(symbol: str, limit: int = 10, export: str = ""):
    """Display ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of last days ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df = fmp_model.get_rating(symbol)

    # TODO: This could be displayed in a nice rating plot over time

    if not df.empty:
        df = df.astype(str).applymap(lambda x: add_color(x))
        l_recoms = [col for col in df.columns if "Recommendation" in col]
        l_recoms_show = [
            recom.replace("rating", "")
            .replace("Details", "")
            .replace("Recommendation", "")
            for recom in l_recoms
        ]
        l_recoms_show[0] = "Rating"
        print_rich_table(
            df[l_recoms].head(limit),
            headers=l_recoms_show,
            show_index=True,
            title="Rating",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df,
    )
