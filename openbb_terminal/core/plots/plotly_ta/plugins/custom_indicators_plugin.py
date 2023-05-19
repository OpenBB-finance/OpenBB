from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.technical_analysis.custom_indicators_model import (
    calculate_fib_levels,
)
from openbb_terminal.core.plots.config.openbb_styles import PLT_FIB_COLORWAY
from openbb_terminal.core.plots.plotly_ta.base import PltTA, indicator


class Custom(PltTA):
    """Volatility technical indicators"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @indicator()
    def plot_srlines(self, fig: OpenBBFigure, df_ta: pd.DataFrame):
        """Adds support and resistance lines to plotly figure"""
        window = self.params["srlines"].get_argument_values("window")
        window = window[0] if isinstance(window, list) and len(window) > 0 else 200

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
        today = pd.to_datetime(datetime.now(), unit="ns")
        start_date = pd.to_datetime(datetime.now() - timedelta(days=window), unit="ns")

        df_ta2 = df_ta2.loc[(df_ta2.index >= start_date) & (df_ta2.index < today)]

        if df_ta2.index[-2].date() != df_ta2.index[-1].date():
            interval = 1440
        else:
            interval = (df_ta2.index[1] - df_ta2.index[0]).seconds / 60

        if interval <= 15:
            cut_days = 1 if interval < 15 else 2
            dt_unique_days = df_ta2.index.normalize().unique()
            df_ta2 = df_ta2.loc[
                (df_ta2.index >= pd.to_datetime(dt_unique_days[-cut_days], unit="ns"))
                & (df_ta2.index < today)
            ].copy()

        levels: list = []
        x_range = df_ta2.index[-1].replace(hour=15, minute=59)
        if interval > 15:
            x_range = df_ta2.index[-1] + timedelta(days=15)
            if x_range.weekday() > 4:
                x_range = x_range + timedelta(days=7 - x_range.weekday())

        elif df_ta2.index[-1] >= today.replace(hour=15, minute=0):
            x_range = (df_ta2.index[-1] + timedelta(days=1)).replace(hour=11, minute=0)
            if x_range.weekday() > 4:
                x_range = x_range + timedelta(days=7 - x_range.weekday())

        for i in range(2, len(df_ta2) - 2):
            if is_support(df_ta2, i):
                lv = df_ta2["Low"][i]
                if is_far_from_level(lv, levels, df_ta2):
                    levels.append((i, lv))
                    fig.add_scatter(
                        x=[df_ta.index[0], x_range],
                        y=[lv, lv],
                        opacity=1,
                        mode="lines+text",
                        text=["", f"{lv:{self.get_float_precision()}}"],
                        textposition="top center",
                        textfont=dict(
                            family="Arial Black", color="rgb(120, 70, 200)", size=10
                        ),
                        line=dict(
                            width=2, dash="dash", color="rgba(120, 70, 200, 0.70)"
                        ),
                        connectgaps=True,
                        showlegend=False,
                        row=1,
                        col=1,
                        secondary_y=False,
                    )
            elif is_resistance(df_ta2, i):
                lv = df_ta2["High"][i]
                if is_far_from_level(lv, levels, df_ta2):
                    levels.append((i, lv))
                    fig.add_scatter(
                        x=[df_ta.index[0], x_range],
                        y=[lv, lv],
                        opacity=1,
                        mode="lines+text",
                        text=["", f"{lv:{self.get_float_precision()}}"],
                        textposition="top center",
                        textfont=dict(
                            family="Arial Black", color="rgb(120, 70, 200)", size=10
                        ),
                        line=dict(
                            width=2, dash="dash", color="rgba(120, 70, 200, 0.70)"
                        ),
                        connectgaps=True,
                        showlegend=False,
                        row=1,
                        col=1,
                        secondary_y=False,
                    )

        return fig

    @indicator()
    def plot_fib(self, fig: OpenBBFigure, df_ta: pd.DataFrame):
        """Adds fibonacci to plotly figure"""
        limit = self.params["fib"].get_argument_values("limit") or 120
        start_date = self.params["fib"].get_argument_values("start_date") or None
        end_date = self.params["fib"].get_argument_values("end_date") or None
        (
            df_fib,
            min_date,
            max_date,
            min_pr,
            max_pr,
            lvl_text,
        ) = calculate_fib_levels(df_ta, limit, start_date, end_date)
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
        min_date = pd.to_datetime(min_date).to_pydatetime()
        max_date = pd.to_datetime(max_date).to_pydatetime()
        self.df_fib = df_fib

        fig.add_scatter(
            x=[min_date, max_date],
            y=[min_pr, max_pr],
            opacity=0.85,
            mode="lines",
            connectgaps=True,
            line=PLT_FIB_COLORWAY[8],
            showlegend=False,
            row=1,
            col=1,
            secondary_y=False,
        )
        df_ta2 = df_ta.copy()
        interval = 1440
        if df_ta2.index[-2].date() == df_ta2.index[-1].date():
            interval = (df_ta2.index[1] - df_ta2.index[0]).seconds / 60
            dt_unique_days = df_ta2.index.normalize().unique()

            if interval not in [15, 30, 60] and len(dt_unique_days) <= 3:
                df_ta2 = df_ta2.loc[
                    (df_ta2.index >= dt_unique_days[-1])
                    & (df_ta2.index < datetime.now())
                ].copy()
                df_ta2 = df_ta2.between_time("09:30", "20:00").copy()

        for i in range(7):
            idx_int = 4 if lvl_text == "left" else 5
            text_pos = f"bottom {lvl_text}" if i != idx_int else f"top {lvl_text}"

            if fibs[i] == "<b>0</b>":
                text_pos = (
                    f"top {lvl_text}" if lvl_text != "right" else f"bottom {lvl_text}"
                )
            text = ["", f"<b>{fibs[i]} ({levels[i]:{self.get_float_precision()}})</b>"]
            if lvl_text == "right":
                text = [text[1], text[0]]

            fig.add_scatter(
                name=fibs[i],
                x=[min_date, df_ta2.index.max()],
                y=[levels[i], levels[i]],
                opacity=0.9,
                mode="lines+text",
                text=text,
                textposition=text_pos,
                textfont=dict(PLT_FIB_COLORWAY[7], color=PLT_FIB_COLORWAY[i]),
                line_color=PLT_FIB_COLORWAY[i],
                line_width=1.5,
                showlegend=False,
                row=1,
                col=1,
                secondary_y=False,
            )

        return fig
