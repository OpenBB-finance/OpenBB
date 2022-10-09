import pytest

try:
    from openbb_terminal.forecast import linregr_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_linregr_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    linregr_view.display_linear_regression(tsla_csv, residuals=True)
    mock.assert_called_once()
