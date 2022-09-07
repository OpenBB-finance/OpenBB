from unittest.mock import patch
from datetime import timedelta, datetime
from typing import Callable, Any
from inspect import signature
import streamlit as st
import pandas as pd
import yfinance as yf
from openbb_terminal import api
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console


model_opts = {
    "expo": api.forecast.models.expo.get_expo_data,  # type: ignore
    "theta": api.forecast.models.theta.get_theta_data,  # type: ignore
    "linregr": api.forecast.models.linregr.get_linear_regression_data,  # type: ignore
    "regr": api.forecast.models.regr.get_regression_data,  # type: ignore
    "rnn": api.forecast.models.rnn.get_rnn_data,  # type: ignore
    "brnn": api.forecast.models.brnn.get_brnn_data,  # type: ignore
    "nbeats": api.forecast.models.nbeats.get_NBEATS_data,  # type: ignore
    "tcn": api.forecast.models.tcn.get_tcn_data,  # type: ignore
    "trans": api.forecast.models.trans.get_trans_data,  # type: ignore
    "tft": api.forecast.models.tft.get_tft_data,  # type: ignore
}

feat_engs = {
    "ema": api.forecast.ema,
    "sto": api.forecast.sto,
    "rsi": api.forecast.rsi,
    "roc": api.forecast.roc,
    "mom": api.forecast.mom,
    "atr": api.forecast.atr,
    "delta": api.forecast.delta,
    "signal": api.forecast.signal,
}

interval_opts = [
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
]


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


@st.cache(suppress_st_warning=True)
def run_forecast(data: pd.DataFrame, model: str, target_column: str):
    if helpers.check_data(data, target_column):

        response = model_opts[model](
            data=data,
            target_column=target_column,
        )
        if model == "theta":
            (
                ticker_series,
                historical_fcast,
                predicted_values,
                precision,
                _,
                _model,
            ) = response
        else:
            (
                ticker_series,
                historical_fcast,
                predicted_values,
                precision,
                _model,
            ) = response
        if model in ["expo", "linregr", "rnn", "tft"]:
            predicted_values = predicted_values.quantile_df()[
                f"{target_column}_0.5"
            ].tail(5)
        else:
            predicted_values = predicted_values.pd_dataframe()[target_column].tail(5)
        return (
            historical_fcast.pd_dataframe(),
            ticker_series.pd_dataframe(),
            pd.DataFrame(predicted_values),
        )
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


class Handler:
    def __init__(self):
        load_state("last_tickers", "")
        load_state("last_intervals", "1d")
        load_state("df", pd.DataFrame())
        default_opts = {
            key: [] for key in ["target_widget", "column_widget", "past_covs_widget"]
        }
        load_state("widget_options", default_opts)

        # Define widgets:
        self.ticker: str = None
        self.start_date: str = None
        self.end_date: str = None
        self.past_covs_widget: str = None
        self.target_widget: str = None
        self.target_interval: str = None
        self.model_widget: str = None

    def handle_changes(
        self,
        past_covariates: list[str],
        start,
        end,
        interval,
        tickers,
        target_column,
        model,
        naive,
        forecast_only,
    ):
        if tickers:
            forecast_model = model_opts[model]
            contains_covariates = has_parameter(forecast_model, "past_covariates")

            start_n = datetime(start.year, start.month, start.day)
            end_n = datetime(end.year, end.month, end.day)
            if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                result = st.session_state["df"].loc[
                    (st.session_state["df"]["date"] >= start_n)
                    & (st.session_state["df"]["date"] <= end_n)
                ]
            else:
                result = st.session_state["df"]
            if not target_column:
                target_column = st.session_state["df"].columns[0]
            kwargs = {}
            if contains_covariates and past_covariates != "":
                kwargs["past_covariates"] = ",".join(past_covariates)
            if has_parameter(forecast_model, "naive"):
                kwargs["naive"] = naive
            if has_parameter(forecast_model, "forecast_only"):
                kwargs["forecast_only"] = forecast_only
            with patch.object(console, "print", st.write):
                if helpers.check_data(result, target_column):
                    final_df = helpers.clean_data(result, None, None)
                    hist_fcast, tick_series, pred_vals = run_forecast(
                        final_df, model, target_column
                    )
                    hist_fcast.columns = ["Historical Forecast"]
                    tick_series.columns = ["Past Prices"]
                    pred_vals.columns = ["Prediction Values"]
                    final = pd.concat(
                        [hist_fcast, tick_series, pred_vals], axis=1, join="outer"
                    )
                    if not final.empty:
                        # Styled write() with sig figs
                        st.write(pred_vals.style.format({"Prediction Values": "{:.2f}"}))
                        st.line_chart(final)

                    else:
                        st.write("There was an error with the data")

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
        st.session_state["widget_options"]["target_widget"] = [
            x for x in st.session_state["df"] if x != "date"
        ]
        st.session_state["widget_options"]["past_covs_widget"] = [
            x for x in st.session_state["df"] if x != "date"
        ]
        st.session_state["widget_options"]["column_widget"] = [
            x for x in st.session_state["df"] if x != "date"
        ]

    def run(self):
        st.title("Forecast")
        r1c1, r1c2, r1c3, r1c4 = st.columns([2, 1, 1, 1])
        r2c1, r2c2, r2c3 = st.columns([1, 1, 1])
        with r1c1:
            self.ticker = st.text_input(
                "Ticker", "", key="ticker", on_change=self.on_ticker_change
            )
        with r1c2:
            self.start_date = st.date_input(
                "Start date", pd.to_datetime("2020-01-01"), key="start"
            )
        with r1c3:
            self.end_date = st.date_input(
                "End date", pd.to_datetime("2020-12-01"), key="end"
            )
        with r1c4:
            self.target_interval = st.selectbox(
                "Interval", index=8, key="interval", options=interval_opts
            )
        with r2c1:
            self.past_covs_widget = st.multiselect(
                "Past Covariates",
                options=st.session_state["widget_options"]["past_covs_widget"],
            )
        with r2c2:
            self.target_widget = st.selectbox(
                "Target", options=st.session_state["widget_options"]["target_widget"]
            )
        with r2c3:
            self.model_widget = st.selectbox("Model", options=list(model_opts))
        if st.button("Get forecast"):
            if self.ticker:
                self.handle_changes(
                    [],
                    start=self.start_date,
                    end=self.end_date,
                    interval=self.target_interval,
                    tickers=self.ticker,
                    target_column=self.target_widget,
                    model=self.model_widget,
                    naive=False,
                    forecast_only=False,
                )
            else:
                st.write("Please select a ticker")

            # TODO need to new add in business days and merge to make new DF before plotting
            # create df with 5 next business days from a start date
            # next_business_days = pd.date_range(start=end_date, periods=5, freq="B")

        """
        if st.button("Add Column"):
            kwargs = {}
            if has_parameter(handler.feature_model, "target_column"):
                kwargs["target_column"] = handler.feature_target
            handler.df = handler.feature_model(handler.df, **kwargs)
            st.session_state["widget_options"]["past_covs_widget"] = handler.df.columns
        """


if __name__ == "__main__":
    handler = Handler()
    handler.run()
