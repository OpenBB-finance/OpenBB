import asyncio
import re
from datetime import date, datetime, timedelta
from typing import Any, List
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.rich_config import console

# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

# Import the OpenBB SDK
# pylint: disable=wrong-import-position
from openbb_terminal.sdk import openbb  # noqa: E402

pd.options.plotting.backend = "plotly"
st.set_page_config(
    layout="wide",
    page_title="Indicators",
    initial_sidebar_state="expanded",
)

logger = st.empty()
page_title = st.empty()
plotly_chart = st.empty()


TA_CLASS = PlotlyTA()
indicators_opts = sorted(
    [c.name.replace("plot_", "") for c in TA_CLASS if c.name != "plot_ma"]
    + TA_CLASS.ma_mode
)

interval_opts = ["5m", "15m", "30m", "1d"]
source_opts = [
    "AlphaVantage",
    "YahooFinance",
    "EODHD",
    "Polygon",
    "Intrinio",
    "DataBento",
]
MAIN_LOOP: asyncio.AbstractEventLoop = None  # type: ignore


def load_state(name: str, default: Any):
    if name not in st.session_state:
        st.session_state[name] = default


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


async def plot_indicators(
    data: pd.DataFrame, tickers: List[str], indicators: List[str]
) -> OpenBBFigure:
    main_ticker = tickers[0]
    tickers = tickers[1:]
    data = data.copy()

    indicators_dict: dict = {}
    for indicator in indicators:
        indicators_dict[indicator] = st.session_state["indicators_args"].get(
            indicator, {}
        )

    title = (
        f"{main_ticker} Technical Analysis"
        if not tickers
        else f"{main_ticker} Technical Analysis with {', '.join(tickers)}"
    )

    fig = TA_CLASS.plot(
        data,
        indicators_dict,
        main_ticker,
        candles=not tickers,
        volume=not tickers,
        volume_ticks_x=5,
    )

    fig.update_traces(showlegend=False)
    rows = fig.subplots_kwargs["rows"]

    for ticker in tickers:
        ticker = ticker
        df_ticker = st.session_state["indicators_dfs"][ticker]
        df_ticker["% Change"] = df_ticker["Close"].apply(
            lambda x: (x - df_ticker["Close"].iloc[0]) / df_ticker["Close"].iloc[0]
        )

        fig.add_scatter(
            x=df_ticker.index,
            y=df_ticker["% Change"],
            name=f"{ticker} % Change",
            customdata=df_ticker["Close"],
            secondary_y=True,
            connectgaps=True,
            hovertemplate="Close: %{customdata:.2f}<br>%{y:.2%}",
            yaxis=f"y{rows}",
            showlegend=True,
            row=1,
            col=1,
        )

    if tickers:
        fig.update_traces(
            selector=dict(type="scatter", name=f"{main_ticker} Close"), showlegend=True
        )
        fig.update_yaxes(
            selector=dict(title_text="Price ($)"),
            title_text=f"{main_ticker} Price ($)",
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.update_yaxes(
            secondary_y=True,
            showgrid=False,
            showticklabels=True,
            row=1,
            col=1,
            showline=False,
            zeroline=False,
            title_text="% Change",
            ticksuffix=f"{'':>20}",
            side="left",
            tickformat=".2%",
            overlaying="y",
        )

    for annotation in fig.select_annotations(
        selector=dict(xanchor="left", x=0, xref="paper")
    ):
        annotation.xshift += -5

    fig.hide_holidays()

    y_min, y_max = data["Low"].min().min(), data["High"].max().max()
    y_range = y_max - y_min
    y_min -= y_range * 0.05
    y_max += y_range * 0.05

    yaxis = "yaxis" if tickers else "yaxis2"

    fig.update_layout(
        {yaxis: dict(range=[y_min, y_max], autorange=False)},
        title=dict(x=0.5, xanchor="center", yanchor="top", y=0.99, text=title),
        showlegend=True,
        height=650,
    )

    return fig


class Handler:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        default_args = {
            "last_tickers": "",
            "last_interval": "1d",
            "last_source": "YahooFinance",
            "interval": "1d",
            "args": {indicator: {} for indicator in indicators_opts},
            "dfs": {},
        }
        for key, value in default_args.items():
            load_state(f"indicators_{key}", value)

        default_opts = {
            "start_date": date.today() - timedelta(days=365),
            "end_date": date.today(),
            "indicators_tickers": st.session_state["indicators_last_tickers"],
            "indicators_interval": st.session_state["indicators_last_interval"],
            "indicators": [],
            "source": st.session_state["indicators_last_source"],
        }
        for key, value in default_opts.items():
            load_state(key, value)

        self.loop = loop

        global MAIN_LOOP  # noqa
        MAIN_LOOP = loop

    # pylint: disable=R0913
    async def handle_changes(
        self,
        start: date,
        end: date,
        tickers: str,
        indicators: list,
    ):
        tickers_l = tickers.split(",")
        main_ticker = tickers_l[0].upper().strip()
        if (
            not tickers_l
            or st.session_state["indicators_dfs"].get(main_ticker, pd.DataFrame()).empty
        ):
            with logger.empty():
                st.error("Please select at least one valid ticker", icon="🔥")
            return None

        start_n = datetime(start.year, start.month, start.day).date()
        end_n = datetime(end.year, end.month, end.day).date()

        for ticker in tickers_l:
            ticker = ticker.upper().strip()
            st.session_state["indicators_dfs"][ticker] = st.session_state[
                "indicators_dfs"
            ][ticker].loc[
                (st.session_state["indicators_dfs"][ticker].index.date >= start_n)
                & (st.session_state["indicators_dfs"][ticker].index.date <= end_n)
            ]

        result: pd.DataFrame = st.session_state["indicators_dfs"][main_ticker]
        with st.spinner("Calculating indicators..."):
            with patch.object(console, "print", special_st):
                if result.empty:
                    with logger.container():
                        logger.error("There was an error with the data", icon="🔥")
                        await asyncio.sleep(2)
                    return None

                data = pd.DataFrame(result)
                data.index.name = "date"

                if ta_helpers.check_columns(data) is None:
                    return None

                fig = await plot_indicators(data, tickers_l, indicators)

                with plotly_chart.container():
                    last_day = data.loc[data.index.date == data.index.date[-1]]

                    if not last_day.empty:
                        last_day.index = pd.to_datetime(last_day.index).date
                        weeks52 = data.loc[
                            data.index.date >= data.index.date[-1] - timedelta(weeks=52)
                        ]
                        stats_df = pd.DataFrame(
                            {
                                "Open": last_day["Open"].head(1).values[0],
                                "High": last_day["High"].max(),
                                "Low": last_day["Low"].min(),
                                "Close": last_day["Close"].tail(1).values[0],
                                "Volume": last_day["Volume"].sum(),
                                "52 week high": weeks52["High"].values.max(),
                                "52 week low": weeks52["Low"].values.min(),
                            },
                            index=[
                                last_day.tail(1).index.values[0].strftime("%Y-%m-%d")
                            ],
                        )
                        st.table(
                            stats_df.style.format(
                                {"Volume": "{:,.0f}"}, precision=2, thousands=","
                            )
                        )

                    dt_now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{dt_now}_{main_ticker}_technical_analysis"
                    fig.show(external=True, bar_width=0.00001)

                    if list(
                        set(indicators).intersection(
                            set(TA_CLASS.ma_mode + TA_CLASS.inchart)
                        )
                    ):
                        margin = fig.layout.margin
                        margin.l += 30
                        fig.update_layout(margin=margin)

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config=dict(
                            scrollZoom=True,
                            displaylogo=False,
                            toImageButtonOptions=dict(
                                format="png",
                                filename=filename,
                            ),
                        ),
                    )

    async def load_ticker_data(
        self, ticker: str, interval: str, start: date, end: date, source: str
    ):
        kwargs = {}
        if interval == "1d":
            kwargs.update(dict(start_date=start, end_date=end))
        else:
            end + timedelta(days=1)
            kwargs.update(dict(interval=int(interval.replace("m", ""))))  # type: ignore

        with patch.object(console, "print", special_st):
            df = openbb.stocks.load(ticker, **kwargs, source=source)

        if df.empty:
            with logger.container():
                st.error(
                    f"Could not load data for {ticker}. Is it a valid ticker?", icon="❗"
                )
                await asyncio.sleep(2)
            return pd.DataFrame()

        df = df.dropna()
        return df

    def on_ticker_change(self):
        self.loop.run_until_complete(self.async_on_ticker_change())

    async def async_on_ticker_change(self):
        """Load ticker data when ticker changes"""
        new_data = False
        tickers = list(set(st.session_state.indicators_ticker.split(",")))  # type: ignore
        tickers = [ticker.strip().upper() for ticker in tickers if ticker.strip()]  # type: ignore

        try:
            interval = st.session_state.indicators_interval
            source = st.session_state.indicators_source
            start = st.session_state.start_date
            end = st.session_state.end_date
        except AttributeError:
            interval = "1d"
            source = "YahooFinance"
            start = date.today() - timedelta(days=365)
            end = date.today()

        check_last = [
            ("indicators_last_tickers", ",".join(tickers)),
            ("indicators_last_interval", interval),
            ("indicators_last_source", source),
        ]
        new_params = any(
            [st.session_state.get(key, None) != value for key, value in check_last]
        )
        if new_params:
            st.session_state["indicators_dfs"] = {}
            for key, value in check_last:
                st.session_state[key] = value
            new_data = True

        for ticker in tickers:
            if ticker not in st.session_state["indicators_dfs"]:
                st.session_state["indicators_dfs"][
                    ticker
                ] = await self.load_ticker_data(ticker, interval, start, end, source)
                if st.session_state["indicators_dfs"][ticker].empty:
                    indicators_dfs = st.session_state["indicators_dfs"]
                    del indicators_dfs[ticker]
                    st.session_state["indicators_dfs"] = indicators_dfs
                    tickers.remove(ticker)
                else:
                    with logger.container():
                        st.success(f"Loaded data for {ticker}", icon="📈")
                        await asyncio.sleep(0.5)

        if new_data:
            st.session_state["indicators_ticker"] = ",".join(tickers)

    def handle_indicators(self, options_col: DeltaGenerator):
        """Handle the indicators selection"""
        indicators = [
            indicator
            for indicator in list(
                set(st.session_state.indicators).intersection(set(TA_CLASS.ma_mode))
            )
            if not st.session_state["indicators_args"][indicator].get("length", [])
        ]

        for indicator in st.session_state["indicators_args"]:
            if indicator not in indicators:
                st.session_state["indicators_args"][indicator] = {}

        if not indicators:
            return None
        with options_col.container().form("indicators_form", clear_on_submit=True):
            st.write("Select window lengths:")
            for indicator in indicators:
                st.multiselect(
                    f"{indicator.upper()} Lengths",
                    options=[7, 10, 20, 50, 100, 200],
                    key=f"{indicator}_length",
                )
            st.form_submit_button(
                "Submit",
                on_click=self.on_length_submit,
                args=(indicators,),
            )

    def on_length_submit(self, indicators: list):
        """Handle the length submit"""
        for indicator in indicators:
            st.session_state["indicators_args"][indicator] = {
                "length": st.session_state[f"{indicator}_length"]
            }

    async def run(self):
        """Run the app"""

        st.sidebar.markdown(
            "<h2 style='text-align: center;'>OpenBB Technical Analysis</h2>",
            unsafe_allow_html=True,
        )
        ticker = st.sidebar.text_input(
            "Ticker(s) (comma separated)",
            "",
            key="indicators_ticker",
            on_change=self.on_ticker_change,
        )
        data_opts = st.sidebar.expander("Data options")
        length_opts = st.sidebar.container()
        indicators_sideopts = st.sidebar.container()

        with data_opts.container():
            data_opts.selectbox(
                "Source",
                index=1,
                key="indicators_source",
                options=source_opts,
                on_change=self.on_ticker_change,
            )
            start_date = data_opts.date_input(
                "Start date", date.today() - timedelta(days=365), key="start_date"
            )
            end_date = data_opts.date_input("End date", date.today(), key="end_date")

            data_opts.selectbox(
                "Interval",
                index=3,
                key="indicators_interval",
                options=interval_opts,
                on_change=self.on_ticker_change,
            )
        with indicators_sideopts:
            indicators = indicators_sideopts.multiselect(
                "Indicators",
                key="indicators",
                options=indicators_opts,
                on_change=self.handle_indicators,
                kwargs=dict(options_col=length_opts),
            )

        st.sidebar.markdown("""---""")
        if st.sidebar.button("Plot Data"):
            if ticker:
                await self.handle_changes(
                    start_date,
                    end_date,
                    ticker,
                    indicators,
                )
            else:
                with logger.container():
                    logger.error("Please enter a ticker", icon="❗")


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(Handler(loop).run())
