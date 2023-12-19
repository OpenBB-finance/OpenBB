import asyncio
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import streamlit as st
import yfinance as yf

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import (
    common_vars,
    streamlit_helpers as st_helpers,
)
from openbb_terminal.rich_config import console

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Stocks",
    initial_sidebar_state="expanded",
)
st_helpers.set_current_page("Stocks")

logger = st.empty()
page_title = st.empty()
main_chart, table_container = st.columns([4, 1.5])
volume_chart = st.empty()

MAIN_LOOP: asyncio.AbstractEventLoop = None  # type: ignore


def special_st(text: str):
    rich_color = re.search(r"\[([a-z ]+)\]", text)
    text = re.sub(r"(\[\/{0,1}[a-z ]+\])|(\[\/\])", "", text)

    async def _special_st():
        with logger.container():
            if rich_color:
                color = rich_color.group(1)
                if "green" in color:
                    st.success(text, icon="🎉")
                elif "red" in color:
                    st.error(text, icon="🔥")
                    await asyncio.sleep(5)
                elif "yellow" in color:
                    st.warning(text, icon="⚠️")
                else:
                    st.write(text)
                await asyncio.sleep(4)

    MAIN_LOOP.create_task(_special_st())


st_helpers.set_css()
st.sidebar.markdown(
    "<h2 style='text-align: center;'>Stock Analysis Dashboard</h2>",
    unsafe_allow_html=True,
)
r2c1, r2c2 = st.sidebar.columns([1, 1])
r2c3 = st.sidebar.container()


def format_plotly(
    fig: OpenBBFigure,
    data: str,
    start: datetime,
    end: datetime,
    calc: pd.DataFrame = None,
):
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None)
    start_t = start.strftime("%Y/%m/%d")
    end_t = end.strftime("%Y/%m/%d")
    if calc:
        if len(calc) == 1:
            fig_title = f"{calc[0]} of {data} from {start_t} to {end_t}"
        else:
            fig_title = f"{', '.join(calc)} of {data} from {start_t} to {end_t}"
        height = 400
    else:
        fig_title = "Volume"
        height = 250
    fig.update_layout(
        autosize=False,
        height=height,
        title=dict(
            text=fig_title,
            y=1,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="#F5EFF3",
            borderwidth=1,
            x=0.99,
            xanchor="right",
        ),
    )


def create_line(
    visual: str,
    x: pd.DataFrame,
    y: pd.DataFrame,
    name: str,
    data: str,
    fig: OpenBBFigure,
):
    if visual == "line":
        fig.add_scatter(
            x=x,
            y=y[data],
            mode="lines",
            name=name,
            connectgaps=True,
            hovertemplate="%{y}",
        )
    if visual == "scatter":
        fig.add_scatter(x=x, y=y[data], mode="markers", name=name, hovertemplate="%{y}")
    if visual == "candle":
        fig.add_candlestick(
            x=x,
            open=y["Open"],
            close=y["Close"],
            high=y["High"],
            low=y["Low"],
            name=name,
        )


def show_fig(fig: OpenBBFigure, margin: bool = True, volume: bool = False):
    fig.show(external=True, margin=margin)
    with_container = main_chart if not volume else volume_chart
    with with_container.container():
        st.plotly_chart(
            fig,
            use_container_width=True,
            config=dict(
                scrollZoom=True,
                displaylogo=False,
            ),
        )


def table_data(infos: dict):
    cols = ["Ticker"] + list(infos)
    data = pd.DataFrame(columns=cols)
    data["Ticker"] = [common_vars.STOCKS_CLEAN_ROW[x] for x in common_vars.STOCKS_ROWS]
    for ticker in list(infos):
        data[ticker] = [
            st_helpers.STOCKS_CLEAN_DATA[x](infos[ticker].get(x, None))
            if infos[ticker].get(x, None)
            else st_helpers.STOCKS_CLEAN_DATA[x](
                getattr(yf.Ticker(ticker).fast_info, x, None)
            )
            for x in common_vars.STOCKS_ROWS
        ]
    return data


def stock_data(
    tickers: list, interval: str, start: datetime, end: datetime
) -> pd.DataFrame:
    with patch.object(console, "print", special_st):
        try:
            kwargs = {}
            if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                kwargs.update({"period": "max"})
            else:
                s_start_dt = datetime.utcnow() - timedelta(days=59)
                s_date_start = s_start_dt.strftime("%Y-%m-%d")
                start = s_date_start if s_start_dt.date() > start else start  # type: ignore
                kwargs.update({"start": start, "end": end + timedelta(days=1)})  # type: ignore

            df: pd.DataFrame = yf.download(
                tickers,
                interval=interval,
                progress=False,
                **kwargs,
            )
            if not df.empty:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                return df
        except Exception:  # noqa: S110
            pass
    return pd.DataFrame()


def volume_data(infos: dict, start: datetime, end: datetime, interval: str) -> dict:
    result = {}
    for ticker in infos:
        try:
            df: pd.DataFrame = yf.download(
                ticker, start=start, end=end, interval=interval
            )
            df = df[["Volume"]]
            df = df.rename(columns={"Volume": ticker})
            result[ticker] = df
        except Exception:  # noqa: S110
            pass
    return result


class Chart:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.df: pd.DataFrame = st_helpers.load_state("df", pd.DataFrame())
        self.tickers: str = st_helpers.load_state("tickers", "TSLA")
        self.last_tickers: str = st_helpers.load_state("last_tickers", "")
        self.last_interval: str = st_helpers.load_state("last_interval", "")
        self.infos: dict = st_helpers.load_state("infos", {})
        self.start: datetime = st_helpers.load_state(
            "start_date", (datetime.today() - timedelta(days=365))
        )
        self.end: datetime = st_helpers.load_state("end_date", datetime.now())
        self.calculation: list = st_helpers.load_state("calculation", ["Raw Data"])
        self.data: str = st_helpers.load_state("data", "Close")
        self.rolling: int = st_helpers.load_state("rolling", 60)
        self.chart: str = st_helpers.load_state("chart", "line")

        self.loop = loop

        global MAIN_LOOP  # noqa
        MAIN_LOOP = loop

    def create_stock(self):
        self.tickers = self.tickers.split(",")
        if not self.tickers:
            return st.error("Missing Tickers")
        if self.tickers:
            if self.tickers != self.last_tickers or self.interval != self.last_interval:
                # get stock data
                self.df = stock_data(self.tickers, self.interval, self.start, self.end)
                self.last_tickers = self.tickers
                self.last_interval = self.interval

            fig = OpenBBFigure()
            for item in self.calculation:
                calcs = st_helpers.get_calc(item, self.df, self.rolling)
                if self.interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    result = calcs.loc[
                        (calcs.index >= self.start) & (calcs.index <= self.end)
                    ]
                else:
                    result = calcs

                if len(result.columns) == 6:
                    name = f"{self.tickers[0]} {item}"
                    create_line(self.chart, result.index, result, name, self.data, fig)

                else:
                    for val in result.columns.levels[1]:
                        vals = result.xs(val, axis=1, level=1, drop_level=True)
                        name = f"{val.upper()} {item}"
                        create_line(
                            self.chart, result.index, vals, name, self.data, fig
                        )
            format_plotly(fig, self.data, self.start, self.end, self.calculation)
            fig.update_layout(margin=dict(l=30, r=0, t=25, b=0))
            show_fig(fig, False)

    def create_volume(self):
        result = self.df.loc[
            (self.df.index >= self.start) & (self.df.index <= self.end)
        ]
        fig = OpenBBFigure.create_subplots(
            1, 1, horizontal_spacing=0.001, vertical_spacing=0.001
        )
        if len(result.columns) == 6:
            name = f"{self.tickers[0]}"
            create_line("line", result.index, result, name, "Volume", fig)
        else:
            for val in result.columns.levels[1]:
                vals = result.xs(val, axis=1, level=1, drop_level=True)
                name = f"{val.upper()}"
                create_line("line", result.index, vals, name, "Volume", fig)

        format_plotly(fig, "Volume", self.start, self.end)
        fig.update_layout(margin=dict(l=30, r=0, t=25, b=0))

        show_fig(fig, False)

    def create_table(self):
        if not self.tickers:
            return
        for ticker in self.tickers:
            if ticker not in self.infos:
                try:
                    self.infos[ticker] = yf.Ticker(ticker).info
                except Exception:
                    self.infos[ticker] = {}
                    pass
        delete = [ticker for ticker in self.infos if ticker not in self.tickers]
        for ticker in delete:
            self.infos.pop(ticker)
        result = table_data(self.infos)
        result.index = result.set_index("Ticker").index
        result = result.drop("Ticker", axis=1)
        with table_container:
            st.table(result)

    async def async_on_ticker_change(self):
        new_data = False
        tickers = list(set(st.session_state.tickers.split(",")))  # type: ignore
        tickers = [ticker.upper().strip() for ticker in tickers if ticker.strip()]  # type: ignore

        try:
            interval = st.session_state.interval
        except AttributeError:
            interval = "1d"

        check_last = [
            ("last_tickers", ",".join(tickers)),
            ("last_interval", interval),
        ]
        new_params = any(
            [st.session_state.get(key, None) != value for key, value in check_last]
        )
        if new_params:
            for key, value in check_last:
                st.session_state[key] = value
            new_data = True

        if new_data:
            st.session_state["tickers"] = ",".join(tickers)

    def on_ticker_change(self):
        self.loop.run_until_complete(self.async_on_ticker_change())

    async def run(self):
        tickers = st.sidebar.text_input(
            "Ticker(s) (comma separated)",
            "",
            key="tickers",
            on_change=self.on_ticker_change,
            help="Enter a comma separated list of tickers",
        )
        date_opts = st.sidebar.expander("Date options")
        data_opts = st.sidebar.expander("Data options")
        (
            r1c2,
            r1c3,
        ) = date_opts.columns([1, 1])

        r1c4, r1c5 = data_opts.columns([1, 1])

        with date_opts.container():
            with r1c2:
                self.start = st.date_input(
                    "Start", (datetime.today() - timedelta(days=365)), key="start_date"
                )
            with r1c3:
                self.end = st.date_input("End", datetime.today(), key="end_date")
            self.interval = st.selectbox(
                "Interval", common_vars.INTERVAL_OPTS[1:], index=2, key="interval"
            )

        with data_opts.container():
            with r1c4:
                self.data = st.selectbox(
                    "Target", ["Open", "Close", "High", "Low"], index=1, key="data"
                )
            with r1c5:
                self.chart = st.selectbox(
                    "Chart", ["line", "scatter", "candle"], index=0, key="chart"
                )
            self.calculation = st.multiselect(
                "Calculations",
                list(common_vars.STOCKS_VIEWS.keys()),
                ["Raw Data"],
                key="calculation",
            )
            self.rolling = st.number_input("Rolling", 3, 100, 60, key="rolling")

        st.sidebar.markdown("""---""")
        submit_button = st.sidebar.button("Display")
        if submit_button and tickers:
            self.start = datetime.combine(self.start, datetime.min.time())
            self.end = datetime.combine(self.end, datetime.max.time())
            self.create_stock()
            self.create_volume()
            self.create_table()


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(Chart(loop).run())
