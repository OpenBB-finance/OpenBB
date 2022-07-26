from openbb_terminal.forecast import tcn_view


def test_display_tcn_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    tcn_view.display_tcn_forecast(tsla_csv, "TSLA", n_epochs=1, residuals=True)
    mock.assert_called_once()
