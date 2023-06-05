import re
from datetime import date, datetime, timedelta
from typing import Any, Optional, Union
from unittest.mock import patch

import pandas as pd
import streamlit as st
import yfinance as yf
from rich.table import Table

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import (
    common_vars,
    streamlit_helpers as st_helpers,
)
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="Forecasting",
    page_icon="📈",
    initial_sidebar_state="expanded",
)
st_helpers.set_css()
st_helpers.set_current_page("Forecasting")


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


def special_st(text: Optional[str] = None) -> Optional[str]:
    if isinstance(text, Table):
        with table_container:
            text.title = re.sub(st_helpers.REGEX_RICH, "", text.title).replace(
                "Actual price:",
                "<h3 class='table_container'>Actual price:"
                "<text style='color: yellow'>",
            )
            st.write(
                f"{text.title}</text></h3>",
                unsafe_allow_html=True,
            )
            st.table(st_helpers.rich_to_dataframe(text))
    elif isinstance(text, str) and "[green]" in text:
        global PAST_COVERAGE_PRINT  # pylint: disable=W0603 # noqa
        PAST_COVERAGE_PRINT += re.sub(st_helpers.REGEX_RICH, "", text) + "<br>"

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
        st_helpers.load_state("last_tickers", "")
        st_helpers.load_state("last_intervals", "1d")
        st_helpers.load_state("df", pd.DataFrame())
        self.default_opts = {
            key: [] for key in ["target_widget", "column_widget", "past_covs_widget"]
        }
        st_helpers.load_widget_options(self.default_opts)

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

                forecast_model = common_vars.FORECAST_MODEL_OPTS[model]
                contains_covariates = st_helpers.has_parameter(
                    forecast_model, "past_covariates"
                )
                if contains_covariates and past_covariates != []:
                    kwargs["past_covariates"] = ",".join(past_covariates)
                if st_helpers.has_parameter(forecast_model, "output_chunk_length"):
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
                        fig: OpenBBFigure = getattr(
                            common_vars.openbb.forecast, f"{model}_chart"
                        )(**kwargs)

                with plotly_chart:
                    dt_now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = (
                        f"{dt_now}_{tickers}_{model}_{target_column.replace(' ', '_')}"
                    )

                    fig.update_layout(
                        title=dict(x=0.5, xanchor="center", yanchor="top", y=0.99),
                        showlegend=True,
                        margin=dict(t=40, l=30),
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
        self.feature_model = common_vars.FORECAST_FEAT_ENGS[feature]

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
                kwargs = {}
                if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    kwargs.update({"period": "max"})
                else:
                    kwargs.update({"start": start, "end": end + timedelta(days=1)})

                df: pd.DataFrame = yf.download(  # type: ignore
                    tickers,
                    interval=interval,
                    progress=False,
                    **kwargs,
                )
                df = df.dropna()
                if not df.empty:
                    df.index = pd.to_datetime(df.index).tz_localize(None)
                st.session_state["df"] = st_helpers.format_df(df)
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
                "Interval",
                index=0,
                key="interval",
                options=common_vars.INTERVAL_OPTS[3:],
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
        enable_past_covs = st_helpers.has_parameter(
            common_vars.FORECAST_MODEL_OPTS[model], "past_covariates"
        )

        col_order = [r2c3, r2c1, r2c2]
        if enable_past_covs:
            col_order = [r2c1, r2c2, r2c3]

        with col_order[1]:
            target_widget = st.selectbox(
                "Target",
                options=st_helpers.get_widget_options(
                    self.default_opts, "target_widget"
                ),
            )

        with col_order[2]:
            model_widget = st.selectbox(
                "Model",
                options=list(common_vars.FORECAST_MODEL_OPTS),
                key="model",
            )

        past_covs_widget = None
        if enable_past_covs:
            with col_order[0]:
                past_covs_widget = st.multiselect(
                    "Past Covariates",
                    options=st_helpers.get_widget_options(
                        self.default_opts, "past_covs_widget"
                    ),
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
