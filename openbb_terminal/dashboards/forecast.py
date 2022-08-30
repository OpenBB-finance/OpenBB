import streamlit as st
import pandas as pd
import yfinance as yf
from openbb_terminal.forecast import expo_model
from openbb_terminal.forecast import helpers

data = yf.download("TSLA")
target_column = "Close"

data = helpers.clean_data(data, None, None)
# TODO: refactor this command to allow for printing the actual error message
if helpers.check_data(data, target_column):
    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        _model,
    ) = expo_model.get_expo_data(
        data=data,
        target_column=target_column,
        trend="A",
        seasonal="A",
        seasonal_periods=7,
        dampen="F",
        n_predict=30,
        start_window=0.85,
        forecast_horizon=5,
    )
    st.write(pd.DataFrame(predicted_values))
else:
    st.write("There was an error with the data")
