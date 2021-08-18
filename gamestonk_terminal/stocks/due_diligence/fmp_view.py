""" Financial Modeling Prep View """
__docformat__ = "numpy"

from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import fmp_model


def rating(ticker: str, num: int):
    """Display ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of ratings to display
    """
    df_fa = fmp_model.get_rating(ticker)

    # TODO: This could be displayed in a nice rating plot over time
    # TODO: Add coloring to table

    l_recoms = [col for col in df_fa.columns if "Recommendation" in col]
    l_recoms_show = [
        recom.replace("rating", "").replace("Details", "").replace("Recommendation", "")
        for recom in l_recoms
    ]
    l_recoms_show[0] = "Rating"
    print(
        tabulate(
            df_fa[l_recoms].head(num),
            headers=l_recoms_show,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        )
    )
    print("")
