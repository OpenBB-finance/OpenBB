from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf

from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import streamlit_helpers as st_helpers

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Correlation",
    initial_sidebar_state="expanded",
)

st_helpers.set_current_page("Correlation")
st_helpers.set_css()
st.sidebar.markdown(
    "<h2 style='text-align: center;'>Correlation Analysis</h2>",
    unsafe_allow_html=True,
)


class Chart:
    def __init__(self):
        self.last_tickers = st_helpers.load_state("last_tickers", "")
        self.last_interval = st_helpers.load_state("last_interval", "1d")
        self.df = st_helpers.load_state("df", pd.DataFrame())

    def create(
        self, data: str, tickers: str, start: datetime, end: datetime, interval: str
    ):
        if tickers:
            if tickers != self.last_tickers or interval != self.last_interval:
                kwargs = {}
                if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    kwargs.update({"period": "max"})
                else:
                    kwargs.update({"start": start, "end": end})  # type: ignore

                self.df = yf.download(
                    tickers, interval=interval, progress=False, **kwargs
                )
                self.last_tickers = tickers
                self.last_interval = interval

            start_n = datetime(start.year, start.month, start.day)
            end_n = datetime(end.year, end.month, end.day)

            df = self.df[data]

            if not isinstance(df, pd.Series):
                if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    result = df.loc[(df.index >= start_n) & (df.index <= end_n)].corr()
                else:
                    result = df.corr()

                base = [
                    [
                        "black" if x == 1 else "lightgreen" if x > 0 else "lightpink"
                        for x in result[y].tolist()
                    ]
                    for y in result.columns
                ]
                base = [["lightgray" for _ in range(result.shape[0])]] + base
                result = result.reset_index()
                result.index = result["index"]
                result = result.drop(columns=["index"])

                st.table(result)

    def run(self):
        data_opts = ["Open", "Close", "High", "Low", "Volume"]
        tickers_widget = st.sidebar.text_input(
            "Tickers", "TSLA,AAPL", help="Separate tickers with commas"
        )
        data_widget = st.sidebar.selectbox(
            "Data", data_opts, index=2, help="Data Column to use"
        )

        base_date = datetime.today() - timedelta(days=365)
        start_widget = st.sidebar.date_input("Start", base_date)
        end_widget = st.sidebar.date_input("End", datetime.today())
        interval_opts = ["1d", "5d", "1wk", "1mo", "3mo"]
        interval_widget = st.sidebar.selectbox("Interval", interval_opts, index=0)

        self.create(
            data_widget, tickers_widget, start_widget, end_widget, interval_widget
        )


if __name__ == "__main__":
    Chart().run()
