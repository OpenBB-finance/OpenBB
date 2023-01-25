# pylint: disable=C0302,R0915,R0914,R0913,R0903,R0904

import pandas as pd

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
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
        )
        fig.add_scatter(
            name="+DI",
            mode="lines",
            line=dict(width=1.5, color="#9467bd"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DMP")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
        )
        fig.add_scatter(
            name="-DI",
            mode="lines",
            line=dict(width=1.5, color="#e250c3"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "DMN")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>ADX</b>",
            x=0,
            xanchor="right",
            xshift=-8,
            y=0.97,
            font_size=16,
            font_color="#e0b700",
            showarrow=False,
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>D+</b>",
            x=0,
            xanchor="right",
            xshift=-24,
            y=0.97,
            yshift=-20,
            font_size=16,
            font_color="#9467bd",
            showarrow=False,
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>D-</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.97,
            yshift=-20,
            font_size=16,
            font_color="#e250c3",
            showarrow=False,
        )
        fig.add_hline(
            y=25,
            fillcolor="grey",
            opacity=1,
            layer="below",
            line_width=1.5,
            line=dict(color="grey", dash="dash"),
            row=subplot_row,
            col=1,
        )
        fig["layout"][f"yaxis{subplot_row}"].update(nticks=5, autorange=True)

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
            line=dict(width=1.5, color="#9467bd"),
            x=df_ta.index,
            y=df_ta[aroon_up_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
        )
        fig.add_scatter(
            name="Aroon Down",
            mode="lines",
            line=dict(width=1.5, color="#e250c3"),
            x=df_ta.index,
            y=df_ta[aroon_down_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
        )
        fig.add_scatter(
            name="Aroon Oscillator",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[aroon_osc_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>Aroon</b>",
            x=0,
            xanchor="right",
            xshift=-8,
            y=0.98,
            font_size=16,
            font_color="#e0b700",
            showarrow=False,
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>UP</b>",
            x=0,
            xanchor="right",
            xshift=-15,
            y=0.79,
            font_size=16,
            font_color="#9467bd",
            showarrow=False,
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row} domain",
            text="<b>DOWN</b>",
            x=0,
            xanchor="right",
            xshift=-8,
            y=0.79,
            font_size=16,
            font_color="#e250c3",
            showarrow=False,
        )
        fig.add_hline(
            y=25,
            fillcolor="grey",
            opacity=1,
            layer="below",
            line_width=1.5,
            line=dict(color="grey", dash="dash"),
            row=subplot_row,
            col=1,
        )
        fig["layout"][f"yaxis{subplot_row}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1
