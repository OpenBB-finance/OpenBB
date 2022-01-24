# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import stockanalysis_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
def test_get_all_names_symbols(recorder):
    result = stockanalysis_model.get_all_names_symbols()

    recorder.capture_list(result)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "symbol",
    [
        "ARKQ",
        "ARKW",
    ],
)
def test_get_etf_overview(recorder, symbol):
    result_df = stockanalysis_model.get_etf_overview(symbol)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "symbol",
    [
        "ARKQ",
        "ARKW",
    ],
)
def test_get_etf_holdings(recorder, symbol):
    result_df = stockanalysis_model.get_etf_holdings(symbol)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "symbols",
    [
        ["ARKQ", "ARKW"],
        ["ARKK", "ARKF"],
    ],
)
def test_compare_etfs(recorder, symbols):
    result_df = stockanalysis_model.compare_etfs(symbols)

    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "name_to_search",
    [
        "oil",
    ],
)
def test_get_etfs_by_name(recorder, name_to_search):
    result_df = stockanalysis_model.get_etfs_by_name(name_to_search)

    assert not result_df.empty
    recorder.capture(result_df)
