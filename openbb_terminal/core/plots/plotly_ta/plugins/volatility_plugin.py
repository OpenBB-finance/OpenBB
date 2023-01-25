import pandas as pd

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure, theme
from openbb_terminal.core.plots.plotly_ta.base import PltTA, indicator
from openbb_terminal.core.plots.plotly_ta.data_classes import columns_regex


class Volatility(PltTA):
    """Volatility technical indicators"""

    __inchart__ = ["bbands", "donchian"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_bbands(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds bollinger bands to plotly figure"""

        if theme.plt_style == "light":
            fillcolor = "rgba(239, 103, 137, 0.05)"
            bbands_opacity = 0.4
        else:
            fillcolor = "rgba(239, 103, 137, 0.05)"
            bbands_opacity = 0.4

        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBU')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBU")[0]].values,
            opacity=bbands_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            row=1,
            col=1,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBL')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBL")[0]].values,
            opacity=bbands_opacity,
            mode="lines",
            line=dict(width=0.3, color="#EF6689"),
            fill="tonexty",
            fillcolor=fillcolor,
            row=1,
            col=1,
        )
        fig.add_scatter(
            name=f"{columns_regex(df_ta, 'BBM')[0]}",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "BBM")[0]].values,
            opacity=0.9,
            mode="lines",
            line=dict(width=0.3, color="#e250c3"),
            row=1,
            col=1,
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text=(
                f"<b>BB{self.params['bbands'].get_argument_values('length') or ''},"
                f"{self.params['bbands'].get_argument_values('std') or ''}</b>"
            ),
            x=0,
            xanchor="left",
            yshift=-inchart_index * 20,
            xshift=-70,
            y=0.98,
            font_size=16,
            font_color="#B47DA0",
            opacity=0.5,
            showarrow=False,
        )

        return fig, inchart_index + 1

    @indicator()
    def plot_donchian(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds donchian channels to plotly figure"""
        print("plot_donchian")
        print(f"inchart_index: {inchart_index}")

        if theme.plt_style == "light":
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
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text=(
                f"<b>DC{self.params['donchian'].get_argument_values('upper_length') or ''},"
                f"{self.params['donchian'].get_argument_values('lower_length') or ''}</b>"
            ),
            x=0,
            xanchor="left",
            yshift=-inchart_index * 20,
            xshift=-70,
            y=0.98,
            font_size=16,
            font_color="#B47DA0",
            opacity=0.5,
            showarrow=False,
        )

        return fig, inchart_index + 1
