import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console


def display_personal_routines(df: pd.DataFrame, page: int, pages: int):
    """Display the routines.

    Parameters
    ----------
    df : pd.DataFrame
        The routines list.
    page : int
        The current page.
    pages : int
        The total number of pages.
    """
    try:
        title = f"Personal routines - page {page}"
        if pages:
            title += f" of {pages}"

            df["updated_date"] = pd.to_datetime(df["updated_date"])
            df["updated_date"] = df["updated_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
            df.replace(to_replace=[None], value="-", inplace=True)
            print_rich_table(
                df=df,
                title=title,
                headers=["Name", "Description", "Version", "Last update"],
                show_index=True,
                index_name="#",
            )
    except Exception:
        console.print("Failed to display personal routines.")


def display_default_routines(df: pd.DataFrame):
    """Display the default routines.

    Parameters
    ----------
    df : pd.DataFrame
        The default routines list.
    """
    try:
        df["date_updated"] = pd.to_datetime(df["date_updated"])
        df["date_updated"] = df["date_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df.replace(to_replace=[None], value="-", inplace=True)
        print_rich_table(
            df=df,
            title="Default routines",
            headers=["Name", "Description", "Version", "Last update"],
            show_index=True,
            index_name="#",
        )
    except Exception:
        console.print("Failed to display default routines.")
