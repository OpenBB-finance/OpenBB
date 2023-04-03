import re
from datetime import date, datetime, timedelta
from inspect import signature
from typing import Any, Callable, Optional, Union
from unittest.mock import patch

import pandas as pd
import streamlit as st
import yfinance as yf
from rich.table import Table

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

# Import the OpenBB SDK
# pylint: disable=wrong-import-position
from openbb_terminal.sdk import openbb  # noqa: E402

st.set_page_config(
    layout="wide",
    page_title="Forecasting",
    page_icon="📈",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

css_container_style = """
<style>
    .table_container {
        position: relative;
        text-align: center;
        align-items: center;
        margin-right: 20px;
        top: 20px;
        font-size: 14px;
        color: white;
    }
    .cov-legend {
        position: relative;
        text-align: center;
        align-items: center;
        top: 20px;
        left: 40px;
        font-size: 16px;
        color: green;
    }
</style>
"""
st.markdown(css_container_style, unsafe_allow_html=True)

# pylint: disable=E1101
model_opts = {
    "expo": openbb.forecast.expo,  # type: ignore
    "theta": openbb.forecast.theta,  # type: ignore
    "linregr": openbb.forecast.linregr,  # type: ignore
    "regr": openbb.forecast.regr,  # type: ignore
    "rnn": openbb.forecast.rnn,  # type: ignore
    "brnn": openbb.forecast.brnn,  # type: ignore
    "nbeats": openbb.forecast.nbeats,  # type: ignore
    "tcn": openbb.forecast.tcn,  # type: ignore
    "trans": openbb.forecast.trans,  # type: ignore
    "tft": openbb.forecast.tft,  # type: ignore
}

feat_engs = {
    "ema": openbb.forecast.ema,  # type: ignore
    "sto": openbb.forecast.sto,  # type: ignore
    "rsi": openbb.forecast.rsi,  # type: ignore
    "roc": openbb.forecast.roc,  # type: ignore
    "mom": openbb.forecast.mom,  # type: ignore
    "atr": openbb.forecast.atr,  # type: ignore
    "delta": openbb.forecast.delta,  # type: ignore
    "signal": openbb.forecast.signal,  # type: ignore
}
# pylint: enable=E1101

# Add these: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
interval_opts = ["1d", "5d", "1wk", "1mo", "3mo"]
REGEX_RICH = re.compile(r"\[\/{0,1}[a-zA-Z0-9#]+\]|\[\/\]")
EXPLAINABILITY_FIGURE: Union[OpenBBFigure, None] = None
PAST_COVERAGE_PRINT: str = "<br>"

# Rows and columns for the dashboard layout
st.sidebar.markdown(
    "<h2 style='text-align: center;'>OpenBB Forecasting</h2>",
    unsafe_allow_html=True,
)
r1c1 = st.sidebar.container()
(
    r1c2,
    r1c3,
) = st.sidebar.columns([1, 1])

r1c4, r1c5 = st.sidebar.columns([1, 1])
r2c1, r2c2 = st.sidebar.columns([1, 1])
r2c3 = st.sidebar.container()

st.sidebar.markdown("""---""")
forecast_button = st.sidebar.button("Get forecast")

plotly_chart, table_container = st.columns([4, 1])
explainability, past_cov_legend = st.columns([4, 1])


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    if len(df.columns) != 6:
        df.columns = ["_".join(col).strip() for col in df.columns.values]
    df.reset_index(inplace=True)
    df.columns = [x.lower() for x in df.columns]
    return df


def has_parameter(func: Callable[..., Any], parameter: str) -> bool:
    params = signature(func).parameters
    parameters = params.keys()
    return parameter in parameters


def load_state(name: str, default: Any):
    if name not in st.session_state:
        st.session_state[name] = default


def rich_to_dataframe(table: Table) -> pd.DataFrame:
    columns = [column.header for column in table.columns]
    rows: dict = {column: [] for column in columns}
    for column in table.columns:
        for cell in column.cells:
            text: str = re.sub(REGEX_RICH, "", cell)  # type: ignore
            rows[column.header].append(text)

    df = pd.DataFrame(rows, columns=columns)
    if "Datetime" in df.columns:
        df.index = pd.to_datetime(df["Datetime"]).dt.date
        df.drop("Datetime", axis=1, inplace=True)

    return df


def special_st(text: Optional[str] = None) -> Optional[str]:
    if isinstance(text, Table):
        with table_container:
            text.title = re.sub(REGEX_RICH, "", text.title).replace(
                "Actual price:",
                "<h3 class='table_container'>Actual price:"
                "<text style='color: yellow'>",
            )
            st.write(
                f"{text.title}</text></h3>",
                unsafe_allow_html=True,
            )
            st.table(rich_to_dataframe(text))
    elif isinstance(text, str) and "[green]" in text:
        global PAST_COVERAGE_PRINT  # pylint: disable=W0603 # noqa
        PAST_COVERAGE_PRINT += re.sub(REGEX_RICH, "", text) + "<br>"

    return text


def mock_show(self: OpenBBFigure, *args, **kwargs):  # pylint: disable=W0613
    if "Target" not in self.layout.title.text:
        return self

    # pylint: disable=W0603
    global EXPLAINABILITY_FIGURE  # noqa
    EXPLAINABILITY_FIGURE = self
    return self


class Handler:
    def __init__(self):
        load_state("last_tickers", "")
        load_state("last_intervals", "1d")
        load_state("df", pd.DataFrame())
        default_opts = {
            key: [] for key in ["target_widget", "column_widget", "past_covs_widget"]
        }
        load_state("widget_options", default_opts)

        self.feature_model = None
        self.feature_target = None

    # pylint: disable=R0913
    def handle_changes(
        self,
        past_covariates: list[str],
        start: date,
        end: date,
        interval: str,
        tickers: str,
        target_column: str,
        model: str,
        n_predict: int,
        naive: bool,
        forecast_only: bool,
    ):
        del naive, forecast_only
        if not tickers and not target_column:
            return

        start_n = datetime(start.year, start.month, start.day).date()
        end_n = datetime(end.year, end.month, end.day).date()

        if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
            result = st.session_state["df"].loc[
                (st.session_state["df"]["date"].dt.date >= start_n)
                & (st.session_state["df"]["date"].dt.date <= end_n)
            ]
        else:
            result = st.session_state["df"]

        # we format the datatime column to be a string
        # otherwise the model will throw an error
        result["date"] = result["date"].dt.date.astype(str)

        if not target_column:
            target_column = st.session_state["df"].columns[0]

        with patch.object(console, "print", special_st):
            if helpers.check_data(result, target_column):
                final_df = helpers.clean_data(result)
                kwargs: dict[str, Any] = {}

                forecast_model = model_opts[model]
                contains_covariates = has_parameter(forecast_model, "past_covariates")
                if contains_covariates and past_covariates != []:
                    kwargs["past_covariates"] = ",".join(past_covariates)
                if has_parameter(forecast_model, "output_chunk_length"):
                    kwargs["output_chunk_length"] = n_predict

                if final_df.empty:
                    st.warning("There was an error with the data")
                    return

                # n_predict and output_chunk_length must be the same if there are past covariates
                # run a spinner while we wait for the model to run
                kwargs = dict(
                    data=final_df,
                    target_column=target_column,
                    n_predict=n_predict,
                    dataset_name=tickers.upper(),
                    **kwargs,
                    external_axes=True,
                )

                with st.spinner("Running model..."):
                    with patch.object(OpenBBFigure, "show", mock_show):
                        fig: OpenBBFigure = getattr(openbb.forecast, f"{model}_chart")(
                            **kwargs
                        )

                with plotly_chart:
                    dt_now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = (
                        f"{dt_now}_{tickers}_{model}_{target_column.replace(' ', '_')}"
                    )

                    fig.update_layout(
                        title=dict(x=0.5, xanchor="center", yanchor="top", y=0.99),
                        showlegend=True,
                        margin=dict(t=40),
                        height=500,
                        legend=dict(
                            bgcolor="rgba(0,0,0,0.5)",
                            bordercolor="#F5EFF3",
                            borderwidth=1,
                            x=0.99,
                            xanchor="right",
                        ),
                    )
                    fig.show(external=True)
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
                with explainability:
                    if EXPLAINABILITY_FIGURE:
                        fig2 = EXPLAINABILITY_FIGURE

                        fig2.show(external=True)
                        fig2.update_layout(
                            margin=dict(r=190, l=30),
                            showlegend=True,
                            height=600,
                            width=1000,
                        )
                        st.plotly_chart(
                            EXPLAINABILITY_FIGURE,
                            config=dict(
                                scrollZoom=True,
                                displaylogo=False,
                                toImageButtonOptions=dict(
                                    format="png",
                                    filename=filename,
                                ),
                            ),
                        )
                with past_cov_legend:
                    global PAST_COVERAGE_PRINT  # pylint: disable=W0603 # noqa
                    text = PAST_COVERAGE_PRINT
                    if text != "<br>":
                        st.write(
                            f"<text class='cov-legend'>{text}</text>",
                            unsafe_allow_html=True,
                        )
                        PAST_COVERAGE_PRINT = "<br>"

    def handle_eng(self, target, feature):
        self.feature_target = target
        self.feature_model = feat_engs[feature]

    def on_ticker_change(self):
        tickers = st.session_state.ticker
        if tickers:
            interval = st.session_state.interval
            start = st.session_state.start
            end = st.session_state.end
            if (
                tickers != st.session_state["last_tickers"]
                or interval != st.session_state["last_interval"]
            ):
                if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    df = yf.download(
                        tickers, period="max", interval=interval, progress=False
                    )
                else:
                    end_date = end + timedelta(days=1)
                    df = yf.download(
                        tickers,
                        start=start,
                        end=end_date,
                        interval=interval,
                        progress=False,
                    )
                df = df.dropna()
                st.session_state["df"] = format_df(df)
                st.session_state["last_tickers"] = tickers
                st.session_state["last_interval"] = interval
        st.session_state["widget_options"]["target_widget"] = sorted(
            [x for x in st.session_state["df"] if x != "date"]
        )
        st.session_state["widget_options"]["past_covs_widget"] = sorted(
            [x for x in st.session_state["df"] if x != "date"]
        )
        st.session_state["widget_options"]["column_widget"] = sorted(
            [x for x in st.session_state["df"] if x != "date"]
        )

    def run(self):
        with r1c1:
            ticker = st.text_input(
                "Ticker", "", key="ticker", on_change=self.on_ticker_change
            )
        with r1c2:
            start_date = st.date_input(
                "Start date", date.today() - timedelta(weeks=104), key="start"
            )
        with r1c3:
            end_date = st.date_input("End date", date.today(), key="end")
        with r1c4:
            target_interval = st.selectbox(
                "Interval", index=0, key="interval", options=interval_opts
            )
        with r1c5:
            n_predict = st.selectbox(
                "Prediction Days", index=3, key="n_predict", options=list(range(2, 31))
            )

        model = (
            "expo"
            if not hasattr(st.session_state, "model")
            else st.session_state["model"]
        )
        enable_past_covs = has_parameter(model_opts[model], "past_covariates")

        col_order = [r2c3, r2c1, r2c2]
        if enable_past_covs:
            col_order = [r2c1, r2c2, r2c3]

        with col_order[1]:
            target_widget = st.selectbox(
                "Target",
                options=st.session_state["widget_options"]["target_widget"],
            )

        with col_order[2]:
            model_widget = st.selectbox(
                "Model",
                options=list(model_opts),
                key="model",
            )

        past_covs_widget = None
        if enable_past_covs:
            with col_order[0]:
                past_covs_widget = st.multiselect(
                    "Past Covariates",
                    options=st.session_state["widget_options"]["past_covs_widget"],
                    disabled=not enable_past_covs,
                    label_visibility="hidden" if not enable_past_covs else "visible",
                )

        if forecast_button:
            # pylint: disable=W0603
            global EXPLAINABILITY_FIGURE  # noqa
            EXPLAINABILITY_FIGURE = None
            if ticker:
                self.handle_changes(
                    past_covariates=past_covs_widget,
                    start=start_date,
                    end=end_date,
                    interval=target_interval,
                    tickers=ticker,
                    target_column=target_widget,
                    model=model_widget,
                    n_predict=n_predict,
                    naive=False,
                    forecast_only=False,
                )
            else:
                st.write("Please select a ticker")

            # TODO need to new add in business days and merge to make new DF before plotting
            # create df with 5 next business days from a start date
            # next_business_days = pd.date_range(start=end_date, periods=5, freq="B")

        # if st.button("Add Column"):
        # kwargs = {}
        # if has_parameter(handler.feature_model, "target_column"):
        # kwargs["target_column"] = handler.feature_target
        # handler.df = handler.feature_model(handler.df, **kwargs)
        # st.session_state["widget_options"]["past_covs_widget"] = handler.df.columns


if __name__ == "__main__":
    handler = Handler()
    handler.run()
