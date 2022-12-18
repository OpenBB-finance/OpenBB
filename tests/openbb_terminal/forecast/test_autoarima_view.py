import pytest

try:
    from openbb_terminal.forecast import autoarima_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_autoarima_forecast(tsla_csv):
    autoarima_view.display_autoarima_forecast(
        tsla_csv,
        target_column="close",
        seasonal_periods=3,
        n_predict=1,
        start_window=0.5,
    )
