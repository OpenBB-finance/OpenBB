import os

from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.cryptocurrency.onchain.gasnow_model import get_gwei_fees
from gamestonk_terminal import feature_flags as gtff


def display_gwei_fees(export: str) -> None:
    """Current gwei fees
    [Source: https://www.gasnow.org]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_gwei_fees()

    print("Current ETH gas fees (gwei):")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_fees.head(4),
                headers=df_fees.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df_fees.to_string(index=False), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gwei",
        df_fees,
    )
