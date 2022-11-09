import pytest

from openbb_terminal.cryptocurrency.overview import glassnode_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
def test_display_btc_rainbow(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    glassnode_view.display_btc_rainbow(start_date="2012-01-01", end_date="2022-01-08")
