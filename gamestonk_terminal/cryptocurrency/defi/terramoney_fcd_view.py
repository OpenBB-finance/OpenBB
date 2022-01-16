"""Terra Engineer View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.defi import terramoney_fcd_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    prettify_column_names,
    very_long_number_formatter,
)


def display_account_staking_info(
    address: str = "", top: int = 10, export: str = ""
) -> None:
    """Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df, report = terramoney_fcd_model.get_staking_account_info(address)
    console.print(report)
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        console.print(df.to_string(index=False), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sinfo",
        df,
    )


def display_validators(
    top: int = 10, sortby: str = "votingPower", descend: bool = False, export: str = ""
) -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_validators()
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend).head(top)
    df["tokensAmount"] = df["tokensAmount"].apply(
        lambda x: very_long_number_formatter(x)
    )
    df.columns = [
        x if x not in ["Voting power", "Commission rate", "Uptime"] else f"{x} %"
        for x in prettify_column_names(df.columns)
    ]

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "validators",
        df_data,
    )


def display_gov_proposals(
    top: int = 10,
    status: str = "Voting",
    sortby: str = "id",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_proposals(status)
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend).head(top)
    df.columns = prettify_column_names(df.columns)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "proposals",
        df_data,
    )
