"""Forecast Model"""
__docformat__ = "numpy"

# pylint: disable=eval-used

import logging
from pathlib import Path
from typing import Dict, Union, Any, Optional, List
from itertools import chain

import pandas as pd
from pandas import DataFrame
import numpy as np

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.core.config.paths import (
    USER_EXPORTS_DIRECTORY,
    USER_CUSTOM_IMPORTS_DIRECTORY,
)

logger = logging.getLogger(__name__)


base_file_types = ["csv", "xlsx"]


def get_default_files() -> Dict[str, Path]:
    """Get the default files to load.

    Returns
    -------
    default_files : Dict[str, Path]
        A dictionary to map the default file names to their paths.
    """
    default_files = {
        filepath.name: filepath
        for file_type in base_file_types
        for filepath in chain(
            USER_EXPORTS_DIRECTORY.rglob(f"*.{file_type}"),
            USER_CUSTOM_IMPORTS_DIRECTORY.rglob(f"*.{file_type}"),
        )
        if filepath.is_file()
    }
    return default_files


@log_start_end(log=logger)
def load(
    file: str,
    file_types: Optional[List[str]] = None,
    data_files: Optional[Dict[Any, Any]] = None,
    add_extension: bool = False,
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
    add_extension:
        Takes a file name and tries loading with csv or xlsx extension

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
    """
    if file_types is None:
        file_types = ["csv", "xlsx"]
    if data_files is None:
        data_files = get_default_files()

    if file in data_files:
        full_file = data_files[file]
    else:
        full_file = file

    if add_extension:
        for ext in ["xlsx", "csv"]:
            tmp = f"{full_file}.{ext}"
            if tmp in data_files:
                full_file = data_files[tmp]

    if not Path(full_file).exists():
        console.print(f"[red]Cannot find the file {full_file}[/red]\n")

        return pd.DataFrame()

    file_type = Path(full_file).suffix

    if file_type == ".xlsx":
        data = pd.read_excel(full_file)
    elif file_type == ".csv":
        data = pd.read_csv(full_file)
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
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one
        options table.
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
def clean(
    dataset: pd.DataFrame,
    fill: Optional[str] = None,
    drop: Optional[str] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Clean up NaNs from the dataset

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    fill : Optional[str]
        The method of filling NaNs
    drop : Optional[str]
        The method of dropping NaNs
    limit : Optional[int]
        The maximum limit you wish to apply that can be forward or backward filled

    Returns
    -------
    pd.DataFrame:
        Dataframe with cleaned up data
    """
    kwargs = {}
    if limit:
        kwargs["limit"] = limit

    if fill:
        if fill == "rfill":
            dataset = dataset.fillna(axis="index", value=0)
        if fill == "cfill":
            dataset = dataset.fillna(axis="columns", value=0)
        elif fill == "rbfill":
            dataset = dataset.fillna(axis="index", method="bfill", **kwargs)
        elif fill == "cbfill":
            dataset = dataset.fillna(axis="columns", method="bfill", **kwargs)
        elif fill == "rffill":
            dataset = dataset.fillna(axis="index", method="ffill", **kwargs)
        elif fill == "cffill":
            dataset = dataset.fillna(axis="columns", method="ffill", **kwargs)

    if drop:
        if drop == "rdrop":
            dataset = dataset.dropna(how="any", axis="index")
        elif drop == "cdrop":
            dataset = dataset.dropna(how="any", axis="columns")

    # TODO - think about if we want to always interpolate and remove above options
    if fill == "" and drop == "":
        # drop all rows with na
        dataset = dataset.dropna(axis=0)

    dataset = dataset.reset_index(drop=True)

    return dataset, dataset.isnull().values.any()


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
def add_sto(
    dataset: pd.DataFrame,
    close_column: str = "close",
    high_column: str = "high",
    low_column: str = "low",
    period: int = 10,
) -> pd.DataFrame:
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
        low_column in dataset.columns
        and high_column in dataset.columns
        and close_column in dataset.columns
    ):
        STOK = (
            (dataset[close_column] - dataset[low_column].rolling(period).min())
            / (
                dataset[high_column].rolling(period).max()
                - dataset[low_column].rolling(period).min()
            )
        ) * 100

        dataset[f"SO%K_{period}"] = STOK
        dataset[f"SO%D_{period}"] = STOK.rolling(3).mean()

        return dataset

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
    u[u.index[period - 1]] = np.mean(u.iloc[:period])  # first value is sum of avg gains
    u = u.drop(u.index[: (period - 1)])
    d[d.index[period - 1]] = np.mean(
        d.iloc[:period]
    )  # first value is sum of avg losses
    d = d.drop(d.index[: (period - 1)])
    rs = (
        u.ewm(com=period - 1, adjust=False).mean()
        / d.ewm(com=period - 1, adjust=False).mean()
    )
    dataset[f"RSI_{period}_{target_column}"] = 100 - 100 / (1 + rs)

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

    return dataset


@log_start_end(log=logger)
def add_delta(
    dataset: pd.DataFrame,
    target_column: str = "close",
) -> pd.DataFrame:
    """
    Calculate the %change of a variable based on a specific column
    """

    dataset[f"delta_{target_column}"] = dataset[target_column].pct_change().fillna(0)

    return dataset


@log_start_end(log=logger)
def add_atr(
    dataset: pd.DataFrame,
    close_column: str = "close",
    high_column: str = "high",
    low_column: str = "low",
) -> pd.DataFrame:
    """
    Calculate the Average True Range of a variable based on a a specific stock ticker.
    """

    if "high" in dataset and "low" in dataset and "close" in dataset:
        dataset["ATR1"] = abs(dataset[high_column] - dataset[low_column])
        dataset["ATR2"] = abs(dataset[high_column] - dataset[close_column].shift())
        dataset["ATR3"] = abs(dataset[low_column] - dataset[close_column].shift())
        dataset["true_range"] = dataset[["ATR1", "ATR2", "ATR3"]].max(axis=1)

        # drop ATR1, ATR2, ATR3
        dataset = dataset.drop(["ATR1", "ATR2", "ATR3"], axis=1)

        return dataset, True

    return dataset, False


@log_start_end(log=logger)
def add_signal(dataset: pd.DataFrame) -> pd.DataFrame:
    """A price signal based on short/long term price.

    1 if the signal is that short term price will go up as compared to the long term.
    0 if the signal is that short term price will go down as compared to the long term.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate with

    Returns
    -------
    pd.DataFrame:
        Dataframe with added signal column
    """

    # Create short simple moving average over the short window
    # > Create long simple moving average over the long window

    # Create signals
    dataset["signal"] = np.where(
        dataset["close"].rolling(window=10, min_periods=1, center=False).mean()
        > dataset["close"].rolling(window=60, min_periods=1, center=False).mean(),
        1.0,
        0.0,
    )

    return dataset


@log_start_end(log=logger)
def combine_dfs(
    df1: pd.DataFrame, df2: pd.DataFrame, column: str, dataset: str = ""
) -> pd.DataFrame:
    """Adds the given column of df2 to df1

    Parameters
    ----------
    df1: pd.DataFrame
        The dataframe to add a column to
    df2: pd.DataFrame
        The dataframe to lose a column
    column: str
        The column to transfer
    dataset: str
        A name for df2 (shows in name of new column)

    Returns
    ----------
    data: pd.DataFrame
        The new dataframe
    """
    if column not in df2:
        console.print(
            f"Not able to find the column {column}. Please choose one of "
            f"the following: {', '.join(df2.columns)}"
        )
        return df1

    if "date" in df1.columns and "date" in df2.columns:
        selected = df2[[column, "date"]]
        new_cols = [f"{dataset}_{x}" if x != "date" else "date" for x in selected]
        selected.columns = new_cols
        return df1.merge(selected, on="date", how="left")

    console.print(
        "[red]Not all dataframes have a date column so we are combining"
        " on index, this may results in data mismatching.[/red]\n"
    )
    selected = df2[[column]]
    new_cols = [f"{dataset}_{x}" for x in selected]
    selected.columns = new_cols
    return df1.merge(selected, left_index=True, right_index=True, how="left")


@log_start_end(log=logger)
def delete_column(df: pd.DataFrame, column: str) -> None:
    if column not in df:
        console.print(
            f"Not able to find the column {column}. Please choose one of "
            f"the following: {', '.join(df.columns)}"
        )
    else:
        del df[column]


@log_start_end(log=logger)
def rename_column(df: pd.DataFrame, old_column: str, new_column: str) -> pd.DataFrame:
    """Rename a column in a dataframe

    Parameters
    ----------
    df: pd.DataFrame
        The dataframe to have a column renamed
    old_column: str
        The column that will have its name changed
    new_column: str
        The name to update to

    Returns
    ----------
    new_df: pd.DataFrame
        The dataframe with the renamed column
    """
    if old_column not in df:
        console.print(
            f"Not able to find the column {old_column}. Please choose one of "
            f"the following: {', '.join(df.columns)}"
        )
        return df
    return df.rename(columns={old_column: new_column})


@log_start_end(log=logger)
def describe_df(df: pd.DataFrame) -> pd.DataFrame:
    """Returns statistics for a given df

    Parameters
    ----------
    df: pd.DataFrame
        The df to produce statistics for

    Returns
    ----------
    df: pd.DataFrame
        The df with the new data
    """
    return df.describe()


@log_start_end(log=logger)
def corr_df(df: pd.DataFrame) -> pd.DataFrame:
    """Returns correlation for a given df

    Parameters
    ----------
    df: pd.DataFrame
        The df to produce statistics for

    Returns
    ----------
    df: pd.DataFrame
        The df with the new data
    """
    corr = df.corr(numeric_only=True)
    return corr
