"""Economy helpers"""
__docformat__ = "numpy"

from typing import Dict

import pandas as pd

from openbb_terminal.rich_config import console


def text_transform(raw_text: str) -> str:
    return f"{round(float(raw_text)/100, 3)}%"


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
            data = pd.concat([data, df], axis=1)
    # In order to account for potentially different index time steps, lets dropNans here.
    # Potentially problematic down the road
    data = data.dropna(axis=0)

    # Eval the query to generate new sequence
    # if there is an = in the query, then there will be a new named column
    if "=" in query:
        new_column = query.split("=")[0].replace(" ", "")
        if new_column in data.columns:
            query = query.replace(new_column, new_column + "_duplicate")
            new_column += "_duplicate"
        # Wrap the eval in a syntax error in case the user does something not allowed
        try:
            new_df = data.eval(query)
        except SyntaxError:
            console.print(
                "[red]Invalid syntax in query.  Please enter something of the form `newcol=col1 + col2`[/red]\n"
            )
            return dataset
        except pd.errors.UndefinedVariableError as e:
            console.print(f"[red]{e}[/red]")
            return dataset

        # If custom exists in the dictionary, we need to append the current dataframe
        if "custom" in dataset:
            dataset["custom"] = pd.concat([dataset["custom"], new_df[[new_column]]])
        else:
            dataset["custom"] = new_df[[new_column]]
        return dataset

    # If there is not an equal (namely  .eval(colA + colB), the result will be a series
    # and not a dataframe.  We can just call this custom_exp

    try:
        data = pd.DataFrame(data.eval(query), columns=["custom_exp"])
        dataset["custom"] = data
    except SyntaxError:
        console.print(
            "Invalid syntax in query.  Please enter something of the form `newcol=col1 + col2`"
        )
        return dataset
    except pd.errors.UndefinedVariableError as e:
        console.print(f"[red]{e}[/red]")
        return dataset
    return dataset


def update_stored_datasets_string(datasets) -> str:
    stored_datasets_string = ""
    for key in datasets:
        # ensure that column name is not empty
        if not datasets[key].columns.empty:
            # update string
            for i, col in enumerate(datasets[key].columns):
                if i == 0:
                    stored_datasets_string += (
                        "\n"
                        + " " * 2
                        + key
                        + " " * (len("Stored datasets") - len(key) - 2)
                        + ": "
                    )
                    stored_datasets_string += col
                else:
                    stored_datasets_string += ", " + col

    return stored_datasets_string
