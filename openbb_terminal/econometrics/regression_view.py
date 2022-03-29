"""Regression View"""
__docformat__ = "numpy"

from typing import Optional, List, Tuple, Dict, Any
import os
import logging
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale, export_data
from openbb_terminal.rich_config import console
from openbb_terminal.econometrics import regression_model
from openbb_terminal.helper_funcs import (
    print_rich_table,
)
from openbb_terminal.config_terminal import theme

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_panel(
    regression_type: str,
    regression_variables: List[Tuple],
    data: Dict[str, pd.DataFrame],
    datasets: Dict[pd.DataFrame, Any],
    entity_effects: bool = False,
    time_effects: bool = False,
    export: str = "",
):
    """Based on the regression type, this function decides what regression to run.

    Parameters
    ----------
    regression_type: str
        The type of regression you wish to execute.
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.
    entity_effects: bool
        Whether to apply Fixed Effects on entities.
    time_effects: bool
        Whether to apply Fixed Effects on time.
    export : str
        Format to export data

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the regression model.
    """
    (
        regression_df,
        dependent,
        independent,
        model,
    ) = regression_model.get_regressions_results(
        regression_type,
        regression_variables,
        data,
        datasets,
        entity_effects,
        time_effects,
    )

    if export:
        results_as_html = model.summary.tables[1].as_html()
        df = pd.read_html(results_as_html, header=0, index_col=0)[0]

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dependent}_{regression_type}_regression",
            df,
        )

    return regression_df, dependent, independent, model


@log_start_end(log=logger)
def display_dwat(
    dependent_variable: pd.Series,
    residual: pd.DataFrame,
    plot: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.axes]] = None,
):
    """Show Durbin-Watson autocorrelation tests

    Parameters
    ----------
    dependent_variable : pd.Series
        The dependent variable.
    residual : OLS Model
        The residual of an OLS model.
    plot : bool
        Whether to plot the residuals
    export : str
        Format to export data
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
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

    if plot:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes[0]

        ax.scatter(dependent_variable, residual)
        ax.axhline(y=0, color="r", linestyle="-")
        ax.set_ylabel("Residual")
        ax.set_xlabel(dependent_variable.name.capitalize())
        ax.set_title("Plot of Residuals")
        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{dependent_variable.name}_dwat",
        autocorrelation,
    )

    console.print()


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

    console.print()


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

    console.print()
