"""Excel Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
from openbb_terminal.rich_config import console

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_configuration(excel_file: str):
    """
    Load in the Excel file to determine the configuration that needs to be set.

    Parameters
    ----------
    excel_file: str
        The location of the Excel file that needs to be loaded.

    Returns
    -------
    configuration: dictionary
        Returns a dictionary with the configurations set.
    """
    # Read in the Optimization template
    df = pd.read_excel(
        excel_file,
        sheet_name="Optimization",
        skiprows=2,
        usecols="B:D",
        names=["Parameter", "Value", "Description"],
        index_col="Parameter",
    )

    # Remove completely empty NaN rows
    cleaned_df = df.dropna(axis="rows", thresh=2)

    # Filter out any general columns
    filtered_df = cleaned_df[cleaned_df["Description"] != "Description"]

    # Convert to Dictionary
    configuration = filtered_df.to_dict()

    return configuration["Value"], configuration["Description"]


@log_start_end(log=logger)
def load_allocation(excel_file: str):
    """
    Load in the Excel file to determine the allocation that needs to be set.

    Parameters
    ----------
    excel_file: str
        The location of the Excel file that needs to be loaded.

    Returns
    -------
    tickers: list
        Returns a list with ticker symbols
    categories: dictionary
        Returns a dictionary that specifies each category
    """
    if str(excel_file).endswith(".xlsx"):
        categories = pd.read_excel(excel_file, engine="openpyxl")
    elif str(excel_file).endswith(".csv"):
        categories = pd.read_excel(excel_file)
    else:
        console.print("Only acceptable files with .xlsx and .csv extensions\n")
        return [], {}

    categories.columns = [
        col.upper().strip().replace(" ", "_") for col in categories.columns
    ]
    categories = categories.apply(lambda x: x.astype(str).str.upper())
    categories = categories[~categories.index.duplicated(keep="first")]

    try:
        categories.set_index("TICKER", inplace=True)
        categories.sort_index(inplace=True)
    except KeyError:
        console.print("Allocation table needs a TICKER column\n")
        return [], {}

    tickers = list(categories.index)
    tickers.sort()
    categories = categories.to_dict()

    return tickers, categories
