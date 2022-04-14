import pytest

import openbb_terminal.portfolio.brokers.coinbase.coinbase_view as cbv


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
@pytest.mark.record_stdout
def test_accounts():
    cbv.display_account()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_deposits():
    cbv.display_deposits(50, "id", "deposit", False)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_orders():
    cbv.display_orders(50, "product_id", False)
