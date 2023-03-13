"""Rekt view"""
import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.overview import rekt_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_crypto_hacks(
    limit: int = 15,
    sortby: str = "Platform",
    ascend: bool = False,
    slug: str = "polyntwork-rekt",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display list of major crypto-related hacks. If slug is passed
    individual crypto hack is displayed instead of list of crypto hacks
    [Source: https://rekt.news]

    Parameters
    ----------
    slug: str
        Crypto hack slug to check (e.g., polynetwork-rekt)
    limit: int
        Number of hacks to search
    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    if slug:
        text = rekt_model.get_crypto_hack(slug)
        if text:
            console.print(text)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ch",
            text,
            sheet_name,
        )
    else:
        df = rekt_model.get_crypto_hacks(sortby, ascend)

        if df.empty:
            console.print("\nError in rekt request\n")
        else:
            df["Amount [$]"] = df["Amount [$]"].apply(
                lambda x: lambda_long_number_format(x)
            )
            df["Date"] = df["Date"].dt.date

            print_rich_table(
                df,
                headers=list(df.columns),
                floatfmt=".1f",
                show_index=False,
                title="Major Crypto Hacks",
                export=bool(export),
                limit=limit,
            )

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "ch",
                df,
                sheet_name,
            )
