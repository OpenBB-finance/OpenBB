from openbb_terminal.forecasting import trans_view


def test_display_trans_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecasting.trans_view.helpers.plot_residuals")
    trans_view.display_trans_forecast(
        tsla_csv, "TSLA", residuals=True, past_covariates="open", n_epochs=1
    )
    mock.assert_called_once()
