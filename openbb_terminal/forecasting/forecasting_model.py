"""Forecasting Model"""
__docformat__ = "numpy"

# pylint: disable=eval-used

import logging
from pathlib import Path
from typing import Dict, Union, Any

import pandas as pd
from pandas import DataFrame

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(
    file: str,
    file_types: list,
    data_files: Dict[Any, Any],
) -> pd.DataFrame:
    """Load custom file into dataframe.

    Parameters
    ----------
    file: str
        Path to file
    file_types: list
        Supported file types
    data_files: dict
        Contains all available data files within the Export folder

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
    """

    if file in data_files:
        file = data_files[file]

    if not Path(file).exists():
        console.print(f"[red]Cannot find the file {file}[/red]\n")
        return pd.DataFrame()

    file_type = Path(file).suffix

    if file_type == ".xlsx":
        data = pd.read_excel(file)
    elif file_type == ".csv":
        data = pd.read_csv(file)
    else:
        return console.print(
            f"The file type {file_type} is not supported. Please choose one of the following: "
            f"{', '.join(file_types)}"
        )

    return data


@log_start_end(log=logger)
def get_options(
    datasets: Dict[str, pd.DataFrame], dataset_name: str = None
) -> Dict[Union[str, Any], DataFrame]:
    """Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

    Parameters
    ----------
    datasets: dict
        The available datasets.
    dataset_name: str
        The dataset you wish to show the options for.

    Returns
    -------
    option_tables: dict
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one options table.
    """
    option_tables = {}

    if dataset_name:
        columns = datasets[dataset_name].columns
        option_tables[dataset_name] = pd.DataFrame(
            {
                "column": columns,
                "option": [f"{dataset_name}.{column}" for column in columns],
            }
        )
    else:
        for dataset, data_values in datasets.items():
            columns = data_values.columns
            option_tables[dataset] = pd.DataFrame(
                {
                    "column": columns,
                    "option": [f"{dataset}.{column}" for column in columns],
                }
            )

    return option_tables


@log_start_end(log=logger)
def clean(dataset: pd.DataFrame, fill: str, drop: str, limit: int) -> pd.DataFrame:
    """Clean up NaNs from the dataset

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    fill : str
        The method of filling NaNs
    drop : str
        The method of dropping NaNs
    limit : int
        The maximum limit you wish to apply that can be forward or backward filled

    Returns
    -------
    pd.DataFrame:
        Dataframe with cleaned up data
    """
    if fill:
        if fill == "rfill":
            dataset = dataset.fillna(axis="index", value=0)
        if fill == "cfill":
            dataset = dataset.fillna(axis="columns", value=0)
        elif fill == "rbfill":
            dataset = dataset.fillna(axis="index", method="bfill", limit=limit)
        elif fill == "cbfill":
            dataset = dataset.fillna(axis="columns", method="bfill", limit=limit)
        elif fill == "rffill":
            dataset = dataset.fillna(axis="index", method="ffill", limit=limit)
        elif fill == "cffill":
            dataset = dataset.fillna(axis="columns", method="ffill", limit=limit)

    if drop:
        if drop == "rdrop":
            dataset = dataset.dropna(how="any", axis="index")
        elif drop == "cdrop":
            dataset = dataset.dropna(how="any", axis="columns")

    return dataset
