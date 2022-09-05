from datetime import timedelta, datetime
from typing import Callable, Any
from inspect import signature
import streamlit as st
import pandas as pd
import yfinance as yf
from openbb_terminal import api
from openbb_terminal.forecast import expo_model
from openbb_terminal.forecast import helpers


model_opts = {
    "expo": api.forecast.models.expo.get_expo_data,
    "theta": api.forecast.models.theta.get_theta_data,
    "linregr": api.forecast.models.linregr.get_linear_regression_data,
    "regr": api.forecast.models.regr.get_regression_data,
    "rnn": api.forecast.models.rnn.get_rnn_data,
    "brnn": api.forecast.models.brnn.get_brnn_data,
    "nbeats": api.forecast.models.nbeats.get_NBEATS_data,
    "tcn": api.forecast.models.tcn.get_tcn_data,
    "trans": api.forecast.models.trans.get_trans_data,
    "tft": api.forecast.models.tft.get_tft_data,
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


class Chart:
    def __init__(self):
        self.last_tickers = ""
        self.last_interval = "1d"
        self.df = pd.DataFrame()
        self.infos = {}
        self.widget_options: dict[str, Any] = {}

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
            if tickers != self.last_tickers or interval != self.last_interval:
                if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                    self.df = yf.download(
                        tickers, period="max", interval=interval, progress=False
                    )
                else:
                    end_date = end + timedelta(days=1)
                    self.df = yf.download(
                        tickers,
                        start=start,
                        end=end_date,
                        interval=interval,
                        progress=False,
                    )
                self.df = format_df(self.df)
                self.last_tickers = tickers
                self.last_interval = interval
            forecast_model = model_opts[model]
            contains_covariates = has_parameter(forecast_model, "past_covariates")

            # Update Inputs
            if list(self.widget_options["target_widget"]) != [
                x for x in self.df.columns if x != "date"
            ]:
                self.widget_options["target_widget"] = [
                    x for x in self.df.columns if x != "date"
                ]
                self.create_widgets()
                return
            if list(self.widget_options["past_covs_widget"]) != [
                x for x in self.df.columns if x != "date"
            ]:
                self.widget_options["past_covs_widget"] = [
                    x for x in self.df.columns if x != "date"
                ]
                # past_covs_widget.disabled = not contains_covariates
                self.create_widgets()
                return
            if self.widget_options["past_covs_widget"] == contains_covariates:
                self.widget_options["past_covs_widget"] = not contains_covariates
            self.widget_options["column_widget"] = [
                x for x in self.df.columns if x != "date"
            ]

            start_n = datetime(start.year, start.month, start.day)
            end_n = datetime(end.year, end.month, end.day)
            calcs = self.df
            if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
                result = calcs.loc[
                    (calcs["date"] >= start_n) & (calcs["date"] <= end_n)
                ]
            else:
                result = calcs
            if not target_column:
                target_column = self.df.columns[0]
            kwargs = {}
            if contains_covariates and past_covariates != ():
                kwargs["past_covariates"] = ",".join(past_covariates)
            if has_parameter(forecast_model, "naive"):
                kwargs["naive"] = naive
            if has_parameter(forecast_model, "forecast_only"):
                kwargs["forecast_only"] = forecast_only
            # df = handler.result.dropna()
            if helpers.check_data(result, target_column):
                (
                    ticker_series,
                    historical_fcast,
                    predicted_values,
                    precision,
                    _model,
                ) = expo_model.get_expo_data(
                    data=result,
                    target_column=target_column,
                    trend="A",
                    seasonal="A",
                    seasonal_periods=7,
                    dampen="F",
                    n_predict=30,
                    start_window=0.85,
                    forecast_horizon=5,
                    **kwargs,
                )
                predicted_values = predicted_values.quantile_df()[
                    f"{target_column}_0.5"
                ].tail(5)
            if predicted_values is not None:
                st.write(predicted_values)
                # draw predicted_values on line graph
                st.line_chart(predicted_values)

            else:
                st.write("There was an error with the data")

    def handle_eng(self, target, feature):
        self.feature_target = target
        self.feature_model = feat_engs[feature]

    def create_widgets(self):
        st.title("Forecast")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            self.ticker = st.text_input("Ticker", "AAPL")
        with col2:
            self.start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
        with col3:
            self.end_date = st.date_input("End date", pd.to_datetime("2020-12-01"))
        self.past_covs_widget = st.multiselect("Past Covariates", options=[])
        self.target_widget = st.selectbox("Target", [])

    def run(self):
        self.create_widgets()
        if st.button("Get forecast"):
            interval = "1d"
            tickers = "AAPL"
            target_column = "Close"
            handler.handle_changes(
                [],
                self.start_date,
                self.end_date,
                interval,
                tickers=tickers,
                target_column=target_column,
                model="expo",
                naive=False,
                forecast_only=False,
            )

            # TODO need to new add in business days and merge to make new DF before plotting
            # create df with 5 next business days from a start date
            # next_business_days = pd.date_range(start=end_date, periods=5, freq="B")

        if st.button("Add Column"):
            kwargs = {}
            if has_parameter(handler.feature_model, "target_column"):
                kwargs["target_column"] = handler.feature_target
            handler.df = handler.feature_model(handler.df, **kwargs)
            self.widget_options["past_covs_widget"]= handler.df.columns


if __name__ == "__main__":
    handler = Chart()
    # select time range
    handler.run()
