import pytest

try:
    from openbb_terminal.forecast import qanom_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_qanom_forecast(tsla_csv):
    qanom_view.display_qanomaly_detection(
        tsla_csv,
        target_column="close",
        start_window=0.5,
    )
