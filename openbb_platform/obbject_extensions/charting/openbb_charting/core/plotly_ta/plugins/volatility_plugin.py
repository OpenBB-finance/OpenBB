"""Volatility technical indicators plugin for Plotly TA."""

import pandas as pd

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.base import (
    PltTA,
    indicator,
)
from openbb_charting.core.plotly_ta.data_classes import (
    columns_regex,
)


class Volatility(PltTA):
    """Volatility technical indicators."""

    __inchart__ = ["bbands", "donchian", "kc"]
    __subplots__ = ["atr"]

    @indicator()
    def plot_atr(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Add average true range to plotly figure."""
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'ATR')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "ATR")[0]].values,
            mode="lines",
            line=dict(width=1, color=fig.theme.get_colors()[1]),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>ATR</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color=fig.theme.get_colors()[1],
        )
        fig["layout"][f"yaxis{subplot_row}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_bbands(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Add bollinger bands to plotly figure."""
        bbands_opacity = 0.8 if fig.theme.plt_style == "light" else 1

        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBU')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBU")[0]].values,
            opacity=bbands_opacity,
            mode="lines",
            line=dict(width=1, color=fig.theme.up_color),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBL')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBL")[0]].values,
            opacity=bbands_opacity,
            mode="lines",
            line=dict(width=1, color=fig.theme.down_color),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBM')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBM")[0]].values,
            opacity=1,
            mode="lines",
            line=dict(width=1, color=fig.theme.get_colors()[1], dash="dash"),
            row=1,
            col=1,
            secondary_y=False,
        )
        bbands_text = (
            columns_regex(df_ta, "BBL")[0].replace("BBL_", "BB").replace("_", ",")
        )
        if float(bbands_text.split(",")[1]) % 1 == 0:
            bbands_text = bbands_text.split(".")[0]
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text=f"<b>{bbands_text}</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color=fig.theme.get_colors()[1],
            opacity=0.9,
        )

        return fig, inchart_index + 1

    @indicator()
    def plot_donchian(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Add donchian channels to plotly figure."""
        if fig.theme.plt_style == "light":
            fillcolor = "rgba(239, 103, 137, 0.05)"
            donchian_opacity = 0.4
        else:
            fillcolor = "rgba(239, 103, 137, 0.05)"
            donchian_opacity = 0.4

        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'DCU')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DCU")[0]].values,
            opacity=donchian_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'DCL')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DCL")[0]].values,
            opacity=donchian_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            fill="tonexty",
            fillcolor=fillcolor,
            row=1,
            col=1,
            secondary_y=False,
        )

        donchian_text = (
            columns_regex(df_ta, "DCL")[0]
            .replace("DCL_", "DC")
            .replace("_", ",")
            .split(".")[0]
        )

        fig.add_annotation(
            xref="paper",
            yref="paper",
            text=f"<b>{donchian_text}</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color="#B47DA0",
            opacity=0.9,
        )

        return fig, inchart_index + 1

    @indicator()
    def plot_kc(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Add Keltner channels to plotly figure."""
        mamode = (self.params["kc"].get_argument_values("mamode") or "ema").lower()  # type: ignore

        if fig.theme.plt_style == "light":
            fillcolor = "rgba(239, 103, 137, 0.05)"
            kc_opacity = 0.4
        else:
            fillcolor = "rgba(239, 103, 137, 0.05)"
            kc_opacity = 0.4

        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'KCU')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "KCU")[0]].values,
            opacity=kc_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'KCL')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "KCL")[0]].values,
            opacity=kc_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            fill="tonexty",
            fillcolor=fillcolor,
            row=1,
            col=1,
            secondary_y=False,
        )
        kctext = (
            columns_regex(df_ta, "KCL")[0]
            .replace(f"KCL{mamode[0]}_", "KC")
            .replace("_", ",")
            .split(".")[0]
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text=f"<b>{kctext}</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color="#B47DA0",
            opacity=0.9,
        )

        return fig, inchart_index + 1
