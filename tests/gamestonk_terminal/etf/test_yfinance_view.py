# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import yfinance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["ARKW", "ARKF"],
)
def test_display_etf_weightings(name, mocker):
    mocker.patch.object(
        target=yfinance_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    yfinance_view.display_etf_weightings(
        name, raw=True, min_pct_to_display=5, export=""
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["ARKW", "ARKF"],
)
def test_display_etf_description(name, mocker):
    mocker.patch.object(
        target=yfinance_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    yfinance_view.display_etf_description(name)
