# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import csimarket_model


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers():
    result_txt = csimarket_model.get_suppliers(ticker="TSLA")
    print(result_txt)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers_invalid():
    result_txt = csimarket_model.get_suppliers(ticker="INVALID_TICKER")
    print(result_txt)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers():
    result_txt = csimarket_model.get_customers(ticker="TSLA")
    print(result_txt)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers_invalid():
    result_txt = csimarket_model.get_customers(ticker="INVALID_TICKER")
    print(result_txt)
