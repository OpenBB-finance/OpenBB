import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table


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
    title = f"Personal routines - page {page}"
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


def display_default_routines(df: pd.DataFrame):
    """Display the default routines.

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
