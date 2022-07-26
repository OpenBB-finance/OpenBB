from openbb_terminal.forecast.mc_model import get_mc_brownian


def test_get_mc_brownian(tsla_csv):
    # This uses non standard test because its from the old system
    get_mc_brownian(tsla_csv["close"], 5, 5)
