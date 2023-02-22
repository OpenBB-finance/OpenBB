"""Regression View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd
import statsmodels

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.econometrics import regression_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_panel(
    Y: pd.DataFrame,
    X: pd.DataFrame,
    regression_type: str = "OLS",
    entity_effects: bool = False,
    time_effects: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Based on the regression type, this function decides what regression to run.

    Parameters
    ----------
    data : dict
        A dictionary containing the datasets.
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
        each column/dataset combination.
    regression_type: str
        The type of regression you wish to execute. Choose from:
        OLS, POLS, RE, BOLS, FE
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
    model = regression_model.get_regressions_results(
        Y,
        X,
        regression_type,
        entity_effects,
        time_effects,
    )
    if regression_type != "OLS":
        console.print(model)

    if export:
        results_as_html = model.summary.tables[1].as_html()
        df = pd.read_html(results_as_html, header=0, index_col=0)[0]
        dependent = Y.columns[0]
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dependent}_{regression_type}_regression",
            df,
            sheet_name,
        )

    return model


@log_start_end(log=logger)
def display_dwat(
    model: statsmodels.regression.linear_model.RegressionResultsWrapper,
    dependent_variable: pd.Series,
    plot: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Show Durbin-Watson autocorrelation tests

    Parameters
    ----------
    model : OLS Model
        A fit statsmodels OLS model.
    dependent_variable : pd.Series
        The dependent variable for plotting
    plot : bool
        Whether to plot the residuals
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure(
        yaxis_title="Residual", xaxis_title=dependent_variable.name.capitalize()
    )
    autocorr = regression_model.get_dwat(model)

    if 1.5 < autocorr < 2.5:
        console.print(
            f"The result {autocorr} is within the range 1.5 and 2.5 which therefore indicates "
            f"autocorrelation not to be problematic."
        )
    else:
        console.print(
            f"The result {autocorr} is outside the range 1.5 and 2.5 and could "
            f"be problematic. Please consider lags of the dependent or independent variable."
        )

    if not fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dependent_variable.name}_dwat",
            autocorr,
            sheet_name,
        )

    if plot or fig.is_image_export(export):
        fig.set_title("Plot of Residuals")

        fig.add_scatter(
            x=dependent_variable,
            y=model.resid,
            mode="markers",
        )
        fig.add_hline(y=0, line=dict(color="red", dash="dash"))

        if fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{dependent_variable.name}_residuals",
                dependent_variable,
                sheet_name,
                fig,
            )

        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_bgod(
    model: statsmodels.regression.linear_model.RegressionResultsWrapper,
    lags: int = 3,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show Breusch-Godfrey autocorrelation test

    Parameters
    ----------
    model : OLS Model
        OLS model that has been fit.
    lags : int
        The amount of lags included.
    export : str
        Format to export data
    """
    df = regression_model.get_bgod(model, lags)

    print_rich_table(
        df,
        headers=list(["Breusch-Godfrey"]),
        show_index=True,
        title=f"Breusch-Godfrey autocorrelation test [Lags: {lags}]",
        export=bool(export),
    )
    p_value = df.loc["p-value"][0]
    if p_value > 0.05:
        console.print(
            f"{round(p_value, 2)} indicates the autocorrelation. Consider re-estimating with "
            "clustered standard errors and applying the Random Effects or Fixed Effects model."
        )
    else:
        console.print(
            f"The result {round(p_value, 2)} indicates no existence of autocorrelation."
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "results_bgod",
        df,
        sheet_name,
    )

    console.print()


@log_start_end(log=logger)
def display_bpag(
    model: statsmodels.regression.linear_model.RegressionResultsWrapper,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show Breusch-Pagan heteroscedasticity test

    Parameters
    ----------
    model : OLS Model
        OLS model that has been fit.
    export : str
        Format to export data
    """
    df = regression_model.get_bpag(model)

    print_rich_table(
        df,
        headers=list(["Breusch-Pagan"]),
        show_index=True,
        title="Breusch-Pagan heteroscedasticity test",
        export=bool(export),
    )
    p_value = df.loc["p-value"][0]
    if p_value > 0.05:
        console.print(
            f"{round(p_value, 2)} indicates heteroscedasticity. Consider taking the log "
            f"or a rate for the dependent variable."
        )
    else:
        console.print(
            f"The result {round(p_value, 2)} indicates no existence of heteroscedasticity."
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "results_bpag",
        df,
        sheet_name,
    )

    console.print()
