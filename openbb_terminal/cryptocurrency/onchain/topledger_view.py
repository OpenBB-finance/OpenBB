"""Topledger Data view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.onchain import topledger_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_topledger_data(
    org_slug: str,
    query_slug: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display on-chain data from Topledger. [Source: Topledger]

    Parameters
    ----------
    org_slug: str
        Organization Slug
    query_slug: str
        Query Slug
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df = topledger_model.get_topledger_data(org_slug, query_slug)
    if df.empty:
        console.print("Failed to retrieve data.")
        return
    df_data = df.copy()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Topledger Query Result {query_slug} for {org_slug}",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{query_slug} for {org_slug}",
        df_data,
        sheet_name,
    )
