import pytest

try:
    from openbb_terminal.forecast import brnn_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_brnn_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    brnn_view.display_brnn_forecast(data=tsla_csv, n_epochs=1, residuals=True)
    mock.assert_called_once()
