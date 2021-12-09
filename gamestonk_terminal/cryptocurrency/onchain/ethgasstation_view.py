"""ETH Gas Station view"""
import os

from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.cryptocurrency.onchain.ethgasstation_model import get_gwei_fees
from gamestonk_terminal import feature_flags as gtff


def display_gwei_fees(export: str) -> None:
    """Current gwei fees
    [Source: https://ethgasstation.info]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_gwei_fees()

    if df_fees.empty:
        print("\nError in ethgasstation request\n")
    else:
        print("\nCurrent ETH gas fees (gwei):")

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
