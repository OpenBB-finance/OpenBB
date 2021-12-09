# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import csimarket_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers():
    csimarket_view.suppliers(ticker="TSLA", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers_invalid():
    csimarket_view.suppliers(ticker="INVALID_TICKER", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers():
    csimarket_view.customers(ticker="TSLA", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers_invalid():
    csimarket_view.customers(ticker="INVALID_TICKER", export=None)
