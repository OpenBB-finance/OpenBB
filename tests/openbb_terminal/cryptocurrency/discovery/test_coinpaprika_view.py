# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.discovery import coinpaprika_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_search_results(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.discovery.coinpaprika_view.export_data"
    )

    coinpaprika_view.display_search_results(
        query="ethereum",
        category="all",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_search_results_empty_df(mocker):
    view_path = "openbb_terminal.cryptocurrency.discovery.coinpaprika_view"

    # MOCK GET_SEARCH_RESULTS
    mocker.patch(
        target=f"{view_path}.paprika.get_search_results",
        return_value=pd.DataFrame(),
    )

    coinpaprika_view.display_search_results(
        query="ethereum",
        category="all",
    )
