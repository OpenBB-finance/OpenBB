import pytest

try:
    from openbb_terminal.forecast import nbeats_view
except ImportError:
    pytest.skip(allow_module_level=True)


def test_display_nbeats_forecast(tsla_csv):
    nbeats_view.display_nbeats_forecast(tsla_csv, "TSLA", n_epochs=1)
