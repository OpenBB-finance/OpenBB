"""Economy Helper Functions"""
__docformat__ = "numpy"

from typing import Dict

import pandas as pd

def create_new_entry(dataset:Dict[str, pd.DataFrame], query:str) -> Dict:
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
    for _,df in dataset.items():
        if not df.empty:
            columns.extend(df.columns)
            data = pd.concat([data,df])
    # Eval the query to generate new sequence
    # if there is an = in the query, then there will be a new named column
    if "=" in query:
        new_df = data.eval(query)
        new_columns = [col for col in new_df if col not in columns][0]
        if "custom" in dataset:
            if new_columns in dataset["custom"].columns:
                new_df = new_df.rename(columns={new_columns:new_columns+"_duplicate"})
                new_columns += "_duplicate"
            dataset["custom"] = pd.concat([dataset["custom"],new_df[new_columns]])
        else:
            dataset["custom"] = new_df[new_columns]
        return dataset

    #If there is not an equal (namely  .eval(colA + colB), the result will be a series
    #and not a dataframe.  We can just call this custom_exp

    data = pd.DataFrame(data.eval(query), columns=["custom_exp"])
    dataset["custom"] = data
    return dataset
