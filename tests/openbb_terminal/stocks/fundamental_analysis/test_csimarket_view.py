# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import csimarket_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers():
    csimarket_view.suppliers(symbol="TSLA", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_suppliers_invalid():
    csimarket_view.suppliers(symbol="INVALID_TICKER", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers():
    csimarket_view.customers(symbol="TSLA", export=None)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_customers_invalid():
    csimarket_view.customers(symbol="INVALID_TICKER", export=None)
