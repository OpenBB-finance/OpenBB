import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table


def display_routines_list(df: pd.DataFrame, page: int, pages: int):
    """Display the routines list.

    Parameters
    ----------
    df : pd.DataFrame
        The routines list.
    page : int
        The current page.
    pages : int
        The total number of pages.
    """
    title = f"User routines - page {page}"
    if pages:
        title += f" of {pages}"

    if all(c in df.columns for c in ["name", "description", "version"]):
        print_rich_table(
            df=df,
            title=title,
            headers=["Name", "Description", "Version"],
            show_index=True,
            index_name="#",
        )


def display_default_routines_list(df: pd.DataFrame):
    """Display the default routines list.

    Parameters
    ----------
    df : pd.DataFrame
        The default routines list.
    """
    if all(c in df.columns for c in ["name", "description", "version"]):
        print_rich_table(
            df=df,
            title="Default routines",
            headers=["Name", "Description", "Version"],
            show_index=True,
            index_name="#",
        )
