# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import financedatabase_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "name",
    [
        "oil",
        "bank",
    ],
)
def test_get_etfs_by_name(recorder, name):
    result = financedatabase_model.get_etfs_by_name(name)

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "description",
    [
        "oil",
        "bank",
    ],
)
def test_get_etfs_by_description(recorder, description):
    result = financedatabase_model.get_etfs_by_description(description)

    recorder.capture(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "category",
    [
        "Bank Loan",
        "Bear Market",
    ],
)
def test_get_etfs_by_category(recorder, category):
    result = financedatabase_model.get_etfs_by_category(category)

    recorder.capture(result)


@pytest.mark.vcr()
def test_get_all_names_symbols(recorder):
    result = financedatabase_model.get_etfs_categories()

    recorder.capture_list(result)
