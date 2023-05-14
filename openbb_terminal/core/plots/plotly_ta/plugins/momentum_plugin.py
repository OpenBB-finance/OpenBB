import numpy as np
import pandas as pd
import pandas_ta as ta

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.common.technical_analysis.momentum_model import clenow_momentum
from openbb_terminal.core.plots.plotly_ta.base import PltTA, indicator
from openbb_terminal.core.plots.plotly_ta.data_classes import columns_regex


class Momentum(PltTA):
    """Momentum technical indicators"""

    __subplots__ = ["rsi", "macd", "stoch", "cci", "fisher", "cg"]
    __inchart__ = ["clenow", "demark", "ichimoku"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_cci(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds cci to plotly figure"""
        cci_col = columns_regex(df_ta, "CCI")[0]
        dmax = df_ta[cci_col].max()
        dmin = df_ta[cci_col].min()
        fig.add_scatter(
            name="CCI",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[cci_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_hrect(
            y0=100,
            y1=dmax,
            fillcolor=theme.down_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hrect(
            y0=-100,
            y1=dmin,
            fillcolor=theme.up_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=100,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.down_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=-100,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.up_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>CCI</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.97,
            font_size=14,
            font_color="#e0b700",
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_cg(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds cg to plotly figure"""
        cg_col = columns_regex(df_ta, "CG")[0]
        fig.add_scatter(
            name="CG",
            mode="lines",
            line=dict(width=1.5, color="#ffed00"),
            x=df_ta.index,
            y=df_ta[cg_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="Signal",
            mode="lines",
            line=dict(width=1.5, color="#ef7d00"),
            x=df_ta.index,
            y=df_ta[cg_col].shift(1),
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>CG</b>",
            x=0,
            xanchor="right",
            xshift=-10,
            y=0.97,
            font_size=14,
            font_color="#ffed00",
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="Signal",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.97,
            yshift=-20,
            font_size=14,
            font_color="#ef7d00",
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_clenow(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds current close price to plotly figure"""
        window = self.params["clenow"].get_argument_values("window") or 90
        _, _, fit_data = clenow_momentum(df_ta[self.close_column], window=window)

        fig.add_scatter(
            x=df_ta.index[-window:],  # type: ignore
            y=pow(np.e, fit_data),
            name="CLenow",
            mode="lines",
            line=dict(color=self.inchart_colors[inchart_index], width=2),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text="<b>CLenow</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color=self.inchart_colors[inchart_index],
            opacity=1,
        )
        return fig, inchart_index + 1

    @indicator()
    def plot_demark(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds demark to plotly figure"""
        min_val = self.params["demark"].get_argument_values("min_val") or 5

        demark = ta.td_seq(df_ta[self.close_column], asint=True)
        demark.set_index(df_ta.index, inplace=True)

        demark["up"] = demark.TD_SEQ_UPa.apply(
            lambda x: f"<b>{x}</b>" if x >= min_val else None
        )
        demark["down"] = demark.TD_SEQ_DNa.apply(
            lambda x: f"<b>{x}</b>" if x >= min_val else None
        )

        # we only keep the values that are not None in up/down columns
        high = df_ta["High"][demark["up"].notnull()]
        low = df_ta["Low"][demark["down"].notnull()]
        demark = demark[demark["up"].notnull() | demark["down"].notnull()]

        fig.add_scatter(
            x=low.index,
            y=low,
            name="Demark Down",
            mode="text",
            text=demark["down"],
            textposition="bottom center",
            textfont=dict(color=theme.down_color, size=14.5),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            x=high.index,
            y=high,
            name="Demark Up",
            mode="text",
            text=demark["up"],
            textposition="top center",
            textfont=dict(color=theme.up_color, size=14.5),
            row=1,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref="paper",
            yref="paper",
            text="<b>Demark</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color=self.inchart_colors[inchart_index],
            opacity=1,
        )

        return fig, inchart_index + 1

    @indicator()
    def plot_fisher(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds fisher to plotly figure"""
        fishert_col = columns_regex(df_ta, "FISHERT")[0]
        fishers_col = columns_regex(df_ta, "FISHERTs")[0]
        fig.add_scatter(
            name="Fisher",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[fishert_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="Fisher Signal",
            mode="lines",
            line=dict(width=1.5, color="#9467bd"),
            x=df_ta.index,
            y=df_ta[fishers_col].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        dmax = df_ta[fishers_col].max()
        dmin = df_ta[fishers_col].min()

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>FISHER</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color="#e0b700",
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>SIGNAL</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.01,
            font_size=13,
            font_color="#9467bd",
        )
        fig.add_hrect(
            y0=2,
            y1=(dmax + 4),
            fillcolor=theme.down_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hrect(
            y0=-2,
            y1=(dmin - 4),
            fillcolor=theme.up_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=2,
            fillcolor=theme.down_color,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.down_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=-2,
            fillcolor=theme.up_color,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.up_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_macd(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds macd to plotly figure"""

        fig.add_bar(
            name="MACD Histogram",
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "MACDh")[0]].values,
            opacity=0.9,
            marker_color="#1a97ea",
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="MACD",
            mode="lines",
            line=dict(width=1.5, color="#9467bd"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "MACD")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="MACD Signal",
            mode="lines",
            line=dict(width=1.5, color="rgb(7, 166, 52)"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "MACDs")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>MACD</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color="#9467bd",
        )
        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>SIGNAL</b>",
            x=0,
            xanchor="right",
            y=0.70,
            font_size=13,
            xshift=-3,
            font_color="rgb(7, 166, 52)",
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(autorange=True, nticks=5)

        return fig, subplot_row + 1

    @indicator()
    def plot_rsi(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds rsi to plotly figure"""
        rsi_col = columns_regex(df_ta, "RSI")[0]
        fig.add_scatter(
            name="RSI",
            mode="lines",
            line=dict(width=1.5, color="rgb(0, 122, 204, 1)"),
            x=df_ta.index,
            y=df_ta[rsi_col].values,
            opacity=1,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>RSI</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color="rgb(0, 122, 204, 1)",
        )
        fig.add_hrect(
            y0=70,
            y1=100,
            fillcolor=theme.down_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hrect(
            y0=0,
            y1=30,
            fillcolor=theme.up_color,
            opacity=0.2,
            layer="below",
            line_width=0,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=70,
            fillcolor=theme.down_color,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.down_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_hline(
            y=30,
            fillcolor=theme.up_color,
            opacity=1,
            layer="below",
            line=dict(width=2, color=theme.up_color, dash="dash"),
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(tickvals=[0, 30, 70, 100])

        return fig, subplot_row + 1

    @indicator()
    def plot_stoch(self, fig: OpenBBFigure, df_ta: pd.DataFrame, subplot_row: int):
        """Adds stoch to plotly figure"""
        fig.add_scatter(
            name="STOCH %K",
            mode="lines",
            line=dict(width=1.5, color="#e0b700"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "STOCHk")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )
        fig.add_scatter(
            name="STOCH %D",
            mode="lines",
            line=dict(width=1.5, color="#9467bd", dash="dash"),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "STOCHd")[0]].values,
            opacity=0.9,
            row=subplot_row,
            col=1,
            secondary_y=False,
        )

        fig.add_annotation(
            xref=f"x{subplot_row} domain",
            yref=f"y{subplot_row + 1} domain",
            text="<b>STOCH</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            y=0.98,
            font_size=14,
            font_color="#e0b700",
        )
        fig["layout"][f"yaxis{subplot_row + 1}"].update(nticks=5, autorange=True)

        return fig, subplot_row + 1

    @indicator()
    def plot_ichimoku(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        # Calculate Ichimoku indicator
        conversion_period = (
            self.params["ichimoku"].get_argument_values("conversion_period") or 9
        )
        base_period = self.params["ichimoku"].get_argument_values("base_period") or 26
        lagging_line_period = (
            self.params["ichimoku"].get_argument_values("lagging_line_period") or 52
        )
        displacement = self.params["ichimoku"].get_argument_values("displacement") or 26

        # Tenkan-sen (Conversion Line)
        conversion_line = (
            df_ta["High"].rolling(window=conversion_period).max()
            + df_ta["Low"].rolling(window=conversion_period).min()
        ) / 2

        # Kijun-sen (Base Line)
        base_line = (
            df_ta["High"].rolling(window=base_period).max()
            + df_ta["Low"].rolling(window=base_period).min()
        ) / 2

        # Senkou Span A (Leading Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(displacement)

        # Senkou Span B (Leading Span B)
        lagging_line = df_ta[self.close_column].shift(-lagging_line_period)  # type: ignore
        leading_span_b = (
            (
                lagging_line.rolling(window=base_period).max()
                + lagging_line.rolling(window=base_period).min()
            )
            / 2
        ).shift(displacement)

        # Plot Tenkan-sen and Kijun-sen
        fig.add_scatter(
            x=df_ta.index,
            y=conversion_line,
            line=dict(color="orange", width=1),
            name="Tenkan-sen",
            secondary_y=False,
            showlegend=True,
            opacity=1,
        )
        fig.add_scatter(
            x=df_ta.index,
            y=base_line,
            line=dict(color="blue", width=1),
            name="Kijun-sen",
            secondary_y=False,
            showlegend=True,
            opacity=1,
        )

        # Plot Senkou Span A and Senkou Span B as a filled area
        fig.add_scatter(
            x=df_ta.index,
            y=leading_span_a,
            line=dict(color="#009600", width=1),
            fill="tonexty",
            fillcolor="rgba(0, 150, 0, 0.1)",
            name="Senkou Span A",
            secondary_y=False,
            showlegend=False,
            opacity=0.2,
        )
        fig.add_scatter(
            x=df_ta.index,
            y=leading_span_b,
            line=dict(color="#c80000", width=1),
            fill="tonexty",
            fillcolor="rgba(200, 0, 0, 0.1)",
            name="Senkou Span B",
            showlegend=False,
            secondary_y=False,
            opacity=0.2,
        )

        fig.add_annotation(
            xref="paper",
            yref="paper",
            text="<b><span style='color:#009600'>Ichi</span>"
            "<span style='color:#c80000'>moku</span></b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            opacity=1,
        )

        return fig, inchart_index + 1
