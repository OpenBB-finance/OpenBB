"""Excel Model"""
__docformat__ = "numpy"

# pylint: disable=abstract-class-instantiated

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_configuration(excel_file: str = ""):
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
def load_allocation(excel_file: str = ""):
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
        categories = pd.read_excel(excel_file, sheet_name="Allocation", usecols="A:G")
        categories = categories.dropna(axis="rows")
    elif str(excel_file).endswith(".csv"):
        categories = pd.read_excel(excel_file)
        categories = categories.dropna(axis="rows")
    else:
        console.print("Only Excel (.xlsx and .csv) files are accepted.\n")
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


@log_start_end(log=logger)
def load_bl_views(excel_file: str = ""):
    """
    Load a Excel file with views for Black Litterman model.

    Parameters
    ----------
    excel_file: str
        The location of the Excel file that needs to be loaded.

    Returns
    -------
    p_views: list
        Returns a list with p_views matrix
    q_views: list
        Returns a list with q_views matrix
    """
    if str(excel_file).endswith(".xlsx"):
        try:
            p_views = pd.read_excel(excel_file, sheet_name="p_views", index_col=0)
            p_views = p_views.fillna(0)
            p_views = p_views.dropna(axis="rows")
        except KeyError:
            console.print("Excel file needs a p_views sheet\n")
            return {}, {}
        try:
            q_views = pd.read_excel(excel_file, sheet_name="q_views", index_col=0)
            q_views = q_views.dropna(axis="rows")
        except KeyError:
            console.print("Excel file needs a p_views sheet\n")
            return {}, {}
    else:
        console.print("Only Excel (.xlsx) files are accepted.\n")
        return {}, {}

    p_views = p_views.T.sort_index()
    p_views = p_views.T.to_csv(index=False, header=0).replace("\n", ";")
    p_views = p_views[:-1]
    p_views = [[float(item) for item in row.split(",")] for row in p_views.split(";")]
    q_views = q_views.to_csv(index=False, header=0).replace("\n", ",")
    q_views = q_views[:-1]
    q_views = [float(item) for item in q_views.split(",")]

    return p_views, q_views


@log_start_end(log=logger)
def excel_bl_views(file: str, stocks: str, n: int = 3):
    """
    Create an Excel file with required format to build n views for Black Litterman cmd.

    Parameters
    ----------
    stocks: str
        List of stocks used to build the Black Litterman model views.
    n: int
        The number of views that will be created.

    Returns
    -------
    file: excel
        Returns a list with ticker symbols
    """
    if len(stocks) < 2:
        console.print("Please have at least 2 loaded tickers to create views.\n")

    p_views = [[""] * len(stocks) for i in range(n)]
    p_views_df = pd.DataFrame(p_views, columns=stocks)

    q_views = [[""] for i in range(n)]
    q_views_df = pd.DataFrame(q_views, columns=["Returns"])

    if file.endswith(".xlsx"):
        pass
    else:
        file += ".xlsx"

    with pd.ExcelWriter(file) as writer:
        p_views_df.to_excel(writer, sheet_name="p_views")
        q_views_df.to_excel(writer, sheet_name="q_views")
