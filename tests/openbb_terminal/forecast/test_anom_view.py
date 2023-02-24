import pytest

try:
    from openbb_terminal.forecast import anom_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_anom_forecast(tsla_csv):
    anom_view.display_anomaly_detection(
        tsla_csv,
        target_column="close",
        train_split=0.5,
    )
