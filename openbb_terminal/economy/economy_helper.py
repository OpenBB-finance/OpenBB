"""Economy Helper Functions"""
__docformat__ = "numpy"

from typing import Dict

import pandas as pd


def create_new_entry(dataset: Dict[str, pd.DataFrame], query: str) -> Dict:
    """Create a new series based off previously loaded columns

    Parameters
    ----------
    dataset: Dict[str,pd.DataFrame]
        Economy datasets that are loaded
    query: str
        Query to execute

    Returns
    -------
    Dict[str, pd.DataFrame]
    """
    # Create a single dataframe from dictionary of dataframes
    columns = []
    data = pd.DataFrame()
    for _, df in dataset.items():
        if not df.empty:
            columns.extend(df.columns)
            data = pd.concat([data, df])
    # Eval the query to generate new sequence
    # if there is an = in the query, then there will be a new named column
    if "=" in query:
        new_column = query.split("=")[0].replace(" ", "")
        if new_column in data.columns:
            query = query.replace(new_column, new_column + "_duplicate")
            new_column += "_duplicate"
        new_df = data.eval(query)
        # If custom exists in the dictionary, we need to append the current dataframe
        if "custom" in dataset:
            dataset["custom"] = pd.concat([dataset["custom"], new_df[[new_column]]])
            print(dataset["custom"].head())
        else:
            dataset["custom"] = new_df[[new_column]]
        return dataset

    # If there is not an equal (namely  .eval(colA + colB), the result will be a series
    # and not a dataframe.  We can just call this custom_exp

    data = pd.DataFrame(data.eval(query), columns=["custom_exp"])
    dataset["custom"] = data
    return dataset
