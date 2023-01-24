# pylint: disable=C0302,R0915,R0914,R0913,R0903,R0904

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from openbb_terminal.common.technical_analysis.custom_indicators_model import (
    calculate_fib_levels,
)
from openbb_terminal.core.plots.config.openbb_styles import PLT_FIB_COLORWAY
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.base import indicator
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA


class Custom(PlotlyTA):
    """Volatility technical indicators"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_srlines(self, fig: OpenBBFigure, df_ta: pd.DataFrame):
        """Adds support and resistance lines to plotly figure"""

        def is_far_from_level(value, levels, df_stock):
            ave = np.mean(df_stock["High"] - df_stock["Low"])
            return np.sum([abs(value - level) < ave for _, level in levels]) == 0

        def is_support(df, i):
            cond1 = df["Low"][i] < df["Low"][i - 1]
            cond2 = df["Low"][i] < df["Low"][i + 1]
            cond3 = df["Low"][i + 1] < df["Low"][i + 2]
            cond4 = df["Low"][i - 1] < df["Low"][i - 2]
            return cond1 and cond2 and cond3 and cond4

        def is_resistance(df, i):
            cond1 = df["High"][i] > df["High"][i - 1]
            cond2 = df["High"][i] > df["High"][i + 1]
            cond3 = df["High"][i + 1] > df["High"][i + 2]
            cond4 = df["High"][i - 1] > df["High"][i - 2]
            return cond1 and cond2 and cond3 and cond4

        df_ta2 = df_ta.copy()
        if df_ta2.index[-2].date() != df_ta2.index[-1].date():
            interval = 1440
        else:
            interval = (df_ta2.index[1] - df_ta2.index[0]).seconds / 60

        if interval <= 15:
            cut_days = 1 if interval < 15 else 2
            dt_unique_days = df_ta2.index.normalize().unique()
            df_ta2 = df_ta2.loc[
                (df_ta.index >= dt_unique_days[-cut_days])
                & (df_ta.index < datetime.now())
            ].copy()

        levels: list = []
        x_range = (
            df_ta2.index[-1].replace(hour=17, minute=45)
            if interval < 15
            else df_ta2.index[-1].replace(hour=15, minute=45)
        )
        if interval > 15:
            x_range = df_ta2.index[-1] + timedelta(days=15)
            if x_range.weekday() > 4:
                x_range = x_range + timedelta(days=7 - x_range.weekday())

        for i in range(2, len(df_ta2) - 2):

            if is_support(df_ta2, i):
                lv = df_ta2["Low"][i]
                if is_far_from_level(lv, levels, df_ta2):
                    levels.append((i, lv))
                    fig.add_scatter(
                        x=[x_range],
                        y=[lv],
                        opacity=1,
                        mode="text",
                        text=f"{lv:{self.get_float_precision()}}",
                        textposition="top left",
                        textfont=dict(
                            family="Arial Black", color="rgb(120, 70, 200)", size=12
                        ),
                        showlegend=False,
                        row=1,
                        col=1,
                    )
                    fig.add_hline(
                        y=lv,
                        line_width=2,
                        line_dash="dash",
                        line_color="rgba(120, 70, 200, 0.70)",
                        row=1,
                        col=1,
                    )
            elif is_resistance(df_ta2, i):
                lv = df_ta2["High"][i]
                if is_far_from_level(lv, levels, df_ta2):
                    levels.append((i, lv))
                    fig.add_scatter(
                        x=[x_range],
                        y=[lv],
                        opacity=1,
                        mode="text",
                        text=f"{lv:{self.get_float_precision()}}",
                        textposition="top left",
                        textfont=dict(
                            family="Arial Black", color="rgb(120, 70, 200)", size=12
                        ),
                        showlegend=False,
                        row=1,
                        col=1,
                    )
                    fig.add_hline(
                        y=lv,
                        line_width=2,
                        line_dash="dash",
                        line_color="rgba(120, 70, 200, 0.70)",
                        row=1,
                        col=1,
                    )

        return fig

    @indicator()
    def plot_fib(self, fig: OpenBBFigure, df_ta: pd.DataFrame):
        """Adds fibonacci to plotly figure"""
        (
            df_fib,
            min_date,
            max_date,
            min_pr,
            max_pr,
            lvl_text,
        ) = calculate_fib_levels(df_ta, 120, df_ta.index.max(), None)
        levels = df_fib.Price
        fibs = [
            "<b>0</b>",
            "<b>0.235</b>",
            "<b>0.382</b>",
            "<b>0.5</b>",
            "<b>0.618</b>",
            "<b>0.65</b>",
            "<b>1</b>",
        ]
        fig.add_scatter(
            x=[min_date, max_date],
            y=[min_pr, max_pr],
            opacity=0.9,
            mode="lines",
            line=PLT_FIB_COLORWAY[8],
            showlegend=False,
            row=1,
            col=1,
        )
        df_ta2 = df_ta.copy()
        interval = 1440
        if df_ta2.index[-2].date() == df_ta2.index[-1].date():
            interval = (df_ta2.index[1] - df_ta2.index[0]).seconds / 60
            dt_unique_days = df_ta2.index.normalize().unique()

            if interval not in [15, 30, 60]:
                if len(dt_unique_days) <= 3:
                    df_ta2 = df_ta2.loc[
                        (df_ta2.index >= dt_unique_days[-1])
                        & (df_ta2.index < datetime.now())
                    ].copy()
                    df_ta2 = df_ta2.between_time("09:30", "20:00").copy()

        for i in range(7):
            fig.add_scatter(
                name=fibs[i],
                x=[min_date, df_ta2.index.max()],
                y=[levels[i], levels[i]],
                opacity=0.9,
                mode="lines",
                line_color=PLT_FIB_COLORWAY[i],
                line_width=1.5,
                showlegend=False,
                row=1,
                col=1,
            )

        for i in range(7):
            idx_int = 4 if lvl_text == "left" else 5

            text_pos = f"top {lvl_text}" if i != idx_int else f"bottom {lvl_text}"
            padding = 0.003 if interval > 15 else 0.0005
            y_pos = (
                levels[i] + (levels[i] * padding)
                if i != idx_int
                else levels[i] - (levels[i] * padding)
            )

            if fibs[i] == "<b>0</b>":
                text_pos = (
                    f"bottom {lvl_text}" if lvl_text != "right" else f"top {lvl_text}"
                )
                padding = 0.004 if interval > 15 else 0.0002
                y_pos = (
                    y_pos - (levels[i] * padding)
                    if lvl_text != "right"
                    else y_pos + (levels[i] * padding)
                )

            x_pos = max_date if max_date > min_date else min_date
            x_pos = x_pos - timedelta(hours=2) if interval == 15 else x_pos
            y_pos = levels[i] if levels[i] < 1 else y_pos

            fig.add_scatter(
                name=fibs[i],
                x=[x_pos],
                y=[y_pos],
                opacity=1,
                mode="text",
                text=f"{fibs[i]} ({levels[i]:{self.get_float_precision()}})",
                textposition=text_pos,
                textfont=dict(PLT_FIB_COLORWAY[7], color=PLT_FIB_COLORWAY[i]),
                showlegend=False,
                row=1,
                col=1,
            )

        return fig
