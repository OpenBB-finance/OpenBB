"""Statistics Controller View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.statistics import statistics_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def custom_plot(
    data: pd.DataFrame,
    dataset: str,
    column: str,
    export: str = "",
):
    """Plot custom data

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of custom data
    dataset: str
        Dataset name
    column: str
        Column for y data
    kind : str
        Kind of plot to pass to pandas plot function
    export: str
        Format to export image
    """
    plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if isinstance(data, pd.Series):
        plt.plot(data)
    elif isinstance(data, pd.DataFrame):
        plt.plot(data[column])

    plt.title(f"{column} data from dataset {dataset}")
    if gtff.USE_ION:
        plt.ion()
    plt.tight_layout()
    plt.show()
    console.print()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "custom_plot",
    )


@log_start_end(log=logger)
def display_auto(dependent_variable: pd.Series, residual: pd.DataFrame):
    """Show autocorrelation tests

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
    """
    autocorrelation = statistics_model.get_autocorrelation(residual)

    if 1.5 < autocorrelation < 2.5:
        console.print(
            f"The result {autocorrelation} is within the range 1.5 and 2.5 which therefore indicates "
            f"autocorrelation not to be problematic."
        )
    else:
        console.print(
            f"The result {autocorrelation} is outside the range 1.5 and 2.5 and therefore autocorrelation "
            f"can be problematic. Please consider lags of the dependent or independent variable."
        )

    plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plt.scatter(dependent_variable, residual)
    plt.axhline(y=0, color="r", linestyle="-")
    plt.ylabel("Residual")
    plt.xlabel(dependent_variable.name.capitalize())
    plt.title("Plot of Residuals")

    console.print("")
