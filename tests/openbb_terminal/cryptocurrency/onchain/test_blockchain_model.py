import pytest

from openbb_terminal.cryptocurrency.onchain import blockchain_model


@pytest.mark.vcr
def test_get_btc_confirmed_transactions(recorder):
    df = blockchain_model.get_btc_confirmed_transactions()
    recorder.capture(df)


@pytest.mark.vcr
def test_get_btc_circulating_supply(recorder):
    df = blockchain_model.get_btc_circulating_supply()
    recorder.capture(df)
