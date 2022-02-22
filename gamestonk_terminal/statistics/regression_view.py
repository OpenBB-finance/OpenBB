import os

import pandas as pd
from matplotlib import pyplot as plt

import gamestonk_terminal.statistics
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.statistics.statistics_view import logger
import gamestonk_terminal.statistics.regression_model
from gamestonk_terminal.helper_funcs import (
    print_rich_table,
)


@log_start_end(log=logger)
def display_dwat(
    dependent_variable: pd.Series, residual: pd.DataFrame, export: str = ""
):
    """Show autocorrelation tests

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
    """
    autocorrelation = gamestonk_terminal.statistics.regression_model.get_dwat(residual)

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
        "custom_plot",
    )

    console.print("")


@log_start_end(log=logger)
def display_bgod(model: pd.DataFrame, lags: int, export: str = ""):
    """Show autocorrelation tests

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
    """
    (
        t_stat,
        p_value,
        f_stat,
        fp_value,
    ) = gamestonk_terminal.statistics.regression_model.get_bgod(model, lags)

    if p_value > 0.05:
        console.print(
            f"The result {p_value} indicates the existence of autocorrelation. Consider re-estimating with clustered "
            "standard errors and applying the First Difference model."
        )
    else:
        console.print(
            f"The result {p_value} indicates no existence of autocorrelation. Therefore, a Pooled OLS model can be "
            "used for the statistical analysis."
        )

    df = pd.DataFrame(
        [t_stat, p_value, f_stat, fp_value],
        index=["t-stat", "p-value", "f-stat", "fp-value"],
    )

    print_rich_table(
        df,
        headers=list("Breusch-Godfrey Test"),
        show_index=True,
        title=f"Breusch Godfrey Test Causality [Lags: {lags}]",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "custom_plot",
    )

    console.print("")
