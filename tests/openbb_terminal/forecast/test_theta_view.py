import pytest

try:
    from openbb_terminal.forecast import theta_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_theta_forecast(tsla_csv):
    theta_view.display_theta_forecast(
        data=tsla_csv,
        seasonal="N",
        seasonal_periods=3,
        n_predict=5,
        target_column="close",
        start_window=0.3,
        forecast_horizon=1,
    )
