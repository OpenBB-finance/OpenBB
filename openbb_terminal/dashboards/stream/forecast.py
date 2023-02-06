from datetime import date, datetime, timedelta
from inspect import signature
from typing import Any, Callable
from unittest.mock import patch

import pandas as pd
import streamlit as st
import yfinance as yf

from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console
from openbb_terminal.sdk import openbb

st.set_page_config(layout="wide")

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


def special_st(text: str):
    if "[green]" not in text:
        st.write(text)


def run_forecast(
    data: pd.DataFrame,
    model: str,
    target_column: str,
    past_covariates: list[str],
    n_predict: int,
):
    if helpers.check_data(data, target_column):
        # TODO: let the user choose their own n_predict
        kwargs: dict[str, Any] = {}
        forecast_model = model_opts[model]
        contains_covariates = has_parameter(forecast_model, "past_covariates")
        if contains_covariates and past_covariates != []:
            kwargs["past_covariates"] = ",".join(past_covariates)
        if has_parameter(forecast_model, "output_chunk_length"):
            kwargs["output_chunk_length"] = n_predict

        # n_predict and output_chunk_length must be the same if there are past covariates
        # run a spinner while we wait for the model to run
        with st.spinner("Running model..."):
            response = forecast_model(
                data=data,
                target_column=target_column,
                n_predict=n_predict,
                **kwargs,
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
        del precision
        if model in ["expo", "linregr", "rnn", "tft"]:
            predicted_values = predicted_values.quantile_df()[f"{target_column}_0.5"]
        else:
            predicted_values = predicted_values.pd_dataframe()[target_column]
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

        self.feature_model = None
        self.feature_target = None

    # pylint: disable=R0913
    def handle_changes(
        self,
        past_covariates: list[str],
        start,
        end,
        interval,
        tickers,
        target_column,
        model,
        n_predict,
        naive,
        forecast_only,
    ):
        del naive, forecast_only
        if tickers and target_column:
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
                    hist_fcast, tick_series, pred_vals = run_forecast(
                        final_df, model, target_column, past_covariates, n_predict
                    )
                    hist_fcast.columns = ["Historical Forecast"]
                    tick_series.columns = ["Past Prices"]
                    pred_vals.columns = ["Prediction Values"]
                    final = pd.concat(
                        [hist_fcast, tick_series, pred_vals], axis=1, join="outer"
                    )
                    if not final.empty:
                        if helpers.check_dates(pred_vals.index.to_series()):
                            pred_vals.index = pred_vals.index.date
                        rowc1, rowc2 = st.columns([4, 1])
                        # Styled write() with sig figs
                        with rowc2:
                            st.write(
                                pred_vals.style.format({"Prediction Values": "{:.2f}"})
                            )
                        with rowc1:
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
        st.title("OpenBB Forecasting")  # Title does not like being in a column

        r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([2, 1, 1, 1, 1])
        r2c1, r2c2, r2c3 = st.columns([1, 1, 1])

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
        with r2c1:
            # TODO: disable this if the current model does not allow for it
            past_covs_widget = st.multiselect(
                "Past Covariates",
                options=st.session_state["widget_options"]["past_covs_widget"],
            )
        with r2c2:
            target_widget = st.selectbox(
                "Target", options=st.session_state["widget_options"]["target_widget"]
            )
        with r2c3:
            model_widget = st.selectbox("Model", options=list(model_opts))

        st.markdown("""---""")
        if st.button("Get forecast"):
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
