import pytest

try:
    from openbb_terminal.forecast import rnn_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_rnn_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    rnn_view.display_rnn_forecast(tsla_csv, n_epochs=1, residuals=True)
    mock.assert_called_once()
