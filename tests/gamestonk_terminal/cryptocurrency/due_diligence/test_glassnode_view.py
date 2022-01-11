import pytest

from gamestonk_terminal.cryptocurrency.due_diligence import glassnode_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_rainbow():
    glassnode_view.display_btc_rainbow(since=1_325_376_000, until=1_641_641_877)
