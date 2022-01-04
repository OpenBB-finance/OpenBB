# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import fidelity_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
def test_get_orders(recorder):
    order_header, df_orders = fidelity_model.get_orders()
    recorder.capture(order_header)
    recorder.capture(df_orders)
