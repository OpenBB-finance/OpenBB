# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.hackernews_view import display_stories


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_stories(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.alternative.hackernews_view.export_data")

    display_stories(
        limit=5,
    )
