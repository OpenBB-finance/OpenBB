"""Econometrics View"""
__docformat__ = "numpy"

import logging
import os
from itertools import combinations
from typing import Dict, Optional, List, Union

from matplotlib.units import ConversionError
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.helper_funcs import (
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.econometrics import econometrics_model
from openbb_terminal.config_terminal import theme
from openbb_terminal.econometrics.econometrics_helpers import get_ending

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def show_options(
    datasets: Dict[str, pd.DataFrame],
    dataset_name: str = None,
    export: str = "",
):
    """Plot custom data

    Parameters
    ----------
    datasets: dict
        The loaded in datasets
    dataset_name: str
        The name of the dataset you wish to show options for
    export: str
        Format to export image
    """
    if not datasets:
        console.print(
            "Please load in a dataset by using the 'load' command before using this feature."
        )
    else:
        option_tables = econometrics_model.get_options(datasets, dataset_name)

        for dataset, data_values in option_tables.items():
            print_rich_table(
                data_values,
                headers=list(data_values.columns),
                show_index=False,
                title=f"Options for dataset: '{dataset}'",
            )

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{dataset}_options",
                data_values.set_index("column"),
            )


@log_start_end(log=logger)
def display_plot(
    data: Union[pd.Series, pd.DataFrame, Dict[str, pd.DataFrame]],
    export: str = "",
    external_axes: Optional[List[plt.axes]] = None,
):
    """Plot data from a dataset

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame, Dict[str: pd.DataFrame]
        Dictionary with key being dataset.column and dataframes being values
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    """
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

    # Check that there's at least a valid dataframe
    if data:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes[0]

        for dataset_col in data:
            try:
                if isinstance(data[dataset_col], pd.Series):
                    ax.plot(data[dataset_col].index, data[dataset_col].values)
                elif isinstance(data[dataset_col], pd.DataFrame):
                    ax.plot(data[dataset_col])

            except ConversionError:
                print(f"Could not convert column: {dataset_col}")
            except TypeError:
                print(f"Could not convert column: {dataset_col}")

        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

        ax.legend(list(data.keys()))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
    )


@log_start_end(log=logger)
def display_norm(
    data: pd.Series,
    dataset: str = "",
    column: str = "",
    plot: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.axes]] = None,
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
    export: str
        Format to export data.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    """
    if data.dtype not in [int, float]:
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
        )

        if plot:
            if external_axes is None:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            else:
                ax = external_axes[0]

            ax.hist(data, bins=100)

            ax.set_title(f"Histogram{ending}")

            theme.style_primary_axis(ax)

            if external_axes is None:
                theme.visualize_output()

        if export:
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{column}_{dataset}_norm",
                results,
            )
        else:
            console.print()


@log_start_end(log=logger)
def display_root(
    df: pd.Series,
    dataset: str = "",
    column: str = "",
    fuller_reg: str = "c",
    kpss_reg: str = "c",
    export: str = "",
):
    """Determine the normality of a timeseries.

    Parameters
    ----------
    df : pd.Series
        Series of target variable
    dataset: str
        Name of the dataset
    column: str
        Name of the column
    fuller_reg : str
        Type of regression of ADF test. Choose c, ct, ctt, or nc
    kpss_reg : str
        Type of regression for KPSS test. Choose c or ct
    export: str
        Format to export data.
    """
    if df.dtype not in [int, float]:
        console.print(
            f"The column type must be numeric. The provided "
            f"type is {df.dtype}. Consider using the command 'type' to change this.\n"
        )
    else:
        results = econometrics_model.get_root(df, fuller_reg, kpss_reg)

        ending = get_ending(dataset, column)
        print_rich_table(
            results,
            headers=list(results.columns),
            show_index=True,
            title=f"Unitroot {ending}",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{dataset}_{column}_root",
            results,
        )


@log_start_end(log=logger)
def display_granger(
    dependent_series: pd.Series,
    independent_series: pd.Series,
    lags: int = 3,
    confidence_level: float = 0.05,
    export: str = "",
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
    if dependent_series.dtype not in [int, float]:
        console.print(
            f"The time series {dependent_series.name} needs to be numeric but is type "
            f"{dependent_series.dtype}. Consider using the command 'type' to change this."
        )
    elif independent_series.dtype not in [int, float]:
        console.print(
            f"The time series {independent_series.name} needs to be numeric but is type "
            f"{independent_series.dtype}. Consider using the command 'type' to change this."
        )
    else:
        granger = econometrics_model.get_granger_causality(
            dependent_series, independent_series, lags
        )

        for test in granger[lags][0]:
            # As ssr_chi2test and lrtest have one less value in the tuple, we fill
            # this value with a '-' to allow the conversion to a DataFrame
            if len(granger[lags][0][test]) != 4:
                pars = granger[lags][0][test]
                granger[lags][0][test] = (pars[0], pars[1], "-", pars[2])

        granger_df = pd.DataFrame(
            granger[lags][0], index=["F-test", "P-value", "Count", "Lags"]
        ).T

        print_rich_table(
            granger_df,
            headers=list(granger_df.columns),
            show_index=True,
            title=f"Granger Causality Test [Y: {dependent_series.name} | X: {independent_series.name} | Lags: {lags}]",
        )

        result_ftest = round(granger[lags][0]["params_ftest"][1], 3)

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
        )


@log_start_end(log=logger)
def display_cointegration_test(
    datasets: Union[pd.DataFrame, Dict[str, pd.Series]],
    significant: bool = False,
    plot: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.axes]] = None,
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
    datasets: Union[pd.DataFrame, Dict[str, pd.Series]]
        All time series to perform co-integration tests on.
    significant: float
        Show only companies that have p-values lower than this percentage
    plot: bool
        Whether you wish to plot the z-values of all pairs.
    export : str
        Format to export data
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    """

    if isinstance(datasets, pd.DataFrame):
        new_datasets = {}
        for column in datasets.columns:
            new_datasets[column] = datasets[column]

    pairs = list(combinations(datasets.keys(), 2))
    result: Dict[str, list] = {}
    z_values: Dict[str, pd.Series] = {}

    for x, y in pairs:
        if sum(datasets[y].isnull()) > 0:
            console.print(
                f"The Series {y} has nan-values. Please consider dropping or filling these "
                f"values with 'clean'."
            )
        elif sum(datasets[x].isnull()) > 0:
            console.print(
                f"The Series {x} has nan-values. Please consider dropping or filling these "
                f"values with 'clean'."
            )
        elif not datasets[y].index.equals(datasets[x].index):
            console.print(f"The Series {y} and {x} do not have the same index.")
        else:
            try:
                (
                    c,
                    gamma,
                    alpha,
                    z,
                    adfstat,
                    pvalue,
                ) = econometrics_model.get_engle_granger_two_step_cointegration_test(
                    datasets[x], datasets[y]
                )
                result[f"{x}/{y}"] = [c, gamma, alpha, adfstat, pvalue]
                z_values[f"{x}/{y}"] = z
            except ValueError:
                console.print(
                    "[red]Error: please only send string and integer columns[/red]\n"
                )

    if result and z_values:
        df = pd.DataFrame.from_dict(
            result,
            orient="index",
            columns=["Constant", "Gamma", "Alpha", "Dickey-Fuller", "P Value"],
        )

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
        )

        if plot:
            if external_axes is None:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            else:
                ax = external_axes[0]

            for pair, values in z_values.items():
                ax.plot(values, label=pair)

            ax.legend()
            ax.set_title("Error correction terms")

            theme.style_primary_axis(ax)

            if external_axes is None:
                theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "coint",
            df,
        )
