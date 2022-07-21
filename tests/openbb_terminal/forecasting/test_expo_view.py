from openbb_terminal.forecasting import expo_view


def test_display_tft_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecasting.trans_view.helpers.plot_residuals")
    expo_view.display_expo_forecast(
        tsla_csv,
        "TSLA",
        target_col="close",
        trend="N",
        seasonal="N",
        seasonal_periods=3,
        dampen="F",
        n_predict=1,
        start_window=0.5,
        forecast_horizon=1,
        residuals=True,
    )
    mock.assert_called_once()
