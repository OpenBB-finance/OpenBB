import pandas as pd


def no_dfs(args: list, kwargs: dict) -> bool:
    """Returns false if there are in dataframe objects given"""
    for item in args:
        if isinstance(item, pd.DataFrame):
            return False
    for item in kwargs.values():
        if isinstance(item, pd.DataFrame):
            return False
    return True
