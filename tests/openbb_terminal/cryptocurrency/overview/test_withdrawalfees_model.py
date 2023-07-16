import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import withdrawalfees_model


@pytest.mark.record_http
def test_get_overall_withdrawal_fees(record):
    df = withdrawalfees_model.get_overall_withdrawal_fees(limit=5)
    record.add_verify(df)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
def test_get_overall_exchange_withdrawal_fees(record):
    df = withdrawalfees_model.get_overall_exchange_withdrawal_fees()
    record.add_verify(df)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
def test_get_crypto_withdrawal_fees():
    response = withdrawalfees_model.get_crypto_withdrawal_fees(symbol="BTC")

    assert isinstance(response, list)
