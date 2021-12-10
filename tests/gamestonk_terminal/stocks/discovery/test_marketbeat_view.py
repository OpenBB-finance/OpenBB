# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import marketbeat_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.skip("Broken + unused ?")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_ratings_view():
    marketbeat_view.ratings_view(other_args=[])
