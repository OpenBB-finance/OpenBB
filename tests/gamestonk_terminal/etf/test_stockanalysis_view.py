# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import stockanalysis_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "symbol,use_tab",
    [
        ("ARKQ", True),
        ("ARKW", True),
        ("ARKQ", False),
        ("ARKW", False),
    ],
)
def test_view_overview(symbol, use_tab, mocker):
    mocker.patch.object(
        target=stockanalysis_view.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )
    stockanalysis_view.view_overview(symbol)
