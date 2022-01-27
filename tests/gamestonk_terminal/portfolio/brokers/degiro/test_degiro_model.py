# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.portfolio.brokers.degiro.degiro_model import DegiroModel
from degiro_connector.trading.models import trading_pb2


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("cookie", None),
        ],
        "filter_query_parameters": [
            ("intAccount", "MOCK_INT_ACCOUNT"),
            ("sessionId", "MOCK_SESSION_ID"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
def test_cancel(mocker):
    model = DegiroModel()

    # MOCK DELETE_ORDER
    mock_delete_order = mocker.Mock()
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="delete_order",
        new=mock_delete_order,
    )

    mock_order_id = "MOCK_ORDER_ID"

    model.cancel(order_id=mock_order_id)

    mock_delete_order.assert_called_once_with(order_id=mock_order_id)


@pytest.mark.vcr
def test_companynews():
    model = DegiroModel()
    credentials = model.login_default_credentials()
    model.login(credentials=credentials)
    result = model.companynews(isin="US88160R1014")

    assert isinstance(result, trading_pb2.NewsByCompany)
