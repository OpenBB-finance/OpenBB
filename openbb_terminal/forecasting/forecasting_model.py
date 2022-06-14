"""Forecasting Model"""
__docformat__ = "numpy"

# pylint: disable=eval-used

import logging
from pathlib import Path
from typing import Dict, Union, Any

import pandas as pd
from pandas import DataFrame
import numpy as np

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

    # TODO - think about if we want to always interpolate and remove above options
    if not fill or not drop:
        # We just want to interpolate any missing nans for timeseries
        dataset = dataset.interpolate(method="linear")

    # reset dataset index
    # dataset = dataset.reset_index(drop=True)
    console.print("Null Values in dataset =", dataset.isnull().values.any())

    return dataset


@log_start_end(log=logger)
def add_ema(
    dataset: pd.DataFrame, target_column: str = "close", period: int = 10
) -> pd.DataFrame:
    """A moving average provides an indication of the trend of the price movement
    by cut down the amount of "noise" on a price chart.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    target_column : str
        The column you wish to add the EMA to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added EMA column
    """
    dataset[f"EMA_{period}"] = (
        dataset[target_column].ewm(span=period, adjust=False).mean()
    )

    return dataset


@log_start_end(log=logger)
def add_sto(dataset: pd.DataFrame, period: int = 10) -> pd.DataFrame:
    """Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing
    price of a security to a range of its prices over a certain period of time. %K and %D are slow and fast indicators.

    Requires Low/High/Close columns.
    Note: This will drop first rows equal to period due to how this metric is calculated.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate for
    period : int
        Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added STO K & D columns
    """

    # check if columns exist
    if (
        "low" in dataset.columns
        and "high" in dataset.columns
        and "close" in dataset.columns
    ):
        STOK = (
            (dataset["close"] - dataset["low"].rolling(period).min())
            / (
                dataset["high"].rolling(period).max()
                - dataset["low"].rolling(period).min()
            )
        ) * 100

        dataset[f"SO%K_{period}"] = STOK
        dataset[f"SO%D_{period}"] = STOK.rolling(3).mean()

        # TODO - See what other thing we can do to avoid this...
        # drop na in %K and %D
        dataset = dataset.dropna(subset=[f"SO%K_{period}", f"SO%D_{period}"])
        dataset = dataset.reset_index(drop=True)
        return dataset

    else:
        console.print("[red]Missing Low/High/Close columns[/red]\n")
        return dataset


@log_start_end(log=logger)
def add_rsi(
    dataset: pd.DataFrame, target_column: str = "close", period: int = 10
) -> pd.DataFrame:
    """A momentum indicator that measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions in the price of a stock or other asset.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate for
    target_column : str
        The column you wish to add the RSI to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added RSI column
    """

    delta = dataset[target_column].diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period - 1]] = np.mean(u[:period])  # first value is sum of avg gains
    u = u.drop(u.index[: (period - 1)])
    d[d.index[period - 1]] = np.mean(d[:period])  # first value is sum of avg losses
    d = d.drop(d.index[: (period - 1)])
    rs = (
        u.ewm(com=period - 1, adjust=False).mean()
        / d.ewm(com=period - 1, adjust=False).mean()
    )
    dataset[f"RSI_{period}"] = 100 - 100 / (1 + rs)

    # TODO - See what other thing we can do to avoid this...
    # drop na in dataset
    dataset = dataset.dropna(subset=[f"RSI_{period}"])
    dataset = dataset.reset_index(drop=True)
    return dataset


@log_start_end(log=logger)
def add_roc(
    dataset: pd.DataFrame, target_column: str = "close", period: int = 10
) -> pd.DataFrame:
    """A momentum oscillator, which measures the percentage change between the current
    value and the n period past value.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate with
    target_column : str
        The column you wish to add the ROC to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added ROC column
    """
    M = dataset[target_column].diff(period - 1)
    N = dataset[target_column].shift(period - 1)

    dataset[f"ROC_{period}"] = (M / N) * 100
    # TODO - See what other thing we can do to avoid this...
    # drop na in dataset
    dataset = dataset.dropna(subset=[f"ROC_{period}"])
    dataset = dataset.reset_index(drop=True)
    return dataset


@log_start_end(log=logger)
def add_momentum(
    dataset: pd.DataFrame, target_column: str = "close", period: int = 10
) -> pd.DataFrame:
    """A momentum oscillator, which measures the percentage change between the current
    value and the n period past value.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate with
    target_column : str
        The column you wish to add the MOM to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added MOM column
    """

    dataset[f"Momentum_{period}"] = dataset[target_column].diff(period)
    # TODO - See what other thing we can do to avoid this...
    # drop na in dataset
    dataset = dataset.dropna(subset=[f"Momentum_{period}"])
    dataset = dataset.reset_index(drop=True)
    return dataset
