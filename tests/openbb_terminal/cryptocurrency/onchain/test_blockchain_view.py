import pytest

from openbb_terminal.cryptocurrency.onchain import blockchain_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_circulating_supply():
    blockchain_view.display_btc_circulating_supply("2010-01-01", "2022-11-10", "")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_confirmed_transactions():
    blockchain_view.display_btc_confirmed_transactions("2010-01-01", "2022-11-10", "")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_single_block():
    blockchain_view.display_btc_single_block(
        # pragma: allowlist nextline secret
        "000000000000000000046af49194517cc5d1cd020692857c1dd09450a7147c6d",
        "",
    )
