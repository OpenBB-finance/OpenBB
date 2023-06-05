"""HackerNews view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.alternative.hackernews_model import get_stories
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_stories(
    limit: int = 10, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """View top stories from HackerNews.
    Parameters
    ----------
    limit: int
        Number of stories to return
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df = get_stories(limit)
    if not df.empty:
        df.columns = [col.capitalize() for col in df.columns]
        print_rich_table(df, title="HackerNews Top Stories", export=bool(export))
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hn",
        df,
        sheet_name,
    )
