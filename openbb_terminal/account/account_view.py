import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table


def display_routines_list(df: pd.DataFrame, page: int, pages: int):
    title = f"Available routines - page {page}"
    if pages:
        title += f" of {pages}"

    print_rich_table(
        df=df,
        title=title,
        headers=["Name", "Description"],
        show_index=True,
        index_name="#",
    )
