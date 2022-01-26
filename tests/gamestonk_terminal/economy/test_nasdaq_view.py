# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import nasdaq_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [("api_key", "MOCK_API_KEY")],
    }


@pytest.mark.default_cassette("test_display_big_mac_index")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw, tab",
    [
        (True, True),
        (True, False),
        (False, False),
    ],
)
@pytest.mark.record_stdout
def test_display_big_mac_index(mocker, raw, tab):
    # MOCK GTFF
    mocker.patch.object(target=nasdaq_view.gtff, attribute="USE_TABULATE_DF", new=tab)
    mocker.patch.object(target=nasdaq_view.gtff, attribute="USE_ION", new=True)

    # MOCK ION + SHOW
    mocker.patch(target="gamestonk_terminal.economy.nasdaq_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.economy.nasdaq_view.plt.show")

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.economy.nasdaq_view.export_data")

    country_codes = ["VNM", "ARG", "AUS"]
    nasdaq_view.display_big_mac_index(
        country_codes=country_codes,
        raw=raw,
        export="",
    )
