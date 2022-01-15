""" opensea.io View """

import os
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.cryptocurrency.nft.opensea_model import get_collection_stats
from gamestonk_terminal.rich_config import console


def display_collection_stats(slug: str, export: str):
    """Display collection stats. [Source: opensea.io]

    Parameters
    ----------
    slug: str
        Opensea collection slug. If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    collection_stats_df = get_collection_stats(slug)
    if collection_stats_df.empty:
        console.print("No data found.", "\n")
    else:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    collection_stats_df,
                    headers=collection_stats_df.columns,
                    floatfmt=".2f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            console.print(collection_stats_df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        collection_stats_df,
    )
