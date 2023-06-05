"""Econometrics View"""
__docformat__ = "numpy"

# pylint: disable=too-many-arguments

import logging
import os
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.econometrics import econometrics_model
from openbb_terminal.econometrics.econometrics_helpers import get_ending
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_options(
    datasets: Dict[str, pd.DataFrame],
    dataset_name: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Plot custom data

    Parameters
    ----------
    datasets: dict
        The loaded in datasets
    dataset_name: str
        The name of the dataset you wish to show options for
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export image
    """
    if not datasets:
        console.print(
            "Please load in a dataset by using the 'load' command before using this feature."
        )
    else:
        option_tables = econometrics_model.get_options(
            datasets, dataset_name if dataset_name is not None else ""
        )

        for dataset, data_values in option_tables.items():
            print_rich_table(
                data_values,
                headers=list(data_values.columns),
                show_index=False,
                title=f"Options for dataset: '{dataset}'",
                export=bool(export),
            )

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{dataset}_options",
                data_values.set_index("column"),
                sheet_name,
            )


@log_start_end(log=logger)
def display_plot(
    data: Union[pd.Series, pd.DataFrame, Dict[str, pd.DataFrame]],
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plot data from a dataset

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame, Dict[str: pd.DataFrame]
        Dictionary with key being dataset.column and dataframes being values
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export image
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure()

    if isinstance(data, pd.Series):
        data = {data.name: data}
    elif isinstance(data, pd.DataFrame):
        data = {x: data[x] for x in data.columns}

    for dataset_col in data:
        if isinstance(data[dataset_col].index, pd.MultiIndex):
            console.print(
                "The index appears to be a multi-index. "
                "Therefore, it is not possible to plot the data."
            )
            del data[dataset_col]

    if not fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "plot",
            sheet_name,
        )

    # Check that there's at least a valid dataframe
    if data:
        for dataset_col in data:
            try:
                if isinstance(data[dataset_col], (pd.Series, pd.DataFrame)):
                    fig.add_scatter(
                        x=data[dataset_col].index,
                        y=data[dataset_col].values,
                        name=dataset_col,
                    )

            except ValueError:
                print(f"Could not convert column: {dataset_col}")
            except TypeError:
                print(f"Could not convert column: {dataset_col}")

        if fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "plot",
                sheet_name=sheet_name,
                figure=fig,
            )

        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_corr(
    dataset: pd.DataFrame,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot correlation coefficients for dataset features

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset fore calculating correlation coefficients
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export image
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure()

    # correlation
    correlation = econometrics_model.get_corr_df(dataset)
    fig.add_heatmap(
        z=correlation,
        x=correlation.columns,
        y=correlation.index,
        zmin=correlation.values.min(),
        zmax=1,
        showscale=True,
        text=correlation,
        texttemplate="%{text:.2f}",
        colorscale="electric",
        colorbar=dict(
            thickness=10,
            thicknessmode="pixels",
            x=1.2,
            y=1,
            xanchor="right",
            yanchor="top",
            xpad=10,
        ),
        xgap=1,
        ygap=1,
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(margin=dict(l=0, r=120, t=0, b=0), title="Correlation Matrix")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
        sheet_name=sheet_name,
        figure=fig,
    )
    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_seasonality(
    data: pd.DataFrame,
    column: str = "close",
    export: str = "",
    sheet_name: Optional[str] = None,
    m: Optional[int] = None,
    max_lag: int = 24,
    alpha: float = 0.05,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot seasonality from a dataset

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to plot
    column: str
        The column of the dataframe to analyze
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export image
    m: Optional[int]
        Optionally, a time lag to highlight on the plot. Default is none.
    max_lag: int
        The maximal lag order to consider. Default is 24.
    alpha: float
        The confidence interval to display. Default is 0.05.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if data.empty:
        return console.print("No data to plot")

    series = data[column]

    ending = get_ending(data.name, column)

    fig = OpenBBFigure()
    fig.set_title(f"Seasonality{ending}", wrap=True, wrap_width=55)
    fig.add_corr_plot(series, m=m, max_lag=max_lag, alpha=alpha)
    fig.update_xaxes(autorange=False, range=[-1, max_lag + 1])
    fig.add_legend_label()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
        sheet_name=sheet_name,
        figure=fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_norm(
    data: pd.Series,
    dataset: str = "",
    column: str = "",
    plot: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Determine the normality of a timeseries.

    Parameters
    ----------
    data: pd.Series
        Series of custom data
    dataset: str
        Dataset name
    column: str
        Column for y data
    plot : bool
        Whether you wish to plot a histogram
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure()

    if data.dtype not in [int, float, np.float64, np.int64]:
        console.print(
            f"The column type must be numeric. The provided column type is {data.dtype}. "
            f"Consider using the command 'type' to change this.\n"
        )
    else:
        results = econometrics_model.get_normality(data)

        ending = get_ending(dataset, column)
        print_rich_table(
            results,
            headers=list(results.columns),
            show_index=True,
            title=f"Normality test{ending}",
            export=bool(export),
        )
        if not fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{column}_{dataset}_norm",
                results,
                sheet_name,
            )

        if plot or fig.is_image_export(export):
            fig.set_title(f"Histogram{ending}", wrap=True, wrap_width=55)

            fig.add_histogram(x=data, name="Histogram", nbinsx=100)

            fig.update_layout(margin=dict(t=65))

            if fig.is_image_export(export):
                export_data(
                    export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{column}_{dataset}_norm",
                    results,
                    sheet_name,
                    fig,
                )

            return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_root(
    data: pd.Series,
    dataset: str = "",
    column: str = "",
    fuller_reg: str = "c",
    kpss_reg: str = "c",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Determine the normality of a timeseries.

    Parameters
    ----------
    data : pd.Series
        Series of target variable
    dataset: str
        Name of the dataset
    column: str
        Name of the column
    fuller_reg : str
        Type of regression of ADF test. Choose c, ct, ctt, or nc
    kpss_reg : str
        Type of regression for KPSS test. Choose c or ct
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data.
    """
    if data.dtype not in [int, float, np.float64, np.int64]:
        console.print(
            f"The column type must be numeric. The provided "
            f"type is {data.dtype}. Consider using the command 'type' to change this.\n"
        )
    else:
        results = econometrics_model.get_root(data, fuller_reg, kpss_reg)

        ending = get_ending(dataset, column)
        print_rich_table(
            results,
            headers=list(results.columns),
            show_index=True,
            title=f"Unitroot {ending}",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dataset}_{column}_root",
            results,
            sheet_name,
        )


@log_start_end(log=logger)
def display_garch(
    dataset: pd.DataFrame,
    column: str,
    p: int = 1,
    o: int = 0,
    q: int = 1,
    mean: str = "constant",
    horizon: int = 1,
    detailed: bool = False,
    export: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the volatility forecasts based on GARCH

    Parameters
    ----------
    dataset: pd.DataFrame
        The dataframe to use
    column: str
        The column of the dataframe to use
    p: int
        Lag order of the symmetric innovation
    o: int
        Lag order of the asymmetric innovation
    q: int
        Lag order of lagged volatility or equivalent
    mean: str
        The name of the mean model
    horizon: int
        The horizon of the forecast
    detailed: bool
        Whether to display the details about the parameter fit, for instance the confidence interval
    export: str
        Format to export data
    external_axes: bool
        Whether to return the figure object or not, by default False
    """
    data = dataset[column]
    result, garch_fit = econometrics_model.get_garch(data, p, o, q, mean, horizon)

    fig = OpenBBFigure()

    fig.add_scatter(x=list(range(1, horizon + 1)), y=result)
    fig.set_title(
        f"{f'GARCH({p}, {o}, {q})' if o != 0 else f'GARCH({p}, {q})'} volatility forecast"
    )

    if fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{column}_{dataset}_GARCH({p},{q})",
            result,
            figure=fig,
        )

    if not detailed:
        print_rich_table(
            garch_fit.params.to_frame(),
            headers=["Values"],
            show_index=True,
            index_name="Parameters",
            title=f"GARCH({p}, {o}, {q})" if o != 0 else f"GARCH({p}, {q})",
            export=bool(export),
        )
    else:
        console.print(garch_fit)
    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_granger(
    dependent_series: pd.Series,
    independent_series: pd.Series,
    lags: int = 3,
    confidence_level: float = 0.05,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show granger tests

    Parameters
    ----------
    dependent_series: Series
        The series you want to test Granger Causality for.
    independent_series: Series
        The series that you want to test whether it Granger-causes dependent_series
    lags : int
        The amount of lags for the Granger test. By default, this is set to 3.
    confidence_level: float
        The confidence level you wish to use. By default, this is set to 0.05.
    export : str
        Format to export data
    """
    if dependent_series.dtype not in [int, float, np.float64, np.int64]:
        console.print(
            f"The time series {dependent_series.name} needs to be numeric but is type "
            f"{dependent_series.dtype}. Consider using the command 'type' to change this."
        )
    elif independent_series.dtype not in [int, float, np.float64, np.int64]:
        console.print(
            f"The time series {independent_series.name} needs to be numeric but is type "
            f"{independent_series.dtype}. Consider using the command 'type' to change this."
        )
    else:
        granger_df = econometrics_model.get_granger_causality(
            dependent_series, independent_series, lags
        )

        print_rich_table(
            granger_df,
            headers=list(granger_df.columns),
            show_index=True,
            title=f"Granger Causality Test [Y: {dependent_series.name} | X: {independent_series.name} | Lags: {lags}]",
            export=bool(export),
        )

        result_ftest = round(granger_df.loc["params_ftest"]["P-value"], 3)

        if result_ftest > confidence_level:
            console.print(
                f"As the p-value of the F-test is {result_ftest}, we can not reject the null hypothesis at "
                f"the {confidence_level} confidence level.\n"
            )
        else:
            console.print(
                f"As the p-value of the F-test is {result_ftest}, we can reject the null hypothesis at "
                f"the {confidence_level} confidence level and find the Series '{independent_series.name}' "
                f"to Granger-cause the Series '{dependent_series.name}'\n"
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f'{dependent_series.name.replace(".","-")}_{independent_series.name.replace(".","-")}_granger',
            granger_df,
            sheet_name,
        )


@log_start_end(log=logger)
def display_cointegration_test(
    *datasets: pd.Series,
    significant: bool = False,
    plot: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Estimates long-run and short-run cointegration relationship for series y and x and apply
    the two-step Engle & Granger test for cointegration.

    Uses a 2-step process to first estimate coefficients for the long-run relationship
        y_t = c + gamma * x_t + z_t

    and then the short-term relationship,
        y_t - y_(t-1) = alpha * z_(t-1) + epsilon_t,

    with z the found residuals of the first equation.

    Then tests co-integration with the Dickey-Fuller phi=1 vs phi < 1 in
        z_t = phi * z_(t-1) + eta_t

    If this implies phi < 1, the z series is stationary is concluded to be
    stationary, and thus the series y and x are concluded to be cointegrated.

    Parameters
    ----------
    datasets: pd.Series
        Variable number of series to test for cointegration
    significant: float
        Show only companies that have p-values lower than this percentage
    plot: bool
        Whether you wish to plot the z-values of all pairs.
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if len(datasets) < 2:
        return console.print(
            "[red]Co-integration requires at least two time series.[/red]"
        )
    fig = OpenBBFigure().set_title("Error correction terms")

    df: pd.DataFrame = econometrics_model.get_coint_df(*datasets)

    if significant:
        console.print(
            f"Only showing pairs that are statistically significant ({significant} > p-value)."
        )
        df = df[significant > df["P Value"]]
        console.print()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        index_name="Pairs",
        title="Cointegration Tests",
        export=bool(export),
    )

    if not fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "coint",
            df,
            sheet_name,
        )
    if plot or fig.is_image_export(export):
        z_values = econometrics_model.get_coint_df(*datasets, return_z=True)

        for pair, values in z_values.items():
            fig.add_scatter(x=values.index, y=values, name=pair, mode="lines")

        if fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "coint",
                df,
                sheet_name,
                fig,
            )

        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_vif(
    dataset: pd.DataFrame,
    columns: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays the VIF (variance inflation factor), which tests for collinearity, values for each column.

    Parameters
    ----------
    dataset: pd.Series
        Dataset to calculate VIF on
    columns: Optional[list]
        The columns to calculate to test for collinearity
    sheet_name: Optional[str]
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data.
    """
    columns = dataset.columns if columns is None else columns
    if any(dataset[column].dtype not in [int, float] for column in columns):
        console.print(
            "All column types must be numeric. Consider using the command 'type' to change this.\n"
        )
    else:
        results = econometrics_model.get_vif(dataset, columns)

        print_rich_table(
            results,
            headers=list(results.columns),
            show_index=True,
            title="Collinearity Test",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dataset}_{','.join(columns)}_vif",
            results,
            sheet_name,
        )
