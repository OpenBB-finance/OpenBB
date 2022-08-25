import pytest

try:
    from openbb_terminal.forecast import trans_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_trans_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    trans_view.display_trans_forecast(
        tsla_csv, residuals=True, past_covariates="open", n_epochs=1
    )
    mock.assert_called_once()
