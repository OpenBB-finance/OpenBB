"""Quantitative Analysis View"""
__docformat__ = "numpy"

# pylint: disable=C0302


import logging
import os
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from detecta import detect_cusum
from pandas.plotting import register_matplotlib_converters
from scipy import stats
from statsmodels.graphics.gofplots import qqplot

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.common.quantitative_analysis import qa_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


def lambda_color_red(val: Any) -> str:
    """Adds red to dataframe value"""
    if val > 0.05:
        return f"[red]{round(val,4)}[/red]"
    return round(val, 4)


@log_start_end(log=logger)
def display_summary(
    data: pd.DataFrame, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing summary statistics

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to get statistics of
    export : str
        Format to export data
    """
    summary = qa_model.get_summary(data)

    print_rich_table(
        summary,
        headers=list(summary.columns),
        floatfmt=".3f",
        show_index=True,
        title="[bold]Summary Statistics[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        summary,
        sheet_name,
    )


@log_start_end(log=logger)
def display_hist(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    bins: int = 15,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots histogram of data

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to get histogram of the dataframe
    symbol : str
        Name of dataset
    bins : int
        Number of bins in histogram
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.hist(data=df, target="Adj Close")
    """

    data = data[target]

    fig = OpenBBFigure.create_subplots(1, 1, shared_yaxes=False)

    if isinstance(data.index[0], datetime):
        start = data.index[0]
        fig.set_title(
            f"Histogram of {symbol} {target} from {start.strftime('%Y-%m-%d')}"
        )
    else:
        fig.set_title(f"Histogram of {symbol} {target}")

    fig.add_histplot(
        data,
        name=["Univariate distribution", "Marginal distributions"],
        colors=[theme.up_color],
        bins=bins,
        curve="kde",
    )

    fig.update_layout(
        xaxis_title="Value",
        margin=dict(r=40),
        yaxis=dict(title="Proportion", title_standoff=40),
        bargap=0.01,
        bargroupgap=0,
    )
    fig.update_traces(
        selector=dict(type="histogram"),
        marker=dict(
            color=theme.up_color,
            line=dict(color="white", width=2.5),
        ),
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_cdf(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Cumulative Distribution Function

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column
    symbol : str
        Name of dataset
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.cdf(data=df, target="Adj Close")
    """
    data = data[target]
    start = data.index[0]
    cdf = data.value_counts().sort_index().div(len(data)).cumsum()

    minVal = data.values.min()
    q25 = np.quantile(data.values, 0.25)
    medianVal = np.quantile(data.values, 0.5)
    q75 = np.quantile(data.values, 0.75)
    labels = [
        (minVal, q25),
        (0.25, 0.25),
        "Q1",
        (q25, q25),
        (0, 0.25),
        "Q1",
        (minVal, medianVal),
        (0.5, 0.5),
        "Median",
        (medianVal, medianVal),
        (0, 0.5),
        "Median",
        (minVal, q75),
        (0.75, 0.75),
        "Q3",
        (q75, q75),
        (0, 0.75),
        "Q3",
    ]

    fig = OpenBBFigure(xaxis_title=target.title(), yaxis_title="Probability")
    fig.set_title(
        f"Cumulative Distribution Function of {symbol} {target} from {start.strftime('%Y-%m-%d')}"
    )

    fig.add_scatter(
        x=cdf.index,
        y=cdf.values,
        name="Cumulative Distribution Function",
        marker_color=theme.up_color,
        mode="lines",
    )

    for xt, yt, label in zip(labels[::3], labels[1::3], labels[2::3]):
        fig.add_annotation(
            x=minVal + (xt[1] - minVal) / 2,
            y=yt[1] + 0.04,
            text=label,
            font=dict(color=theme.down_color),
        )
        fig.add_shape(
            type="line",
            x0=xt[0],
            y0=yt[0],
            x1=xt[1],
            y1=yt[1],
            line=dict(color=theme.down_color, width=1.5, dash="dash"),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cdf",
        pd.DataFrame(cdf),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_bw(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    yearly: bool = True,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots box and whisker plots

    Parameters
    ----------
    symbol : str
        Name of dataset
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    yearly : bool
        Flag to indicate yearly accumulation
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.bw(data=df, target="Adj Close")
    """
    data = data.copy()
    start = data[target].index[0]

    colors = theme.get_colors()
    color = colors[0]
    pd.options.mode.chained_assignment = None
    data["x_data"] = data[target].index.year if yearly else data[target].index.month
    pd.options.mode.chained_assignment = "warn"

    l_months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig = OpenBBFigure(
        title=(
            f"{['Monthly','Yearly'][yearly]} box plot of {symbol.upper()} "
            f"{target} from {start.strftime('%Y-%m-%d')}"
        ),
        yaxis_title=target,
        xaxis_title=["Monthly", "Yearly"][yearly],
    )

    for i, group in enumerate(data["x_data"].unique()):
        x = group if yearly else l_months[group - 1]
        y = data[data["x_data"] == group][target]

        fig.add_box(
            y=y,
            x=[x] * len(y),
            name=str(x),
            marker=dict(
                color=theme.up_color,
                outliercolor=theme.up_color,
            ),
            fillcolor=colors[i % len(colors)],
            line_color=color,
            boxmean=True,
            whiskerwidth=1,
            boxpoints="suspectedoutliers",
            hoveron="points",
            showlegend=False,
        )

        fig.add_shape(
            type="line",
            x0=x,
            y0=y.min(),
            x1=x,
            y1=y.max(),
            line=dict(color=color, width=1.5, dash="dash"),
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_acf(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    lags: int = 15,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Auto and Partial Auto Correlation of returns and change in returns

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    symbol : str
        Name of dataset
    lags : int
        Max number of lags to look at
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.acf(data=df, target="Adj Close")
    """
    data = data[target]
    start = data.index[0]

    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=2,
        shared_xaxes=False,
        subplot_titles=[
            f"{symbol} Returns Auto-Correlation",
            f"{symbol} Returns Partial Auto-Correlation",
            f"Change in {symbol} Returns Auto-Correlation",
            f"Change in {symbol} Returns Partial Auto-Correlation",
        ],
        vertical_spacing=0.1,
        horizontal_spacing=0.1,
        x_title="Lag",
    ).set_title(title=f"ACF differentials starting from {start.strftime('%Y-%m-%d')}")

    kwargs = dict(marker=dict(color=theme.get_colors()[0]), line=dict(color="white"))
    np_diff = np.diff(data.values)

    # Diff Auto - correlation function for original time series
    fig.add_corr_plot(np_diff, lags, row=1, col=1, **kwargs)  # type: ignore
    # Diff Partial auto - correlation function for original time series
    fig.add_corr_plot(np_diff, lags, row=1, col=2, pacf=True, method="ywm", **kwargs)  # type: ignore
    # Diff Diff Auto-correlation function for original time series
    fig.add_corr_plot(np.diff(np_diff), lags, row=2, col=1, **kwargs)  # type: ignore
    # Diff Diff Partial auto-correlation function for original time series
    fig.add_corr_plot(
        np.diff(np_diff), lags, row=2, col=2, pacf=True, method="ywm", **kwargs  # type: ignore
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_qqplot(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots QQ plot for data against normal quantiles

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    symbol : str
        Stock ticker
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.qqplot(data=df, target="Adj Close")
    """
    # Statsmodels has a UserWarning for marker kwarg-- which we don't use
    warnings.filterwarnings(category=UserWarning, action="ignore")
    data = data[target]

    fig = OpenBBFigure(
        xaxis_title="Theoretical quantiles", yaxis_title="Sample quantiles"
    )
    fig.set_title(title=f"Q-Q plot for {symbol} {target}")

    qqplot_data = (
        qqplot(
            data,
            stats.distributions.norm,
            fit=True,
            line="45",
            color=theme.down_color,
        )
        .gca()
        .lines
    )

    fig.add_scatter(
        x=qqplot_data[0].get_xdata(),
        y=qqplot_data[0].get_ydata(),
        mode="markers",
        showlegend=False,
    )
    fig.add_scatter(
        x=qqplot_data[1].get_xdata(),
        y=qqplot_data[1].get_ydata(),
        mode="lines",
        line_color=theme.up_color,
        showlegend=False,
    )

    plt.close()

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_cusum(
    data: pd.DataFrame,
    target: str,
    threshold: float = 5,
    drift: float = 2.1,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe
    target : str
        Column of data to look at
    threshold : float
        Threshold value
    drift : float
        Drift parameter
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.cusum(data=df, target="Adj Close")
    """
    target_series = data[target].values

    # The code for this plot was adapted from detecta's sources because at the
    # time of writing this detect_cusum had a bug related to external axes support.
    # see https:  // github.com/demotu/detecta/pull/3
    tap, tan = 0, 0
    ta, tai, taf, _ = detect_cusum(
        x=target_series,
        threshold=threshold,
        drift=drift,
        ending=True,
        show=False,
    )
    # Thus some variable names are left unchanged and unreadable...
    gp, gn = np.zeros(target_series.size), np.zeros(target_series.size)
    for i in range(1, target_series.size):
        s = target_series[i] - target_series[i - 1]
        gp[i] = gp[i - 1] + s - drift  # cumulative sum for + change
        gn[i] = gn[i - 1] - s - drift  # cumulative sum for - change
        if gp[i] < 0:
            gp[i], tap = 0, i
        if gn[i] < 0:
            gn[i], tan = 0, i
        if gp[i] > threshold or gn[i] > threshold:  # change detected!
            ta = np.append(ta, i)  # alarm index
            tai = np.append(tai, tap if gp[i] > threshold else tan)  # start
            gp[i], gn[i] = 0, 0  # reset alarm

    fig = OpenBBFigure.create_subplots(
        2,
        1,
        x_title="Data points",
        subplot_titles=[
            "Time series and detected changes "
            + f"(threshold= {threshold:.3g}, drift= {drift:.3g}): N changes = {len(tai)}",
            "Time series of the cumulative sums of positive and negative changes",
        ],
        vertical_spacing=0.1,
    )
    target_series_indexes = range(data[target].size)
    fig.add_scatter(
        x=[*target_series_indexes], y=target_series, showlegend=False, row=1, col=1
    )

    if len(ta):
        fig.add_scatter(
            x=tai,
            y=target_series[tai],
            mode="markers",
            marker=dict(
                color=theme.up_color,
                size=8,
                symbol="triangle-right",
            ),
            name="Start",
            row=1,
            col=1,
        )
        fig.add_scatter(
            x=taf,
            y=target_series[taf],
            mode="markers",
            marker=dict(
                color=theme.down_color,
                size=8,
                symbol="triangle-left",
            ),
            name="Ending",
            row=1,
            col=1,
        )
        fig.add_scatter(
            x=ta,
            y=target_series[ta],
            mode="markers",
            marker=dict(
                color=theme.get_colors()[-1],
                size=5,
                symbol="circle",
                line=dict(
                    color=theme.get_colors()[-2],
                    width=1,
                ),
            ),
            name="Alarm",
            row=1,
            col=1,
        )
    fig.set_yaxis_title("Amplitude", row=1, col=1)

    fig.add_scatter(
        x=[*target_series_indexes],
        y=gp,
        mode="lines",
        name="+",
        row=2,
        col=1,
        line=dict(color=theme.get_colors()[0]),
    )
    fig.add_scatter(
        x=[*target_series_indexes],
        y=gn,
        mode="lines",
        name="-",
        row=2,
        col=1,
        line=dict(color=theme.get_colors()[1]),
    )
    fig.add_hline(threshold, row=2, col=1)
    fig.update_yaxes(
        position=0.0, row=2, col=1, range=[0, max(gp.max(), gn.max(), threshold) * 1.1]
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_seasonal(
    symbol: str,
    data: pd.DataFrame,
    target: str,
    multiplicative: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots seasonal decomposition data

    Parameters
    ----------
    symbol : str
        Name of dataset
    data : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    multiplicative : bool
        Boolean to indicate multiplication instead of addition
    export : str
        Format to export trend and cycle data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    result, cycle, trend = qa_model.get_seasonal_decomposition(data, multiplicative)

    plot_data = data.copy()
    for rmerge, suffix in zip(
        [result.trend, result.seasonal, result.resid, cycle, trend],
        ["_result.trend", "_result.seasonal", "_result.resid", "_cycle", "_trend"],
    ):
        plot_data = pd.merge(
            plot_data,
            rmerge,
            how="outer",
            left_index=True,
            right_index=True,
            suffixes=("", suffix),
        )

    # Multiplicative model
    fig = OpenBBFigure.create_subplots(4, 1, vertical_spacing=0.06)
    fig.set_title(f"{symbol} (Time-Series) {target} seasonal decomposition")
    colors = iter(theme.get_colors())

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target],
        name="Values",
        line_color=next(colors),
        legend="legend",
        row=1,
        col=1,
    )
    for i, (column, name) in enumerate(
        zip(
            [("trend", "trend_cycle"), ("trend_trend", "seasonal")],
            [
                ("Cyclic-Trend", "Cycle component"),
                ("Trend component", "Seasonal effect"),
            ],
        )
    ):
        for j in range(2):
            fig.add_scatter(
                x=plot_data.index,
                y=plot_data[column[j]],
                name=name[j],
                line_color=next(colors) if i != 0 else theme.down_color,
                legend=f"legend{i + 2}",
                row=i + 2,
                col=1,
            )

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data["resid"],
        name="Residuals",
        line_color=next(colors),
        legend="legend4",
        row=4,
        col=1,
    )

    legend_defaults = dict(
        xanchor="left",
        yanchor="top",
        xref="paper",
        yref="paper",
        font=dict(size=13),
        bgcolor="rgba(0, 0, 0, 0.4)",
    )
    fig.update_traces(selector=dict(name="Cyclic-Trend"), line_color=theme.down_color)
    fig.update_traces(
        selector=dict(name="Cycle component"),
        line=dict(color=theme.up_color, dash="dash"),
    )
    fig.update_yaxes(nticks=5)
    fig.update_layout(
        legend=dict(**legend_defaults),
        legend2=dict(x=0.01, y=0.73, **legend_defaults),
        legend3=dict(x=0.01, y=0.46, **legend_defaults),
        legend4=dict(x=0.01, y=0.20, **legend_defaults),
    )

    # From #https:  // otexts.com/fpp2/seasonal-strength.html
    console.print("Time-Series Level is " + str(round(data.mean(), 2)))

    Ft = max(0, 1 - np.var(result.resid)) / np.var(result.trend + result.resid)
    console.print(f"Strength of Trend: {Ft:.4f}")

    Fs = max(
        0,
        1 - np.var(result.resid) / np.var(result.seasonal + result.resid),
    )
    console.print(f"Strength of Seasonality: {Fs:.4f}\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        cycle.join(trend),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_normality(
    data: pd.DataFrame, target: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing normality statistics

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame
    target : str
        Column in data to look at
    export : str
        Format to export data
    """
    data = data[target]
    normal = qa_model.get_normality(data)
    stats1 = normal.copy().T
    stats1.iloc[:, 1] = stats1.iloc[:, 1].apply(lambda x: lambda_color_red(x))

    print_rich_table(
        stats1,
        show_index=True,
        headers=["Statistic", "p-value"],
        floatfmt=".4f",
        title="[bold]Normality Statistics[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "normality",
        normal,
        sheet_name,
    )


@log_start_end(log=logger)
def display_unitroot(
    data: pd.DataFrame,
    target: str,
    fuller_reg: str = "c",
    kpss_reg: str = "c",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Prints table showing unit root test calculations

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    fuller_reg : str
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : str
        Type of regression for KPSS test. Can be ‘c’,’ct'
    export : str
        Format for exporting data
    """
    data = data[target]
    data = qa_model.get_unitroot(data, fuller_reg, kpss_reg)
    print_rich_table(
        data,
        show_index=True,
        headers=list(data.columns),
        title="[bold]Unit Root Calculation[/bold]",
        floatfmt=".4f",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "unitroot",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_raw(
    data: pd.DataFrame,
    sortby: str = "",
    ascend: bool = False,
    limit: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing raw stock data

    Parameters
    ----------
    data : DataFrame
        DataFrame with historical information
    sortby : str
        The column to sort by
    ascend : bool
        Whether to sort descending
    limit : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    """

    df1 = pd.DataFrame(data) if isinstance(data, pd.Series) else data.copy()

    if sortby:
        sortby = sortby.replace("_", " ")
        try:
            sort_col = [x.lower().replace(" ", "") for x in df1.columns].index(
                sortby.lower().replace(" ", "")
            )
        except ValueError:
            console.print("[red]The provided column is not a valid option[/red]\n")
            return
        df1 = df1.sort_values(by=data.columns[sort_col], ascending=ascend)
    else:
        df1 = df1.sort_index(ascending=ascend)

    print_rich_table(
        df1,
        headers=[x.title() if x != "" else "Date" for x in df1.columns],
        title="[bold]Raw Data[/bold]",
        show_index=True,
        floatfmt=".3f",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "raw",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_line(
    data: pd.Series,
    title: str = "",
    log_y: bool = True,
    markers_lines: Optional[List[datetime]] = None,
    markers_scatter: Optional[List[datetime]] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display line plot of data

    Parameters
    ----------
    data: pd.Series
        Data to plot
    title: str
        Title for plot
    log_y: bool
        Flag for showing y on log scale
    markers_lines: Optional[List[datetime]]
        List of dates to highlight using vertical lines
    markers_scatter: Optional[List[datetime]]
        List of dates to highlight using scatter
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.qa.line(data=df["Adj Close"])
    """

    fig = OpenBBFigure(yaxis_title=data.name)

    if log_y:
        fig.add_scatter(
            x=data.index,
            y=data.values,
            name="",
            mode="lines",
            showlegend=False,
        )
        fig.update_layout(yaxis_type="log")

    else:
        fig.add_scatter(
            x=data.index,
            y=data.values,
            name="",
            mode="lines",
            showlegend=False,
        )

        if markers_lines:
            for marker_date in markers_lines:
                fig.add_vline(x=marker_date, line=dict(color=theme.up_color, width=2))

        if markers_scatter:
            scatter: Dict[str, list] = dict(x=[], y=[])
            for n, marker_date in enumerate(markers_scatter):
                price_location_idx = data.index.get_loc(marker_date, method="nearest")
                # algo to improve text placement of highlight event number
                if (
                    price_location_idx > 0
                    and data.iloc[price_location_idx - 1]
                    > data.iloc[price_location_idx]
                ):
                    text_loc = (0, -20)
                else:
                    text_loc = (0, 10)

                fig.add_annotation(
                    x=marker_date,
                    y=data.iloc[price_location_idx],
                    text=str(n + 1),
                    xshift=text_loc[0],
                    yshift=text_loc[1],
                )
                scatter["x"].append(marker_date.strftime("%Y-%m-%d"))
                scatter["y"].append(data.iloc[price_location_idx])

            fig.add_scatter(
                x=scatter["x"],
                y=scatter["y"],
                mode="markers",
                marker=dict(
                    size=12,
                    color=theme.up_color,
                    line=dict(
                        width=2,
                        color=theme.up_color,
                    ),
                ),
            )

    if title:
        fig.set_title(title)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "line",
        sheet_name=sheet_name,
        figure=fig,
    )

    return fig.show(external=external_axes)


def display_var(
    data: pd.DataFrame,
    symbol: str = "",
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
    data_range: int = 0,
    portfolio: bool = False,
) -> None:
    """Prints table showing VaR of dataframe.

    Parameters
    ----------
    data: pd.Dataframe
        Data dataframe
    use_mean: bool
        if one should use the data mean return
    symbol: str
        name of the data
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: int
        var percentile
    data_range: int
        Number of rows you want to use VaR over
    portfolio: bool
        If the data is a portfolio
    """

    if data_range > 0:
        df = qa_model.get_var(
            data[-data_range:], use_mean, adjusted_var, student_t, percentile, portfolio
        )
    else:
        df = qa_model.get_var(
            data, use_mean, adjusted_var, student_t, percentile, portfolio
        )

    if adjusted_var:
        str_title = "Adjusted "
    elif student_t:
        str_title = "Student-t "
    else:
        str_title = ""

    if symbol != "":
        symbol += " "

    print_rich_table(
        df,
        show_index=True,
        headers=list(df.columns),
        title=f"[bold]{symbol}{str_title}Value at Risk[/bold]",
        floatfmt=".2f",
    )


def display_es(
    data: pd.DataFrame,
    symbol: str = "",
    use_mean: bool = False,
    distribution: str = "normal",
    percentile: float = 99.9,
    portfolio: bool = False,
) -> None:
    """Prints table showing expected shortfall.

    Parameters
    ----------
    data: pd.DataFrame
        Data dataframe
    use_mean:
        if one should use the data mean return
    symbol: str
        name of the data
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: int
        es percentile
    portfolio: bool
        If the data is a portfolio
    """
    df = qa_model.get_es(data, use_mean, distribution, percentile, portfolio)

    if distribution == "laplace":
        str_title = "Laplace "
    elif distribution == "student_t":
        str_title = "Student-t "
    elif distribution == "logistic":
        str_title = "Logistic "
    else:
        str_title = ""

    if symbol != "":
        symbol += " "

    print_rich_table(
        df,
        show_index=True,
        headers=list(df.columns),
        title=f"[bold]{symbol}{str_title}Expected Shortfall[/bold]",
        floatfmt=".2f",
    )


def display_sharpe(
    data: pd.DataFrame, rfr: float = 0, window: float = 252, external_axes: bool = False
) -> Union[OpenBBFigure, None]:
    """Plots Calculated the sharpe ratio

    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    sharpe_ratio = qa_model.get_sharpe(data, rfr, window)

    data = sharpe_ratio[int(window - 1) :]

    fig = OpenBBFigure(yaxis_title="Sharpe Ratio", xaxis_title="Date")
    fig.set_title(f"Sharpe Ratio - over a {window} day window")

    fig.add_scatter(x=data.index, y=data)

    return fig.show(external=external_axes)


def display_sortino(
    data: pd.DataFrame,
    target_return: float,
    window: float,
    adjusted: bool,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the sortino ratio

    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    sortino_ratio = qa_model.get_sortino(data, target_return, window, adjusted)
    str_adjusted = "Adjusted " if adjusted else ""

    data = sortino_ratio[int(window - 1) :]

    fig = OpenBBFigure(yaxis_title="Sortino Ratio", xaxis_title="Date")
    fig.set_title(f"{str_adjusted}Sortino Ratio - over a {window} day window")

    fig.add_scatter(x=data.index, y=data)

    return fig.show(external=external_axes)


def display_omega(
    data: pd.DataFrame,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the omega ratio

    Parameters
    ----------
    data: pd.DataFrame
        stock dataframe
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = qa_model.get_omega(data, threshold_start, threshold_end)

    # Plotting
    fig = OpenBBFigure(yaxis_title="Omega Ratio", xaxis_title="Threshold (%)")
    fig.set_title(f"Omega Curve - over last {len(data)}'s period")

    fig.add_scatter(x=df["threshold"], y=df["omega"], name="Omega Curve")

    return fig.show(external=external_axes)
