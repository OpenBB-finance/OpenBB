import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.core.plots.plotly_ta.base import PltTA, indicator
from openbb_terminal.core.plots.plotly_ta.data_classes import columns_regex


class Trend(PltTA):
    """Trend technical indicators"""

    __subplots__ = ["adx", "aroon"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_adx(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds adx to plotly figure"""
        fig.add_scatter(
            name="ADX",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "ADX")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="+DI",
            mode="lines",
            line=dict(width=1.5, color=theme.up_color),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DMP")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="-DI",
            mode="lines",
            line=dict(width=1.5, color=theme.down_color),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DMN")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>ADX</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.97,
            font_size=14,
            font_color="#e0b700",
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text=(
                f"<span style='color: {theme.up_color}'>D+</span><br>"
                f"<span style='color: {theme.down_color}'>D-</span>"
            ),
            x=0,
            xanchor="right",
            xshift=-14,
            y=0.97,
            yshift=-20,
            font_size=14,
            font_color=theme.up_color,
        )
        fig.add_hline(
            y=25,
            fillcolor="white",
            opacity=1,
            layer="below",
            line_width=1.5,
            line=dict(color="white", dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_aroon(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds aroon to plotly figure"""
        aroon_up_col = columns_regex(df_ta, "AROONU")[0]
        aroon_down_col = columns_regex(df_ta, "AROOND")[0]
        aroon_osc_col = columns_regex(df_ta, "AROONOSC")[0]
        fig.add_scatter(
            name="Aroon Up",
            mode="lines",
            line=dict(width=1.5, color=theme.up_color),
            x=df_ta.index,
            y=df_ta[aroon_up_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="Aroon Down",
            mode="lines",
            line=dict(width=1.5, color=theme.down_color),
            x=df_ta.index,
            y=df_ta[aroon_down_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>Aroon</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=1,
            font_size=14,
            font_color="#e0b700",
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text=(
                f"<span style='color: {theme.up_color}'>↑</span><br>"
                f"<span style='color: {theme.down_color}'>↓</span>"
            ),
            x=0,
            xanchor="right",
            xshift=-14,
            y=0.75,
            font_size=14,
            font_color=theme.down_color,
        )
        fig.add_hline(
            y=50,
            fillcolor="white",
            opacity=1,
            layer="below",
            line_width=1.5,
            line=dict(color="white", dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        subplot_row += 1

        fig.add_scatter(
            name="Aroon Oscillator",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[aroon_osc_col].values,
            connectgaps=True,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>Aroon<br>OSC</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color="#e0b700",
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(
            tickvals=[-100, 0, 100],
            ticktext=["-100", "0", "100"],
            nticks=5,
            autorange=True,
        )

        return fig, subplot_row + 1
