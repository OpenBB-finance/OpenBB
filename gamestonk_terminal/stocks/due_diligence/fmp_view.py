""" Financial Modeling Prep View """
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.due_diligence import fmp_model
from gamestonk_terminal.rich_config import console


def rating(ticker: str, num: int, export: str):
    """Display ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of last days ratings to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = fmp_model.get_rating(ticker)

    # TODO: This could be displayed in a nice rating plot over time
    # TODO: Add coloring to table

    if not df.empty:
        l_recoms = [col for col in df.columns if "Recommendation" in col]
        l_recoms_show = [
            recom.replace("rating", "")
            .replace("Details", "")
            .replace("Recommendation", "")
            for recom in l_recoms
        ]
        l_recoms_show[0] = "Rating"
        print(
            tabulate(
                df[l_recoms].head(num),
                headers=l_recoms_show,
                floatfmt=".2f",
                showindex=True,
                tablefmt="fancy_grid",
            )
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df,
    )
