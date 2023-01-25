import json
import os
from math import floor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pandas.tseries.holiday import USFederalHolidayCalendar
from plotly.figure_factory import create_distplot
from plotly.subplots import make_subplots

from openbb_terminal.base_helpers import console, strtobool
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    USER_DATA_DIRECTORY,
)
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.plots.config.openbb_styles import (
    PLT_COLORWAY,
    PLT_DECREASING_COLORWAY,
    PLT_INCREASING_COLORWAY,
    PLT_TBL_ROW_COLORS,
)


class TerminalStyle:
    """The class that helps with handling of style configurations.

    It serves styles for 2 libraries. For `Plotly` this class serves absolute paths
    to the .pltstyle files. For `Plotly` and `Rich` this class serves custom
    styles as python dictionaries.
    """

    DEFAULT_STYLES_LOCATION = MISCELLANEOUS_DIRECTORY / "styles" / "default"
    USER_STYLES_LOCATION = USER_DATA_DIRECTORY / "styles" / "user"

    plt_styles_available: Dict[str, Path] = {}
    plt_style: str = "dark"
    plotly_template: Dict[str, Any] = {}

    console_styles_available: Dict[str, Path] = {}
    console_style: Dict[str, Any] = {}

    line_color: str = ""
    up_color: str = ""
    down_color: str = ""
    up_colorway: List[str] = []
    down_colorway: List[str] = []

    line_width: float = 1.5

    def __init__(
        self,
        plt_style: Optional[str] = "",
        console_style: Optional[str] = "",
    ):
        """Initialize the class

        Parameters
        ----------
        plt_style : `str`, optional
            The name of the Plotly style to use, by default ""
        console_style : `str`, optional
            The name of the Rich style to use, by default ""
        """
        self.plt_style = plt_style or self.plt_style
        self.console_style = console_style
        self.load_available_styles()
        self.load_style()

    def apply_style(self) -> None:
        """Apply the style to the libraries."""
        if self.plt_style and self.plotly_template:
            pio.templates["openbb"] = go.layout.Template(self.plotly_template)
            style = (
                "plotly_white" if self.plt_style == "light" else "plotly_dark+openbb"
            )
            pio.templates.default = style

    def load_available_styles_from_folder(self, folder: Path) -> None:
        """Load custom styles from folder.

        Parses the styles/default and styles/user folders and loads style files.
        To be recognized files need to follow a naming convention:
        *.pltstyle        - plotly stylesheets
        *.richstyle.json  - rich stylesheets

        Parameters
        ----------
        folder : str
            Path to the folder containing the stylesheets
        """
        if not folder.exists():
            return

        for file in folder.glob("*.pltstyle.json"):
            self.plt_styles_available[file.name.replace(".pltstyle.json", "")] = file

    def load_available_styles(self) -> None:
        """Load custom styles from default and user folders."""
        self.load_available_styles_from_folder(self.DEFAULT_STYLES_LOCATION)
        self.load_available_styles_from_folder(self.USER_STYLES_LOCATION)

    def load_json_style(self, file: Path) -> None:
        """Load style from json file.

        Parameters
        ----------
        file : str
            Path to the file containing the style
        """

        with open(file) as f:
            self.plotly_template = json.load(f)

    def load_style(self, style: str = "") -> None:
        """Load style from file.

        Parameters
        ----------
        style : str
            Name of the style to load
        """
        if not style:
            style = self.plt_style

        if style in self.plt_styles_available:
            self.load_plt_style(style)

    def load_plt_style(self, style: str) -> None:
        """Load Plotly style from file.

        Parameters
        ----------
        style : str
            Name of the style to load
        """
        self.plt_style = style
        self.load_json_style(self.plt_styles_available[style])
        line = self.plotly_template.pop("line", {})

        self.up_color = line.get("up_color", "#00ACFF")
        self.down_color = line.get("down_color", "#FF0000")
        self.line_color = line.get("color", "#ffed00")
        self.line_width = line.get("width", self.line_width)
        self.down_colorway = line.get("down_colorway", PLT_DECREASING_COLORWAY)
        self.up_colorway = line.get("up_colorway", PLT_INCREASING_COLORWAY)

    def get_colors(self, reverse: bool = False) -> list:
        """Get colors for the plot.

        Parameters
        ----------
        reverse : bool, optional
            Whether to reverse the colors, by default False

        Returns
        -------
        list
            List of colors
        """
        colors = self.plotly_template.get("layout", {}).get("colorway", PLT_COLORWAY)
        if reverse:
            colors.reverse()
        return colors


theme = TerminalStyle("dark", "dark")
theme.apply_style()


# pylint: disable=R0913
class OpenBBFigure(go.Figure):
    """Custom Figure class for OpenBB Terminal

    Parameters
    ----------
    fig : `go.Figure`, optional
        Figure to copy, by default None
    has_subplots : `bool`, optional
        Whether the figure has subplots, by default False
    **kwargs
        Keyword arguments to pass to `go.Figure.update_layout`

    Class Methods
    -------------
    create_subplots(rows: `int`, cols: `int`, **kwargs) -> `OpenBBFigure`
        Creates a subplots figure
    to_table(df: `pd.DataFrame`, columnwidth: `list`, print_index: `bool`, ...)
        Converts a DataFrame to a table figure

    Methods
    -------
    add_hline_legend(y: `float`, name: `str`, line: `dict`, legendrank: `int`, **kwargs)
        Adds a horizontal line with a legend label
    add_vline_legend(x: `float`, name: `str`, line: `dict`, legendrank: `int`, **kwargs)
        Adds a vertical line with a legend label
    add_legend_label(trace: `str`, label: `str`, mode: `str`, marker: `dict`, **kwargs)
        Adds a legend label
    add_histplot(x: `list`, name: `str`, colors: `list`, bins: `int`, show_curve: `str`, ...)
        Adds a histogram plot
    horizontal_legend(x: `float`, y: `float`, xanchor: `str`, yanchor: `str`, ...)
        Moves the legend to a horizontal position
    to_subplot(subplot: `OpenBBFigure`, row: `int`, col: `int`, secondary_y: `bool`, ...)
        Returns the figure as a subplot of another figure
    """

    def __init__(self, fig: go.Figure = None, **kwargs) -> None:
        super().__init__()
        if fig:
            self.__dict__ = fig.__dict__

        self._has_secondary_y = kwargs.pop("has_secondary_y", False)

        if xaxis := kwargs.pop("xaxis", None):
            self.update_xaxes(xaxis)
        if yaxis := kwargs.pop("yaxis", None):
            self.update_yaxes(yaxis)

        if plots_backend().isatty:
            self.update_layout(
                margin=dict(l=0, r=0, t=0, b=0, pad=0, autoexpand=True),
                height=762,
                width=1400,
                **kwargs,
            )

    @property
    def has_subplots(self):
        return self._has_subplots()

    @classmethod
    def create_subplots(
        cls,
        rows: int = 1,
        cols: int = 1,
        shared_xaxes: bool = True,
        vertical_spacing: float = None,
        horizontal_spacing: float = None,
        subplot_titles: Union[List[str], tuple] = None,
        row_width: List[Union[float, int]] = None,
        specs: List[List[Dict[Any, Any]]] = None,
        **kwargs,
    ) -> "OpenBBFigure":
        """Create a new Plotly figure with subplots

        Parameters
        ----------
        rows : `int`, optional
            Number of rows, by default 1
        cols : `int`, optional
            Number of columns, by default 1
        shared_xaxes : `bool`, optional
            Whether to share x axes, by default True
        vertical_spacing : `float`, optional
            Vertical spacing between subplots, by default None
        horizontal_spacing : `float`, optional
            Horizontal spacing between subplots, by default None
        subplot_titles : `Union[List[str], tuple]`, optional
            Titles for each subplot, by default None
        row_width : `List[Union[float, int]]`, optional
            Width of each row, by default [1]
        specs : `List[List[dict]]`, optional
            Subplot specs, by default `[[{}] * cols] * rows` (all subplots are the same size)
        """

        fig = make_subplots(
            rows=rows,
            cols=cols,
            shared_xaxes=shared_xaxes,
            vertical_spacing=vertical_spacing,
            horizontal_spacing=horizontal_spacing,
            subplot_titles=subplot_titles,
            row_width=row_width or [1] * rows,
            specs=specs or [[{}] * cols] * rows,
            **kwargs,
        )
        kwargs = {}
        if specs and any(
            spec.get("secondary_y", False) for row in specs for spec in row if spec
        ):
            kwargs["has_secondary_y"] = True

        return cls(fig, **kwargs)

    def add_histplot(
        self,
        x: Union[List[List[float]], np.ndarray, pd.Series],
        name: Union[str, List[str]] = None,
        colors: List[str] = None,
        bins: Union[int, str] = "auto",
        show_curve: bool = True,
        show_rug: bool = True,
        show_hist: bool = True,
        row: int = None,
        col: int = None,
        secondary_y: bool = None,
    ) -> None:
        """Add a histogram plot to the figure

        Parameters
        ----------
        x : `Union[List[List[float]], np.ndarray, pd.Series]`
            Data to plot
        name : `Union[str, List[str]]`, optional
            Name of the plot, by default None
        colors : `List[str]`, optional
            Colors of the plot, by default None
        bins : `Union[int, str]`, optional
            Number of bins or bin size, by default "auto"
        show_curve : `str`, optional
            Whether to show the curve, by default "kde"
        show_rug : `bool`, optional
            Whether to show the rug, by default False
        show_hist : `bool`, optional
            Whether to show the histogram, by default True
        row : `int`, optional
            Row of the subplot, by default None
        col : `int`, optional
            Column of the subplot, by default None
        secondary_y : `bool`, optional
            Whether to plot on the secondary y axis, by default None
        """

        fig = create_distplot(
            [x] if not isinstance(x, list) else x,
            [name] if not isinstance(name, list) else name,
            colors=colors,
            bin_size=bins,
            show_rug=show_rug,
            show_hist=show_hist,
            show_curve=show_curve,
            histnorm="probability",
            curve_type="kde",
        )

        for trace in fig.select_traces():
            if trace.type == "scatter":
                trace.showlegend = False
            self.add_trace(trace, row=row, col=col, secondary_y=secondary_y)

    def set_title(self, title: str, **kwargs) -> "OpenBBFigure":
        """Sets the main title of the figure

        Parameters
        ----------
        title : `str`
            Title of the figure
        """
        self.update_layout(title=title, **kwargs)
        return self

    def set_xaxis_title(
        self, title: str, row: int = None, col: int = None, **kwargs
    ) -> "OpenBBFigure":
        """Set the x axis title of the figure or subplot (if row and col are specified)

        Parameters
        ----------
        title : `str`
            Title of the x axis
        row : `int`, optional
            Row number, by default None
        col : `int`, optional
            Column number, by default None
        """
        self.update_xaxes(title=title, row=row, col=col, **kwargs)
        return self

    def set_yaxis_title(
        self, title: str, row: int = None, col: int = None, **kwargs
    ) -> "OpenBBFigure":
        """Set the y axis title of the figure or subplot (if row and col are specified)

        Parameters
        ----------
        title : `str`
            Title of the x axis
        row : `int`, optional
            Row number, by default None
        col : `int`, optional
            Column number, by default None
        """
        self.update_yaxes(title=title, row=row, col=col, **kwargs)
        return self

    def xaxis_type(
        self, xaxis_type: str = "category", row: int = None, col: int = None
    ) -> None:
        """Set the xaxis type of the figure or subplot (if row and col are specified)

        Parameters
        ----------
        xaxis_type : `str`, optional
            Type of xaxis, by default "category"
        row : `int`, optional
            Row number, by default None
        col : `int`, optional
            Column number, by default None
        """
        self.update_xaxes(type=xaxis_type, row=row, col=col)

    def add_hline_legend(
        self,
        y: float,
        name: str,
        line: dict,
        legendrank: int = None,
        **kwargs,
    ) -> None:
        """Add a horizontal line with a legend label

        Parameters
        ----------
        y : `float`
            y value of the line
        name : `str`
            Name of the to display in the legend
        line : `dict`
            Line style
        legendrank : `int`, optional
            Legend rank, by default None (e.g. 1 is above 2)
        """
        self.add_hline(
            y,
            line=line,
        )
        self.add_legend_label(
            label=name,
            mode="lines",
            line_dash=line["dash"],
            marker=dict(color=line["color"]),
            legendrank=legendrank,
            **kwargs,
        )

    def add_vline_legend(
        self,
        x: float,
        name: str,
        line: dict,
        legendrank: int = None,
        **kwargs,
    ) -> None:
        """Add a vertical line with a legend label

        Parameters
        ----------
        x : `float`
            x value of the line
        name : `str`
            Name of the to display in the legend
        line : `dict`
            Line style
        legendrank : `int`, optional
            Legend rank, by default None (e.g. 1 is above 2)
        """
        self.add_vline(
            x,
            line=line,
        )
        self.add_legend_label(
            label=name,
            mode="lines",
            line_dash=line["dash"],
            marker=dict(color=line["color"]),
            legendrank=legendrank,
            **kwargs,
        )

    def horizontal_legend(
        self,
        x: float = 1,
        y: float = 1.02,
        xanchor: str = "right",
        yanchor: str = "bottom",
        orientation: str = "h",
        **kwargs,
    ) -> None:
        """Set the legend to be horizontal

        Parameters
        ----------
        x : `float`, optional
            The x position of the legend, by default 1
        y : `float`, optional
            The y position of the legend, by default 1.02
        xanchor : `str`, optional
            The x anchor of the legend, by default "right"
        yanchor : `str`, optional
            The y anchor of the legend, by default "bottom"
        orientation : `str`, optional
            The orientation of the legend, by default "h"
        """
        self.update_layout(
            legend=dict(
                x=x,
                y=y,
                xanchor=xanchor,
                yanchor=yanchor,
                orientation=orientation,
                **kwargs,
            )
        )

    def add_legend_label(
        self,
        trace: str = None,
        label: str = None,
        mode: str = None,
        marker: dict = None,
        line_dash: str = None,
        legendrank: int = None,
        **kwargs,
    ) -> None:
        """Adds a legend label

        Parameters
        ----------
        trace : `str`, optional
            The name of the trace to use as a template, by default None
        label : `str`, optional
            The label to use, by default None (uses the trace name if trace is specified)
            If trace is not specified, label must be specified
        mode : `str`, optional
            The mode to use, by default "lines" (uses the trace mode if trace is specified)
        marker : `dict`, optional
            The marker to use, by default dict() (uses the trace marker if trace is specified)
        line_dash : `str`, optional
            The line dash to use, by default "solid" (uses the trace line dash if trace is specified)
        legendrank : `int`, optional
            The legend rank, by default None (e.g. 1 is above 2)

        Raises
        ------
        ValueError
            If trace is not found
        ValueError
            If label is not specified and trace is not specified
        """

        if trace:
            for trace_ in self.data:
                if trace_.name == trace:
                    for arg, default in zip(
                        [label, mode, marker, line_dash],
                        [trace, trace_.mode, trace_.marker, trace_.line_dash],
                    ):
                        if not arg and default:
                            arg = default

                    kwargs.update(dict(yaxis=trace_.yaxis))
                    break
            else:
                raise ValueError(f"Trace '{trace}' not found")

        if not label:
            raise ValueError("Label must be specified")

        self.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode=mode or "lines",
                name=label,
                marker=marker or dict(),
                line_dash=line_dash or "solid",
                legendrank=legendrank,
                **kwargs,
            )
        )

    def show(self, *args, **kwargs) -> None:
        """Show the figure"""
        if kwargs.pop("margin", True):
            self._adjust_margins()
        self._apply_feature_flags()

        # height = 600 if not self.layout.height else self.layout.height
        # self.update_layout(
        #     legend=dict(
        #         tracegroupgap=height / 4.5,
        #         groupclick="toggleitem",
        #     ),
        #     barmode="overlay",
        #     bargap=0,
        #     bargroupgap=0,
        # )
        self.update_traces(marker_line_width=0.0001, selector=dict(type="bar"))

        # Set modebar style
        if self.layout.template.layout.mapbox.style == "dark":  # type: ignore
            self.update_layout(  # type: ignore
                newshape_line_color="gold",
                modebar=dict(
                    bgcolor="#2A2A2A",
                    color="#FFFFFF",
                    activecolor="#d1030d",
                ),
            )

        # We check if in Terminal Pro to return the JSON
        if strtobool(os.environ.get("TERMINAL_PRO", False)):
            return self.to_json()

        kwargs.update(config=dict(scrollZoom=True, displaylogo=False))
        if plots_backend().isatty:
            try:
                # We send the figure to the backend to be displayed
                return plots_backend().send_figure(self)
            except Exception:
                # If the backend fails, we just show the figure normally
                # This is a very rare case, but it's better to have a fallback
                if strtobool(os.environ.get("DEBUG_MODE", False)):
                    console.print_exception()

        return pio.show(self, *args, **kwargs)

    def to_subplot(
        self,
        subplot: "OpenBBFigure",
        row: int,
        col: int,
        secondary_y: bool = False,
        **kwargs,
    ) -> "OpenBBFigure":
        """Return the figure as a subplot of another figure

        Parameters
        ----------
        subplot : `plotly.graph_objects.Figure`
            The subplot
        row : `int`
            Row number
        col : `int`
            Column number
        secondary_y : `bool`, optional
            Whether to use the secondary y axis, by default False

        Returns
        -------
        `plotly.graph_objects.Figure`
            The subplot with the figure added
        """
        for trace in self.data:
            trace.legendgroup = f"{row}"
            if kwargs:
                trace.update(**kwargs)

            subplot.add_trace(trace, row=row, col=col, secondary_y=secondary_y)
            subplot.set_xaxis_title(self.layout.xaxis.title.text, row=row, col=col)
            subplot.set_yaxis_title(self.layout.yaxis.title.text, row=row, col=col)

        return subplot

    def to_html(self, *args, **kwargs) -> str:
        """Return the figure as HTML"""
        kwargs.update(
            dict(
                config={"displayModeBar": False, "scrollZoom": True},
                include_plotlyjs=kwargs.get("include_plotlyjs", False),
                full_html=False,
            )
        )
        if not plots_backend().isatty and self.data[0].type != "table":
            self.layout.margin = dict(l=30, r=30, b=50, t=50, pad=0)

        return super().to_html(*args, **kwargs)

    @staticmethod
    def row_colors(df: pd.DataFrame) -> Optional[List[str]]:
        """Return the row colors of the table

        Parameters
        ----------
        df : `pandas.DataFrame`
            The dataframe

        Returns
        -------
        `list`
            The list of colors
        """
        row_count = len(df)
        # we determine how many rows in `df` and then create a list with alternating
        # row colors
        row_odd_count = floor(row_count / 2) + row_count % 2
        row_even_count = floor(row_count / 2)
        odd_list = [PLT_TBL_ROW_COLORS[0]] * row_odd_count
        even_list = [PLT_TBL_ROW_COLORS[1]] * row_even_count
        color_list = [x for y in zip(odd_list, even_list) for x in y]
        if row_odd_count > row_even_count:
            color_list.append(PLT_TBL_ROW_COLORS[0])

        return color_list

    def hide_holidays(
        self, dateindex: Union[pd.DatetimeIndex, pd.Series, pd.Index]
    ) -> None:
        """Add rangebreaks to hide holidays on the xaxis

        Parameters
        ----------
        dateindex : `pandas.DatetimeIndex`
            The date index
        """
        if not isinstance(dateindex, pd.DatetimeIndex):
            dateindex = pd.DatetimeIndex(dateindex)

        mkt_holidays = USFederalHolidayCalendar().holidays(
            start=dateindex.min(), end=dateindex.max()
        )
        rangebreaks = [
            dict(values=[date.strftime("%Y-%m-%d") for date in mkt_holidays]),
            dict(bounds=["sat", "mon"]),
        ]

        # We add a rangebreak if the first and last time are not the same
        # since daily data will have the same time (00:00)
        if dateindex[0].time() != dateindex[-1].time():
            rangebreaks.append(dict(bounds=[15.99, 9.50], pattern="hour"))

        self.update_xaxes(
            rangebreaks=rangebreaks,
            type="date",
        )

    @staticmethod
    def _tbl_values(df: pd.DataFrame, print_index: bool) -> Tuple[List[str], List]:
        """Return the values of the table

        Parameters
        ----------
        df : `pandas.DataFrame`
            The dataframe to convert
        print_index : `bool`
            Whether to print the index

        Returns
        -------
        `tuple`
            The header values and the cell values
        """
        if print_index:
            header_values = list(
                [df.index.name if df.index.name is not None else "", *df.columns]
            )
            cell_values = [df.index, *[df[col] for col in df]]

        else:
            header_values = df.columns.to_list()
            cell_values = [df[col] for col in df]

        header_values = [f"<b>{x}</b>" for x in header_values]

        return header_values, cell_values

    @classmethod
    def to_table(
        cls,
        df: pd.DataFrame,
        columnwidth: Optional[List[Union[int, float]]] = None,
        print_index: bool = True,
        **kwargs,
    ) -> "OpenBBFigure":
        """Converts a dataframe to a table figure

        Parameters
        ----------
        df : `pandas.DataFrame`
            The dataframe to convert
        columnwidth : `list`, optional
            The width of each column, by default None (auto)
        print_index : `bool`, optional
            Whether to print the index, by default True
        height : `int`, optional
            The height of the table, by default len(df.index) * 28 + 25
        width : `int`, optional
            The width of the table, by default sum(columnwidth) * 8.7

        Returns
        -------
        `plotly.graph_objects.Figure`
            The figure as a table
        """

        if not columnwidth:
            # we get the length of each column using the max length of the column
            # name and the max length of the column values as the column width
            columnwidth = [
                max(len(str(df[col].name)), df[col].astype(str).str.len().max())
                for col in df.columns
            ]
            # we add the length of the index column if we are printing the index
            if print_index:
                columnwidth.insert(
                    0,
                    max(len(str(df.index.name)), df.index.astype(str).str.len().max()),
                )

            # we add a percentage of max to the min column width
            columnwidth = [
                int(x + (max(columnwidth) - min(columnwidth)) * 0.2)
                for x in columnwidth
            ]

        header_values, cell_values = cls._tbl_values(df, print_index)

        if (height := kwargs.get("height", None)) and height < len(df.index) * 28 + 25:
            kwargs.pop("height")
        if (width := kwargs.get("width", None)) and width < sum(columnwidth) * 8.7:
            kwargs.pop("width")

        height = kwargs.pop("height", len(df.index) * 28 + 25)
        width = kwargs.pop("width", sum(columnwidth) * 8.7)

        fig: OpenBBFigure = cls()
        fig.add_table(
            header=dict(values=header_values),
            cells=dict(
                values=cell_values,
                align="left",
                height=25,
            ),
            columnwidth=columnwidth,
            **kwargs,
        )
        fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
            font=dict(size=14),
        )

        return fig

    def _adjust_margins(self) -> None:
        """Adjust the margins of the figure"""
        margin_add = (
            [90, 90, 80, 40, 0] if not self._has_secondary_y else [90, 50, 80, 40, 0]
        )

        # We adjust margins
        if plots_backend().isatty:
            for key, add in zip(
                ["l", "r", "b", "t", "pad"],
                margin_add,
            ):
                if key in self.layout.margin and self.layout.margin[key] is not None:
                    self.layout.margin[key] += add
                else:
                    self.layout.margin[key] = add

        if not plots_backend().isatty:
            self.layout.margin = dict(l=30, r=40, b=80, t=50, pad=0)

    def _set_watermark(self) -> None:
        """Sets the watermark for OpenBB Terminal"""
        self.add_annotation(
            yref="y domain" if not self.has_subplots else "paper",
            xref="x domain",
            x=1,
            y=0,
            text="OpenBB Terminal",
            font_size=17,
            font_color="gray",
            opacity=0.5,
            xanchor="right",
            yanchor="bottom",
            showarrow=False,
            yshift=-80,
            xshift=40,
        )

    # pylint: disable=import-outside-toplevel
    def _add_cmd_source(self) -> None:
        """Sets the watermark for OpenBB Terminal"""
        from openbb_terminal.helper_funcs import command_location

        if command_location:
            yaxis = self.layout.yaxis
            yaxis2 = self.layout.yaxis2 if hasattr(self.layout, "yaxis2") else None
            xshift = -60 if yaxis.side == "right" else -80

            if yaxis2 and yaxis2.overlaying == "y":
                xshift = -110 if not yaxis2.title.text else -120

            self.add_annotation(
                x=-0.015,
                y=0.5,
                yref="paper",
                xref="paper",
                text=command_location,
                textangle=-90,
                font_size=24,
                font_color="gray",
                opacity=0.5,
                yanchor="middle",
                xanchor="left",
                xshift=xshift,
                showarrow=False,
            )

    # pylint: disable=import-outside-toplevel
    def _apply_feature_flags(self) -> None:
        import openbb_terminal.feature_flags as obbff

        if obbff.USE_CMD_LOCATION_FIGURE:
            self._add_cmd_source()
        if obbff.USE_WATERMARK:
            self._set_watermark()

    def add_logscale_menus(self) -> None:
        """Sets the menus for the figure"""
        self.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=False),
                rangeselector=dict(
                    bgcolor="#000000",
                    bordercolor="gold",
                    font=dict(color="white"),
                    buttons=list(
                        [
                            dict(
                                count=1,
                                label="1M",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(
                                count=3,
                                label="3M",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(
                                count=1,
                                label="1y",
                                step="year",
                                stepmode="backward",
                            ),
                            dict(step="all"),
                        ]
                    ),
                ),
            ),
            bargap=0,
            bargroupgap=0,
        )

        self.update_layout(
            updatemenus=[
                dict(
                    bgcolor="#000000",
                    bordercolor="gold",
                    font=dict(color="white", size=14),
                    buttons=[
                        dict(
                            label="linear   ",
                            method="relayout",
                            args=[{"yaxis.type": "linear"}],
                        ),
                        dict(
                            label="log",
                            method="relayout",
                            args=[{"yaxis.type": "log"}],
                        ),
                    ],
                    y=1.07,
                    x=-0.01,
                )
            ],
        )
