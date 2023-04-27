import pandas as pd
import streamlit as st
import yfinance

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import streamlit_helpers as st_helpers

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Chains",
    initial_sidebar_state="expanded",
)
st_helpers.set_current_page("Chains")
st_helpers.set_css()

st.sidebar.markdown(
    "<h2 style='text-align: center;'>Option Chain Dashboard</h2>",
    unsafe_allow_html=True,
)
st.sidebar.write("Select a ticker and expiry to view the option chain")
TICKER_WIDGET = st.sidebar.empty()
EXPIRY_WIDGET = st.sidebar.empty()
INST_WIDGET = st.sidebar.empty()
X_WIDGET = st.sidebar.empty()
Y_WIDGET = st.sidebar.empty()

OPTS = [
    "lastTradeDate",
    "strike",
    "lastPrice",
    "bid",
    "ask",
    "change",
    "percentChange",
    "volume",
    "openInterest",
    "impliedVolatility",
]


def clean_str(string):
    new_str = ""
    for letter in string:
        if letter.isupper():
            new_str += " "
        new_str += letter
    return new_str.title()


def format_plotly(fig: OpenBBFigure, x, y, ticker, expiry, inst):
    fig.update_yaxes(title=clean_str(y))
    fig.update_xaxes(title=clean_str(x))
    expires = ", ".join(expiry)
    title = (
        f"{clean_str(y)} vs. {clean_str(x)} for {ticker.upper()} {inst}s on {expires}"
    )
    fig.update_layout(
        margin=dict(t=40),
        autosize=False,
        width=1000,
        height=500,
        title=dict(
            text=title,
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
    )


class Chart:
    def __init__(self):
        self.stock = st_helpers.load_state("stock", {})
        self.last_ticker = st_helpers.load_state("last_ticker", "")
        self.expiry = st_helpers.load_state("expiry", [])
        self.dfs = st_helpers.load_state("dfs", {})
        self.options = st_helpers.load_state("options", [])

    def update(self, ticker, inst, x, y):
        if self.expiry:
            fig = OpenBBFigure()
            for expire in self.expiry:
                if expire not in self.dfs:
                    self.dfs[expire] = self.stock.option_chain(expire)
                group = self.dfs[expire]
                df = group.calls if inst == "Call" else group.puts

                fig.add_scatter(
                    x=df[x],
                    y=df[y],
                    mode="lines",
                    connectgaps=True,
                    name=expire,
                )

            format_plotly(fig, x, y, ticker, self.expiry, inst)
            fig.update_layout(margin=dict(l=40))
            st.plotly_chart(fig, use_container_width=True)

    def on_change(self):
        ticker = st_helpers.load_state("ticker", "")
        if ticker and ticker != self.last_ticker:
            stock = yfinance.Ticker(ticker)
            self.options = list([*stock.options])
            st_helpers.save_state("options", self.options)
            self.last_ticker = ticker
            st_helpers.save_state("last_ticker", self.last_ticker)
            self.stock = stock
            st_helpers.save_state("stock", self.stock)

    def run(self):
        with TICKER_WIDGET.container():
            ticker = TICKER_WIDGET.text_input(
                "Ticker", key="ticker", on_change=self.on_change
            )
        if self.options:
            with EXPIRY_WIDGET.container():
                exp = EXPIRY_WIDGET.multiselect(
                    "Expiry",
                    st_helpers.load_state("options", []),
                    key="exp",
                    default=self.options[0] if self.options else None,
                )
                self.expiry = exp

        with INST_WIDGET.container():
            inst = INST_WIDGET.selectbox("Type", ["Put", "Call"])

        with X_WIDGET.container():
            x = X_WIDGET.selectbox("X", OPTS, index=1)
        with Y_WIDGET.container():
            y = Y_WIDGET.selectbox("Y", OPTS, index=3)

        self.update(ticker, inst, x, y)


if __name__ == "__main__":
    Chart().run()
