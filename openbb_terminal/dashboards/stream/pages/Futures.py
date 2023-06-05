import calendar
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st
import yfinance as yf

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import streamlit_helpers as st_helpers

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Futures",
    initial_sidebar_state="expanded",
)
st_helpers.set_current_page("Futures")
st_helpers.set_css()

df = pd.read_csv(MISCELLANEOUS_DIRECTORY / "futures" / "futures.csv")

# These are the symbols that futures use for each month
months = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
st.sidebar.markdown(
    "<h2 style='text-align: center;'>Futures Analysis</h2>",
    unsafe_allow_html=True,
)


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")  # noqa

    # pylint: disable=unused-argument
    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa
        sys.stdout.close()
        sys.stdout = self._original_stdout


def format_plotly(fig: OpenBBFigure):
    fig.update_yaxes(title="Price")
    fig.update_xaxes(title="Date")
    fig.update_layout(
        margin=dict(l=0, r=10, t=10, b=10),
        autosize=False,
        width=900,
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


def create_line(visual, x, y, name, fig: OpenBBFigure):
    if visual == "line":
        fig.add_scatter(x=x, y=y, mode="lines", name=name)  # , connectgaps=True
    if visual == "scatter":
        fig.add_scatter(x=x, y=y, mode="markers", name=name)
    if visual == "candle":
        fig.add_candlestick(
            x=x,
            open=y["Open"],
            close=y["Close"],
            high=y["High"],
            low=y["Low"],
            name=name,
        )


def build_ticker(ticker: str, month: int, year: int) -> str:
    if ticker:
        row = df[df["Ticker"] == f"{ticker.split(':')[0]}"].iloc[0]
        row = row.to_dict()
        the_tick = row["Ticker"].replace("=F", "")
        return f"{the_tick}{months[month-1]}{str(year)[-2:]}.{row['Exchange']}"
    return ""


def next_ticker(ticker: str) -> str:
    symbol, exchange = ticker.split(".")
    month = symbol[-3]
    if month == "Z":
        new_month = "F"
        new_year = int(symbol[-2:]) + 1
    else:
        index = months.index(month)
        new_month = months[index + 1]
        new_year = int(symbol[-2:])
    return f"{symbol[:-3]}{new_month}{new_year}.{exchange}"


def get_column(df: pd.DataFrame, column: str):
    sub_df = df.xs(column, level=1, axis=1, drop_level=False)
    sub_df.columns = sub_df.columns.to_flat_index().map(lambda x: x[0])
    sub_df = sub_df.dropna(how="all")
    sub_df = sub_df.sort_index()
    if sub_df.empty:
        return None
    return sub_df


def get_date(x: str) -> datetime:
    ticker, _ = x.split(".")
    month_str = ticker[-3]
    month = months.index(month_str) + 1
    year = int(ticker[-2:]) + 2000
    day = calendar.monthrange(year, month)
    return datetime(year, month, day[1])


CATEGORIES = df["Category"].unique().tolist()
EXCHANGES = df[df["Category"].isin([CATEGORIES[0]])]["Exchange"].unique().tolist()
FILT_DF = df[df["Category"].isin([CATEGORIES[0]]) & df["Exchange"].isin([EXCHANGES[0]])]
TICKERS_RAW = FILT_DF[["Ticker", "Description"]].values.tolist()
TICKERS = [f"{x.replace('=F', '')}: {y}" for x, y in TICKERS_RAW]

CATEGORIES.sort()
EXCHANGES.sort()
TICKERS.sort()


class Chart:
    def __init__(self):
        self.exchange = st_helpers.load_state("exchanges", [EXCHANGES[0]])
        self.tickers = st_helpers.load_state("tickers", {})
        self.last_ticker = st_helpers.load_state("last_ticker", TICKERS[0])
        self.last_exchange = st_helpers.load_state("last_exchange", EXCHANGES[0])
        self.default_opts = {
            "exch_widget": EXCHANGES,
            "tickers_widget": TICKERS,
            "cat_widget": CATEGORIES,
        }
        st_helpers.load_widget_options(self.default_opts)

    def create_stock(self, chart_type, contracts, ticker):
        if not ticker:
            return
        if self.last_ticker != ticker or not self.tickers:
            now = datetime.now()
            clean_ticker = build_ticker(ticker, now.month, now.year)
            if clean_ticker:
                raw_tickers = [clean_ticker]
                for _ in range(36):
                    new_ticker = next_ticker(raw_tickers[-1])
                    raw_tickers.append(new_ticker)
                    raw_ticker = ",".join(raw_tickers)
                with HiddenPrints():
                    # ,period="max"
                    dfs = yf.download(raw_ticker, progress=False)
                self.tickers = {
                    x: {"data": get_column(dfs, x), "date": get_date(x)}
                    for x in raw_tickers
                }
            self.last_ticker = ticker

        fig = OpenBBFigure()
        if chart_type[0][:4] == "Hist":
            for i, (key, item) in enumerate(self.tickers.items()):
                if i == contracts:
                    break
                result = item["data"]
                if result is not None:
                    create_line(
                        visual="line",
                        x=result.index,
                        y=result["Adj Close"],
                        name=key,
                        fig=fig,
                    )
        else:
            x = []
            y = []
            for _, value in self.tickers.items():
                if len(x) > contracts:
                    break
                if value["data"] is None:
                    continue
                x.append(value["date"])
                y.append(value["data"]["Adj Close"].iloc[-1])
            create_line(visual="line", x=x, y=y, name="Future Curve", fig=fig)

        format_plotly(fig)
        fig.show(external=True)
        st.plotly_chart(
            fig,
            use_container_width=True,
            config=dict(
                scrollZoom=True,
                displaylogo=False,
            ),
        )

    def on_change(self):
        category = st.session_state.cat_widget
        exchange = st.session_state.exch_widget

        # Filter exchange widget
        exch_filtered = df[df["Category"].isin(category)]["Exchange"].unique().tolist()
        exch_filtered.sort()
        st.session_state["widget_options"]["exch_widget"] = exch_filtered

        # Filter ticker widget
        filtered = df[df["Category"].isin(category) & df["Exchange"].isin(exchange)]
        tick_raw = filtered[["Ticker", "Description"]].values.tolist()
        tick = [f"{x.replace('=F', '')}: {y}" for x, y in tick_raw]
        tick.sort()
        st.session_state["widget_options"]["tickers_widget"] = tick

    def run(self):
        chart_type = ["Historical Time Series", "Future Curve"]

        st.sidebar.multiselect(
            "Category",
            st_helpers.get_widget_options(self.default_opts, "cat_widget"),
            on_change=self.on_change,
            key="cat_widget",
        )
        st.sidebar.multiselect(
            "Exchange",
            st_helpers.get_widget_options(self.default_opts, "exch_widget"),
            key="exch_widget",
            on_change=self.on_change,
        )
        ticker_widget = st.sidebar.selectbox(
            "Ticker",
            st_helpers.get_widget_options(self.default_opts, "tickers_widget"),
            key="tickers_widget",
            index=0,
        )

        chart_widget = st.sidebar.selectbox(
            "Chart Type", chart_type, key="chart_widget", index=0
        )
        contracts_widget = st.sidebar.slider(
            "Contracts", 1, 24, 6, key="contracts_widget"
        )

        self.create_stock(chart_widget, contracts_widget, ticker_widget)


if __name__ == "__main__":
    Chart().run()
