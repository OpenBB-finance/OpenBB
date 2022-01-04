# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import nasdaq_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_key", "MOCK_API"),
        ]
    }


@pytest.mark.default_cassette("test_display_top_retail")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize("use_tab", [True, False])
def test_display_top_retail(mocker, use_tab):
    mocker.patch.object(
        target=nasdaq_view.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )

    nasdaq_view.display_top_retail(n_days=3, export="")
