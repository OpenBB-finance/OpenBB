import pytest

from openbb_terminal.cryptocurrency.due_diligence import glassnode_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.skip(reason="`subplots` not mocked => calling displays the plot")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_rainbow(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    glassnode_view.display_btc_rainbow(since=1_325_376_000, until=1_641_641_877)
