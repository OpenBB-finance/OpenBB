import streamlit as st
import pandas as pd
import yfinance as yf
from openbb_terminal.forecast import expo_model
from openbb_terminal.forecast import helpers

target_column = "Close"

# Seperate out the forecast function for testing cache...?
@st.cache
def run_forecast(data):
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
        predicted_values = predicted_values.quantile_df()[f"{target_column}_0.5"].tail(
            5
        )
        return pd.DataFrame(predicted_values)
    else:
        return None


def run():
    st.title("Forecast")
    st.write(
        "This is a simple forecast dashboard. You can select a ticker and a time range and get a forecast for the next 5 days."
    )
    ticker = st.text_input("Ticker", "AAPL")
    # select time range
    start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("End date", pd.to_datetime("2020-12-01"))
    if st.button("Get forecast"):
        data = yf.download(ticker, start_date, end_date)
        data = data.reset_index()
        data = data[["Date", "Close"]]
        data = helpers.clean_data(data, None, None)
        predicted_values = run_forecast(data)

        # TODO need to new add in business days and merge to make new DF before plotting
        # create df with 5 next business days from a start date
        # next_business_days = pd.date_range(start=end_date, periods=5, freq="B")

        if predicted_values is not None:
            st.write(predicted_values)
            # draw predicted_values on line graph
            st.line_chart(predicted_values)

        else:
            st.write("There was an error with the data")


if __name__ == "__main__":

    run()
