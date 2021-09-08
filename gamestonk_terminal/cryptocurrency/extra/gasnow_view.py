import os
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.cryptocurrency.extra.gasnow_model import get_gwei_fees


def display_gwei_fees(export: str) -> None:
    """Current gwei fees
    [Source: https://www.gasnow.org]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_gwei_fees()

    print("Current ETH gas fees (gwei):\n")
    print(df_fees.to_string(index=False), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gwei",
        df_fees,
    )
