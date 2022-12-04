import pytest

try:
    from openbb_terminal.forecast import autoets_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_tft_forecast(tsla_csv):
    autoets_view.display_autoets_forecast(
        tsla_csv,
        target_column="close",
        seasonal_periods=3,
        n_predict=1,
        start_window=0.5,
        forecast_horizon=1,
    )
