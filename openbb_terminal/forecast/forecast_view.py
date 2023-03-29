"""Forecast View"""
__docformat__ = "numpy"

import logging
import os
from typing import Dict, List, Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import forecast_model, helpers
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
        option_tables = forecast_model.get_options(datasets, dataset_name)

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
    data: pd.DataFrame,
    columns: List[str],
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot data from a dataset
    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to plot
    columns: List[str]
        The columns to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export image
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    # Check that there's at least a valid dataframe
    if data.empty:
        return console.print("No data to plot")

    # Only do if data is not plotted, otherwise an error will occur
    if "date" in data.columns and "date" not in columns:
        data = data.set_index("date")

    fig = OpenBBFigure()
    for column in columns:
        fig.add_scatter(x=data.index, y=data[column], name=column)

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

    _, series = helpers.get_series(data, column)

    # TODO: Add darts check_seasonality here
    fig = OpenBBFigure()
    fig.add_corr_plot(series.values(), m=m, max_lag=max_lag, alpha=alpha)

    fig.update_xaxes(autorange=False, range=[-1, max_lag + 1])

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
        sheet_name=sheet_name,
        figure=fig,
    )

    return fig.show(external=external_axes)


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
    correlation = forecast_model.corr_df(dataset)
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
def show_df(
    data: pd.DataFrame,
    limit: int = 15,
    limit_col: int = 10,
    name: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show a dataframe in a table

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to show
    limit: int
        The number of rows to show
    limit_col: int
        The number of columns to show
    name: str
        The name of the dataframe
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    """
    console.print(
        f"[green]{name} dataset has shape (row, column): {data.shape}\n[/green]"
    )
    if len(data.columns) > limit_col:
        console.print(
            f"[red]Dataframe has more than {limit_col} columns."
            " If you have extra screen space, consider increasing the `limit_col`,"
            " else export to see all of the data.[/red]\n"
        )
        data = data.iloc[:, :limit_col]
    print_rich_table(
        data,
        headers=list(data.columns),
        show_index=True,
        title=f"Dataset {name} | Showing {limit} of {len(data)} rows",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{name}_show",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def describe_df(
    data: pd.DataFrame,
    name: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show descriptive statistics for a dataframe

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to show
    name: str
        The name of the dataframe
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    """
    new_df = forecast_model.describe_df(data)
    print_rich_table(
        new_df,
        headers=list(data.describe().columns),
        show_index=True,
        title=f"Showing Descriptive Statistics for Dataset {name}",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{name}_show",
        sheet_name,
    )


@log_start_end(log=logger)
def export_df(
    data: pd.DataFrame, export: str, name: str = "", sheet_name: Optional[str] = None
) -> None:
    """Export a dataframe to a file

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to export
    export: str
        The format to export the dataframe to
    name: str
        The name of the dataframe
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    """

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{name}_show",
        data,
        sheet_name,
    )
