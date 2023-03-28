"""Covid View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.alternative.covid import covid_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_covid_ov(
    country: str,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots historical cases and deaths by country.

    Parameters
    ----------
    country: str
        Country to plot
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    cases = covid_model.get_global_cases(country) / 1_000
    deaths = covid_model.get_global_deaths(country)
    if cases.empty or deaths.empty:
        return None
    ov = pd.concat([cases, deaths], axis=1)
    ov.columns = ["Cases", "Deaths"]

    fig = OpenBBFigure.create_subplots(
        specs=[[{"secondary_y": True}]], horizontal_spacing=0.0
    )

    fig.add_scatter(
        x=cases.index,
        y=cases[country].values,
        name="Cases",
        opacity=0.2,
        line_color=theme.up_color,
        showlegend=False,
        secondary_y=False,
    )
    fig.add_scatter(
        x=cases.index,
        y=cases[country].rolling(7).mean().values,
        name="Cases (7d avg)",
        line_color=theme.up_color,
        hovertemplate="%{y:.2f}",
        secondary_y=False,
    )
    fig.add_scatter(
        x=deaths.index,
        y=deaths[country].values,
        name="Deaths",
        opacity=0.2,
        yaxis="y2",
        line_color=theme.down_color,
        showlegend=False,
        secondary_y=True,
    )
    fig.add_scatter(
        x=deaths.index,
        y=deaths[country].rolling(7).mean().values,
        name="Deaths (7d avg)",
        yaxis="y2",
        line_color=theme.down_color,
        hovertemplate="%{y:.2f}",
        secondary_y=True,
    )
    fig.update_layout(
        margin=dict(t=20),
        title=f"Overview for {country.upper()}",
        xaxis_title="Date",
        yaxis=dict(
            title="Cases [1k]",
            side="left",
        ),
        yaxis2=dict(
            title="Deaths",
            side="right",
            overlaying="y",
            showgrid=False,
        ),
        hovermode="x unified",
    )

    return fig.show(external=external_axes, cmd_xshift=-10)


def plot_covid_stat(
    country: str,
    stat: str = "cases",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots historical stat by country.

    Parameters
    ----------
    country: str
        Country to plot
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure(title=f"{country} COVID {stat}", xaxis_title="Date")

    if stat == "cases":
        data = covid_model.get_global_cases(country) / 1_000
        fig.set_yaxis_title(f"{stat.title()} [1k]")
        color = theme.up_color
    elif stat == "deaths":
        data = covid_model.get_global_deaths(country)
        fig.set_yaxis_title(stat.title())
        color = theme.down_color
    elif stat == "rates":
        cases = covid_model.get_global_cases(country)
        deaths = covid_model.get_global_deaths(country)
        data = (deaths / cases).fillna(0) * 100
        color = theme.get_colors(reverse=True)[0]
        fig.set_yaxis_title(f"{stat.title()} (Deaths/Cases)")
    else:
        return console.print("Invalid stat selected.\n")

    fig.add_scatter(
        x=data.index,
        y=data[country].values,
        name=stat.title(),
        opacity=0.2,
        line_color=color,
        showlegend=False,
    )
    fig.add_scatter(
        x=data.index,
        y=data[country].rolling(7).mean().values,
        name=f"{stat.title()} (7d avg)",
        line_color=color,
        hovertemplate="%{y:.2f}",
    )

    fig.update_layout(hovermode="x unified")

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_covid_ov(
    country: str,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    plot: bool = True,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Prints table showing historical cases and deaths by country.

    Parameters
    ----------
    country: str
        Country to get data for
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    plot: bool
        Flag to display historical plot
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure()

    if country.lower() == "us":
        country = "US"
    if plot or fig.is_image_export(export):
        fig = plot_covid_ov(country, external_axes=True)
    if raw:
        data = covid_model.get_covid_ov(country)
        print_rich_table(
            data,
            headers=[x.title() for x in data.columns],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID Numbers[/bold]",
            export=bool(export),
            limit=limit,
        )

    if export:
        data = covid_model.get_covid_ov(country)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ov",
            data,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_covid_stat(
    country: str,
    stat: str = "cases",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    plot: bool = True,
) -> Union[OpenBBFigure, None]:
    """Prints table showing historical cases and deaths by country.

    Parameters
    ----------
    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    plot : bool
        Flag to plot data
    """
    fig = OpenBBFigure()
    data = covid_model.get_covid_stat(country, stat)

    if plot or fig.is_image_export(export):
        fig = plot_covid_stat(country, stat, external_axes=True)  # type: ignore

    if raw:
        print_rich_table(
            data,
            headers=[stat.title()],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID {stat}[/bold]",
            export=bool(export),
            limit=limit,
        )
    if export:
        data["date"] = data.index
        data = data.reset_index(drop=True)
        # make sure date is first column in export
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            stat,
            data,
            sheet_name,
            fig,
        )

    return fig.show(external=raw)


@log_start_end(log=logger)
def display_case_slopes(
    days_back: int = 30,
    limit: int = 10,
    threshold: int = 10000,
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing countries with the highest case slopes.

    Parameters
    ----------
    days_back: int
        Number of historical days to get slope for
    limit: int
        Number to show in table
    ascend: bool
        Flag to sort in ascending order
    threshold: int
        Threshold for total cases over period
    export : str
        Format to export data
    """
    data = covid_model.get_case_slopes(days_back, threshold, ascend)

    print_rich_table(
        data,
        show_index=True,
        index_name="Country",
        title=f"[bold]{('Highest','Lowest')[ascend]} Sloping Cases[/bold] (Cases/Day)",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"slopes_{days_back}day",
        data,
        sheet_name,
    )
