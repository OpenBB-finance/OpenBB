import pytest

try:
    from openbb_terminal.forecast import regr_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_regr_forecast(tsla_csv, mocker):
    mock = mocker.patch("openbb_terminal.forecast.trans_view.helpers.plot_residuals")
    regr_view.display_regression(tsla_csv, residuals=True)
    mock.assert_called_once()
