# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.feedparser_view import display_news


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize("term", ["", "Apple", "Coal", "asdf&%$"])
def test_display_news(term, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.common.feedparser_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    display_news(term=term)
