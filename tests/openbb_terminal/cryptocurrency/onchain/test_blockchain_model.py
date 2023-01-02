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


@pytest.mark.vcr
def test_get_btc_single_block(recorder):
    df = blockchain_model.get_btc_single_block(
        # pragma: allowlist nextline secret
        "000000000000000000046af49194517cc5d1cd020692857c1dd09450a7147c6d"
    )
    recorder.capture(df)
