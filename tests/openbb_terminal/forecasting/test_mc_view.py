from openbb_terminal.forecasting import mc_view


def test_display_mc_forecast(tsla_csv):
    tsla_csv = tsla_csv.set_index("date")
    mc_view.display_mc_forecast(tsla_csv["close"], 1, 2)
