import pytest
from openbb_terminal.forecast import nbeats_view


@pytest.mark.prediction
def test_display_nbeats_forecast(tsla_csv):
    nbeats_view.display_nbeats_forecast(tsla_csv, "TSLA", n_epochs=1)
