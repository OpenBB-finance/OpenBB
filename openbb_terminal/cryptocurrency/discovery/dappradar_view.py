"""DappRadar view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import numpy as np

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.discovery import dappradar_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_nft_marketplaces(
    limit: int = 10,
    sortby: str = "",
    order: str = "",
    chain: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing nft marketplaces [Source: https://dappradar.com/]

    Parameters
    ----------
    chain: str
        Name of the chain
    order: str
        Order of sorting (asc/desc)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Name of the sheet in excel or csv file
    """

    df = dappradar_model.get_nft_marketplaces(
        chain=chain,
        sortby=sortby,
        order=order,
        limit=limit,
    )
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    for col in ["Avg Price [$]", "Volume [$]"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna(-1)
                .apply(lambda x: lambda_very_long_number_formatter(x))
                .replace(-1, np.nan)
            )
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="NFT marketplaces",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drnft",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_nft_marketplace_chains(
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing nft marketplaces chains [Source: https://dappradar.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Name of the sheet in excel or csv file
    """

    df = dappradar_model.get_nft_marketplace_chains()
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="NFT marketplace chains",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drnftchains",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_dapps(
    chain: str = "",
    page: int = 1,
    resultPerPage: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Prints table showing dapps [Source: https://dappradar.com/]

    Parameters
    ----------
    chain: str
        Name of the chain
    page: int
        Page number
    resultPerPage: int
        Number of records per page
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Name of the sheet in excel or csv file
    """

    df = dappradar_model.get_dapps(
        chain=chain,
        page=page,
        resultPerPage=resultPerPage,
    )
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Dapps",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdapps",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_dapp_categories(
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing dapp categories [Source: https://dappradar.com/]"""

    df = dappradar_model.get_dapp_categories()
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Dapp categories",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdappcategories",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_dapp_chains(
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing dapp chains [Source: https://dappradar.com/]"""

    df = dappradar_model.get_dapp_chains()
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Dapp chains",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdappchains",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_dapp_metrics(
    dappId: int,
    chain: str = "",
    time_range: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing dapp metrics [Source: https://dappradar.com/]

    Parameters
    ----------
    dappId: int
        Dapp id
    chain: str
        Name of the chain
    range: str
        Range of data to display (24h, 7d, 30d)
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Name of the sheet in excel or csv file
    """

    df = dappradar_model.get_dapp_metrics(
        dappId=dappId,
        chain=chain,
        time_range=time_range,
    )
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    for col in ["Volume [$]", "Balance [$]"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna(-1)
                .apply(lambda x: lambda_very_long_number_formatter(x))
                .replace(-1, np.nan)
            )
    print_rich_table(
        df.T,
        show_index=True,
        title=f"Dapp metrics for dappId: {dappId}",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdappmetrics",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_defi_chains(export: str = "", sheet_name: Optional[str] = None) -> None:
    """Prints table showing defi chains [Source: https://dappradar.com/]"""

    df = dappradar_model.get_defi_chains()
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Defi chains",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdefichains",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_DAPPRADAR_KEY"])
def display_token_chains(
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing chains that support tokens [Source: https://dappradar.com/]"""

    df = dappradar_model.get_token_chains()
    if df.empty:
        console.print("[red]Failed to fetch data from DappRadar[/red]")
        return
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Token chains",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drtokenchains",
        df,
        sheet_name,
    )
