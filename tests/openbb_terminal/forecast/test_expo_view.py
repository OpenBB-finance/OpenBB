import pytest

try:
    from openbb_terminal.forecast import expo_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_expo_forecast(tsla_csv):
    expo_view.display_expo_forecast(
        tsla_csv,
        target_column="close",
        trend="N",
        seasonal="N",
        seasonal_periods=3,
        dampen="F",
        n_predict=1,
        start_window=0.5,
        forecast_horizon=1,
    )
