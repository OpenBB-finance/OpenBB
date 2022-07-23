from openbb_terminal.forecasting import nbeats_view


def test_display_nbeats_forecast(tsla_csv):
    nbeats_view.display_nbeats_forecast(tsla_csv, "TSLA", n_epochs=1)
