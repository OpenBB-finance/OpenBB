# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from freezegun import freeze_time

# IMPORTATION INTERNAL
from openbb_terminal.common.ultima_newsmonitor_view import display_news


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize("term", ["", "AAPL", "TSLA", "FCX", "asdf&%$"])
@freeze_time("2023-05-30")
def test_display_news(term, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.common.ultima_newsmonitor_view.export_data")

    display_news(term=term)
