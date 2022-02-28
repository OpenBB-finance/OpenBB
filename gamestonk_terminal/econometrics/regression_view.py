"""Regression View"""
__docformat__ = "numpy"

import os
import logging
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.econometrics import regression_model
from gamestonk_terminal.helper_funcs import (
    print_rich_table,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_dwat(
    dependent_variable: pd.Series, residual: pd.DataFrame, export: str = ""
):
    """Show Durbin-Watson autocorrelation tests

    Parameters
    ----------
    dependent_variable : pd.Series
        The dependent variable.
    residual : OLS Model
        The residual of an OLS model.
    export : str
        Format to export data
    """
    autocorrelation = regression_model.get_dwat(residual)

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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{dependent_variable.name}_dwat",
        autocorrelation,
    )

    console.print("")


@log_start_end(log=logger)
def display_bgod(model: pd.DataFrame, lags: int, export: str = ""):
    """Show Breusch-Godfrey autocorrelation test

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags included.
    export : str
        Format to export data
    """
    (
        lm_stat,
        p_value,
        f_stat,
        fp_value,
    ) = regression_model.get_bgod(model, lags)

    df = pd.DataFrame(
        [lm_stat, p_value, f_stat, fp_value],
        index=["LM-stat", "p-value", "f-stat", "fp-value"],
    )

    print_rich_table(
        df,
        headers=list(["Breusch-Godfrey"]),
        show_index=True,
        title=f"Breusch-Godfrey autocorrelation test [Lags: {lags}]",
    )

    if p_value > 0.05:
        console.print(
            f"The result {round(p_value, 2)} indicates the existence of autocorrelation. Consider re-estimating "
            f"with clustered standard errors and applying the Random Effects or Fixed Effects model."
        )
    else:
        console.print(
            f"The result {round(p_value, 2)} indicates no existence of autocorrelation."
        )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "results_bgod", df)

    console.print("")


@log_start_end(log=logger)
def display_bpag(model: pd.DataFrame, export: str = ""):
    """Show Breusch-Pagan heteroscedasticity test

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
    """
    (
        lm_stat,
        p_value,
        f_stat,
        fp_value,
    ) = regression_model.get_bpag(model)

    df = pd.DataFrame(
        [lm_stat, p_value, f_stat, fp_value],
        index=["lm-stat", "p-value", "f-stat", "fp-value"],
    )

    print_rich_table(
        df,
        headers=list(["Breusch-Pagan"]),
        show_index=True,
        title="Breusch-Pagan heteroscedasticity test",
    )

    if p_value > 0.05:
        console.print(
            f"The result {round(p_value, 2)} indicates the existence of heteroscedasticity. Consider taking the log "
            f"or a rate for the dependent variable."
        )
    else:
        console.print(
            f"The result {round(p_value, 2)} indicates no existence of heteroscedasticity."
        )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "results_bpag", df)

    console.print("")
