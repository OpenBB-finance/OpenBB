# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import csimarket_model


@pytest.mark.vcr
def test_get_suppliers(recorder):
    result = csimarket_model.get_suppliers(symbol="TSLA")
    recorder.capture(result)


@pytest.mark.vcr
def test_get_suppliers_invalid(recorder):
    result = csimarket_model.get_suppliers(symbol="INVALID_TICKER")
    recorder.capture(result)


@pytest.mark.vcr
def test_get_customers(recorder):
    result = csimarket_model.get_customers(symbol="TSLA")
    recorder.capture(result)


@pytest.mark.vcr
def test_get_customers_invalid(recorder):
    result = csimarket_model.get_customers(symbol="INVALID_TICKER")
    recorder.capture(result)
