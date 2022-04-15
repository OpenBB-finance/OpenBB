"""Excel Model"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_configuration(excel_file: str):
    """
    Load in the Excel file to determine the configuration that needs to be set.

    Parameters
    ----------
    excel_file: str
        The location of the Excel file that needs to be laoded.

    Returns
    -------
    configuration: dictionary
        Returns a dictionary with the configurations set.
    """
    # Read in the Optimization template
    df = pd.read_excel(excel_file, sheet_name="Optimization", skiprows=2, usecols="B:D",
                       names=['Parameter', 'Value', 'Description'], index_col='Parameter')

    # Remove completely empty NaN rows
    cleaned_df = df.dropna(axis='rows', thresh=2)

    # Filter out any general columns
    filtered_df = cleaned_df[cleaned_df['Description'] != "Description"]

    # Convert to Dictionary
    configuration = filtered_df.to_dict()

    return configuration['Value'], configuration['Description']
