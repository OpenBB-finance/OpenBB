import asyncio
import io
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure, theme
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import streamlit_helpers as st_helpers

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Short Data",
    initial_sidebar_state="expanded",
)
st.sidebar.markdown(
    "<h2 style='text-align: center;'>Finra Short Data</h2>",
    unsafe_allow_html=True,
)
TICKER = st.sidebar.container()
DAYS = st.sidebar.container()
COUNT = st.sidebar.container()

load_button, ticker_button, show_button = st.sidebar.columns([1, 1, 1])
output1 = st.empty()
output2 = st.empty()
title_html = """
<p><strong style="color: #00ACFF">Load Data:</strong> <br>
This widget downloads the consolidated NMS short data from FINRA and aggregates
the data by summing over the entire time period.</p>
<p>Note that clicking the this button will reload all data.
This can get time consuming, so if you pick a few hundred days,
expect a few minutes for loading time.</p>
"""
middle_html = """

<strong style="color: #00ACFF">Plot Ticker:</strong> <br>Query for a single stock.  This will work with the loaded data.
Note that if you want to reload the data, this will once again take some time.
"""
st.markdown(title_html, unsafe_allow_html=True)

st.markdown(middle_html, unsafe_allow_html=True)

MAIN_LOOP: asyncio.AbstractEventLoop = None  # type: ignore

st_helpers.set_current_page("Short Data")
st_helpers.set_css()


class FinraShortData:
    def __init__(self, days_slider=30, count_slider=10):
        self.df = st_helpers.load_state("df", pd.DataFrame())
        self.days_slider = st_helpers.load_state("days_slider", days_slider)
        self.count_slider = st_helpers.load_state("count_slider", count_slider)
        self.ticker_button = None
        self.load_button = None
        self.show_button = None
        self.loaded = False

    def activate_buttons(self):
        if not self.loaded:
            with ticker_button.container():
                self.ticker_button = ticker_button.button(
                    "Plot Ticker", key="ticker_button"
                )
            with show_button.container():
                self.show_button = show_button.button("Show", key="show_button")
            self.loaded = True

    def show_button_click(self):
        output1.empty()
        self.update()

    def load_button_click(self):
        output1.empty()
        output2.empty()
        with st.spinner(f"Loading data for {self.days_slider} days"):
            self.fetch_new_data()
            self.update()

    def ticker_button_click(self):
        output2.empty()
        self.ticker_plot()

    def fetch_new_data(self):
        self.df = pd.DataFrame()
        today = datetime.now().date()
        start_date = today - timedelta(days=self.days_slider)
        dates = pd.date_range(start_date, today)
        for date in dates:
            r = requests.get(
                f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date.strftime('%Y%m%d')}.txt",
                timeout=30,
            )
            if r.status_code == 200:
                self.df = pd.concat(
                    [self.df, pd.read_csv(io.StringIO(r.text), sep="|")], axis=0
                )

        self.df = self.df[self.df.Date > 20100101]
        self.df.Date = self.df["Date"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d")
        )
        st_helpers.save_state("df", self.df)

    def update(self):
        if not self.df.empty:
            temp = (
                self.df.groupby("Symbol")[["ShortVolume", "TotalVolume"]]
                .agg("sum")
                .sort_values(by="ShortVolume", ascending=False)
                .head(self.count_slider)[::-1]
            )
            fig = OpenBBFigure()
            fig.add_bar(
                x=temp.TotalVolume,
                y=temp.index,
                orientation="h",
                name="Total Volume",
                marker_color=theme.up_color,
            )
            fig.add_bar(
                x=temp.ShortVolume,
                y=temp.index,
                orientation="h",
                name="Short Volume",
                marker_color=theme.down_color,
            )
            fig.update_layout(
                title=f"Top {self.count_slider} Short Volume in Last {self.days_slider} Days",
                margin=dict(l=30),
                xaxis_title="Volume",
                yaxis_title="Ticker",
                barmode="stack",
                bargap=0.1,
                hovermode="y unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )
            fig.show(external=True)
            with output1:
                st.plotly_chart(fig, use_container_width=True)

    def ticker_plot(self):
        stock_data = self.df.copy().loc[
            self.df.Symbol == self.stock_input.upper(),
            ["Date", "ShortVolume", "TotalVolume"],
        ]
        fig2 = OpenBBFigure()
        fig2.add_scatter(
            x=stock_data.Date,
            y=stock_data.TotalVolume,
            name="Total Volume",
            marker_color=theme.up_color,
        )
        fig2.add_scatter(
            x=stock_data.Date,
            y=stock_data.ShortVolume,
            name="Short Volume",
            marker_color=theme.down_color,
        )
        fig2.update_layout(
            title=f"Stock Volume and Short Volume for {self.stock_input.upper()}",
            margin=dict(l=30),
            xaxis_title="Date",
            yaxis_title="Volume",
        )
        fig2.show(external=True)
        with output2:
            st.plotly_chart(fig2)

    def build_app(self):
        with TICKER:
            self.stock_input = TICKER.text_input("Ticker", "GME", key="ticker")
        with DAYS:
            self.days_slider = DAYS.slider(
                "Days", 1, 1000, 100, help="Number of days to load"
            )
        with COUNT:
            self.count_slider = COUNT.slider(
                "Count", 1, 100, 20, help="Number of stocks to plot"
            )

        with load_button.container():
            self.load_button = load_button.button("Load Data", key="load")

        if not self.df.empty:
            self.activate_buttons()

        if self.load_button:
            self.load_button_click()
        if self.show_button:
            self.show_button_click()
        if self.ticker_button:
            self.ticker_button_click()

        if not self.df.empty:
            self.activate_buttons()


if __name__ == "__main__":
    app = FinraShortData()
    app.build_app()
