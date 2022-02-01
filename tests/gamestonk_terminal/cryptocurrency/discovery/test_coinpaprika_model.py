# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import coinpaprika_model


@pytest.mark.vcr
def test_get_search_results(recorder):
    result = coinpaprika_model.get_search_results(
        query="ethereum",
    )
    recorder.capture(result)
