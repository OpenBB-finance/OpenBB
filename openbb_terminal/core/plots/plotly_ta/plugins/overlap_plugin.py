import logging

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.base import PltTA, indicator
from openbb_terminal.core.plots.plotly_ta.data_classes import columns_regex

logger = logging.getLogger(__name__)


class Overlap(PltTA):
    """Overlap technical indicators"""

    __inchart__ = ["vwap"]
    __ma_mode__ = ["sma", "ema", "wma", "hma", "zlma", "rma"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_ma(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds moving average to plotly figure"""
        check_ma = [ma for ma in self.ma_mode if ma in self.indicators.get_active_ids()]
        if check_ma:
            for ma in check_ma:
                column_names = columns_regex(df_ta, ma.upper())
                try:
                    for column in column_names:
                        if df_ta[column].empty:
                            continue

                        fig.add_scatter(
                            name=column.replace("RMA", "MA"),
                            mode="lines",
                            line=dict(
                                width=1.2, color=self.inchart_colors[inchart_index]
                            ),
                            x=df_ta.index,
                            y=df_ta[column].values,
                            opacity=0.9,
                            connectgaps=True,
                            row=1,
                            col=1,
                            secondary_y=False,
                        )
                        fig.add_annotation(
                            xref="paper",
                            yref="paper",
                            text=f"<b>{column.replace('_', '').replace('RMA', 'MA')}</b>",
                            x=0,
                            xanchor="right",
                            xshift=-6,
                            yshift=-inchart_index * 18,
                            y=0.98,
                            font_size=14,
                            font_color=self.inchart_colors[inchart_index],
                            opacity=1,
                        )
                        inchart_index += 1

                except Exception as e:
                    logger.exception("Error adding %s to plot - %s", ma.upper(), e)

        return fig, inchart_index

    @indicator()
    def plot_vwap(self, fig: OpenBBFigure, df_ta: pd.DataFrame, inchart_index: int):
        """Adds vwap to plotly figure"""
        fig.add_scatter(
            name=columns_regex(df_ta, "VWAP_")[0],
            mode="lines",
            line=dict(width=1.5, color=self.inchart_colors[inchart_index]),
            x=df_ta.index,
            y=df_ta[columns_regex(df_ta, "VWAP_")[0]].values,
            opacity=0.8,
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            text="<b>VWAP</b>",
            x=0,
            xanchor="right",
            xshift=-6,
            yshift=-inchart_index * 18,
            y=0.98,
            font_size=14,
            font_color=self.inchart_colors[inchart_index],
        )

        return fig, inchart_index + 1
