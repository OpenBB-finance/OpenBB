"""SDK Helper Functions."""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.economy import finviz_model, wsj_model


def futures(source="WSJ", future_type: str = "Indices") -> pd.DataFrame:
    """Get futures data.

    Parameters
    ----------
    source : str
        Data source for futures data.  From the following: WSJ, Finviz
    future_type : str
        (Finviz only) Future type to get.  Can be: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies.

    Returns
    -------
    pd.DataFrame
        Dataframe of futures data.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> wsj_futures = openbb.economy.futures()

    To sort by the largest percent change:
    >>> futures_sorted = openbb.economy.futures().sort_values(by="%Chg", ascending=False)

    FinViz provides different options for future types.  We can get Meats with the following command:
    >>> meat_futures = openbb.economy.futures(source="Finviz", future_type="Meats")

    """

    if source.lower() == "wsj":
        return wsj_model.top_commodities()
    if source.lower() == "finviz":
        return finviz_model.get_futures(future_type.title())
    return pd.DataFrame()
