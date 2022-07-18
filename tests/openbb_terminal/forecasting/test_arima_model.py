from openbb_terminal.forecasting import arima_model


def test_get_arima_model(tsla_csv):
    arima_model.get_arima_model(
        tsla_csv["close"],
        arima_order=None,
        ic="aic",
        seasonal=False,
        n_predict=5,
    )
