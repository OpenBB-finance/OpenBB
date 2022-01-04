# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import geekofwallstreet_model


@pytest.mark.vcr
def test_get_realtime_earnings(recorder):
    data_df = geekofwallstreet_model.get_realtime_earnings()
    recorder.capture(data_df)
