# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import financedatabase_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["oil", "banks"],
)
def test_display_etf_by_name(name, mocker):
    mocker.patch.object(
        target=financedatabase_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    financedatabase_view.display_etf_by_name(name, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "description",
    ["oil", "banks"],
)
def test_display_etf_by_description(description, mocker):
    mocker.patch.object(
        target=financedatabase_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    financedatabase_view.display_etf_by_description(description, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "category",
    [
        "Bank Loan",
        "Bear Market",
    ],
)
def test_display_etf_by_category(category, mocker):
    mocker.patch.object(
        target=financedatabase_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    financedatabase_view.display_etf_by_category(category, limit=5, export="")
