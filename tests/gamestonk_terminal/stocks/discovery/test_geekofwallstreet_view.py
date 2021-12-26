# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import geekofwallstreet_view


@pytest.mark.default_cassette("test_get_realtime_earnings")
@pytest.mark.vcr
@pytest.mark.parametrize("use_tab", [True, False])
def test_get_realtime_earnings(mocker, use_tab):
    mocker.patch.object(
        target=geekofwallstreet_view.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )
    geekofwallstreet_view.display_realtime_earnings(export="")
