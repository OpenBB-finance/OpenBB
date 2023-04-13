"""Common Model"""
__docformat__ = "numpy"

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import statsmodels.api as sm
from linearmodels.datasets import wage_panel
from pandas import errors

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
DATA_EXAMPLES: Dict[str, str] = {
    "anes96": "American National Election Survey 1996",
    "cancer": "Breast Cancer Data",
    "ccard": "Bill Greene’s credit scoring data.",
    "cancer_china": "Smoking and lung cancer in eight cities in China.",
    "co2": "Mauna Loa Weekly Atmospheric CO2 Data",
    "committee": "First 100 days of the US House of Representatives 1995",
    "copper": "World Copper Market 1951-1975 Dataset",
    "cpunish": "US Capital Punishment dataset.",
    "danish_data": "Danish Money Demand Data",
    "elnino": "El Nino - Sea Surface Temperatures",
    "engel": "Engel (1857) food expenditure data",
    "fair": "Affairs dataset",
    "fertility": "World Bank Fertility Data",
    "grunfeld": "Grunfeld (1950) Investment Data",
    "heart": "Transplant Survival Data",
    "interest_inflation": "(West) German interest and inflation rate 1972-1998",
    "longley": "Longley dataset",
    "macrodata": "United States Macroeconomic data",
    "modechoice": "Travel Mode Choice",
    "nile": "Nile River flows at Ashwan 1871-1970",
    "randhie": "RAND Health Insurance Experiment Data",
    "scotland": "Taxation Powers Vote for the Scottish Parliament 1997",
    "spector": "Spector and Mazzeo (1980) - Program Effectiveness Data",
    "stackloss": "Stack loss data",
    "star98": "Star98 Educational Dataset",
    "statecrim": "Statewide Crime Data 2009",
    "strikes": "U.S. Strike Duration Data",
    "sunspots": "Yearly sunspots data 1700-2008",
    "wage_panel": "Veila and M. Verbeek (1998): Whose Wages Do Unions Raise?",
}

file_types = ["xlsx", "csv"]


@log_start_end(log=logger)
def load(
    file: str,
    sheet_name: Optional[str] = None,
    data_files: Optional[Dict[Any, Any]] = None,
    data_examples: Optional[Dict[Any, Any]] = None,
) -> pd.DataFrame:
    """Load custom file into dataframe.

    Parameters
    ----------
    file: str
        Path to file
    data_files: dict
        Contains all available data files within the Export folder
    data_examples: dict
        Contains all available examples from Statsmodels

    Returns
    -------
    pd.DataFrame
        Dataframe with custom data
    """
    if data_files is None:
        data_files = {}
    if data_examples is None:
        data_examples = DATA_EXAMPLES
    if file in data_examples:
        if file == "wage_panel":
            return wage_panel.load()
        return getattr(sm.datasets, file).load_pandas().data

    full_file = data_files[file] if file in data_files else file

    if not Path(full_file).exists():
        console.print(f"[red]Cannot find the file {full_file}[/red]\n")
        return pd.DataFrame()

    file_type = Path(full_file).suffix

    try:
        if file_type == ".xlsx":
            try:
                data = (
                    pd.read_excel(full_file)
                    if sheet_name is None
                    else pd.read_excel(full_file, sheet_name=sheet_name)
                )
            except ValueError as err:
                console.print(f"[red]{err}[/red]\n")
                return pd.DataFrame()
        elif file_type == ".csv":
            data = pd.read_csv(full_file)
        else:
            console.print(
                f"The file type {file_type} is not supported. Use .xlsx or .csv."
            )
            return pd.DataFrame()
    except errors.ParserError:
        console.print("[red]The given file is not properly formatted.[/red]\b")
        return pd.DataFrame()
    except errors.EmptyDataError:
        console.print("[red]The given file is empty.[/red]\b")
        return pd.DataFrame()

    if data is None:
        return pd.DataFrame()
    if not data.empty:
        data.columns = [x.replace("/", "_") for x in data.columns]
    return data
