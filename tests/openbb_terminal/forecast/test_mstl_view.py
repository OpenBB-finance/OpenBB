import pytest

try:
    from openbb_terminal.forecast import mstl_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_mstl_forecast(tsla_csv):
    mstl_view.display_mstl_forecast(
        tsla_csv,
        target_column="close",
        seasonal_periods=3,
        n_predict=1,
        start_window=0.5,
        forecast_horizon=1,
    )
