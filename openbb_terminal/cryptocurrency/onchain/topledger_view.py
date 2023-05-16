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
    org_slug: str = None,
    query_slug: str = None,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    df = topledger_model.get_topledger_data(org_slug, query_slug)
    if df.empty:
        console.print("Failed to retrieve data.")
        return
    df_data = df.copy()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Topledger Query Result for [{org_slug} {query_slug}]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "topledger-query-result",
        df_data,
        sheet_name,
    )
