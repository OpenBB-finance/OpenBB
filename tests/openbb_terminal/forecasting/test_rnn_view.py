from openbb_terminal.forecasting import rnn_view


def test_display_rnn_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecasting.trans_view.helpers.plot_residuals")
    rnn_view.display_rnn_forecast(tsla_csv, "TSLA", n_epochs=1, residuals=True)
    mock.assert_called_once()
