import pytest
import openbb_terminal.portfolio.brokers.coinbase.coinbase_model as cbm


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("CB-ACCESS-SIGN", "MOCK-CB-ACCESS-SIGN"),
            ("CB-ACCESS-TIMESTAMP", "MOCK-CB-ACCESS-TIMESTAMP"),
            ("CB-ACCESS-KEY", "MOCK-CB-ACCESS-KEY"),
            ("CB-ACCESS-PASSPHRASE", "MOCK-CB-ACCESS-PASSPHRASE"),
        ],
    }


@pytest.mark.vcr
def test_accounts(recorder):
    json_out = cbm.get_accounts()
    recorder.capture(json_out)


@pytest.mark.vcr
def test_deposits(recorder):
    json_out = cbm.get_deposits()
    recorder.capture(json_out)


@pytest.mark.vcr
def test_orders(recorder):
    json_out = cbm.get_deposits()
    recorder.capture(json_out)
