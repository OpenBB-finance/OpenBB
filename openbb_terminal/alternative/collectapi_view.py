"""CollectAPI view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.alternative.collectapi_model import get_european_gas_prices

logger = logging.getLogger(__name__)


SORTBY_EUROPEAN_GAS_PRICES = ["Country", "Diesel", "Gasoline", "Lpg"]


@log_start_end(log=logger)
def display_european_gas_prices(
    country: str = "",
    limit: int = 10,
    sortby: str = "",
    reverse: bool = False,
    export: str = "",
) -> None:
    """View European gas prices.
    Parameters
    ----------
    country: str
        Country to filter by
    limit: int
        Number of stories to return
    sortby: str
        Column to sort by
    reverse: bool
        Sort in descending order
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df = get_european_gas_prices()
    if not df.empty:
        if country:
            df_copy = df[df.index == country]
        else:
            df_copy = df
            if sortby:
                df_copy = df[df[sortby] != 0.0]
                df_copy = df_copy.sort_values(by=sortby, ascending=reverse)
            df_copy = df_copy.iloc[:limit]
            df_copy.columns = [col.capitalize() for col in df.columns]
            df_copy["Diesel"] = df_copy["Diesel"].astype(str) + " €"
            df_copy["Gasoline"] = df_copy["Gasoline"].astype(str) + " €"
            df_copy["Lpg"] = df_copy["Lpg"].astype(str) + " €"
        print_rich_table(
            df_copy, title="European Gas Prices", show_index=True, index_name="Country"
        )
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "gp", df)
