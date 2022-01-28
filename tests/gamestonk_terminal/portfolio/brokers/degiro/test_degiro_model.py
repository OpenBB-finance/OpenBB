# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
from degiro_connector.trading.models import trading_pb2

# IMPORTATION INTERNAL
from gamestonk_terminal.portfolio.brokers.degiro.degiro_model import DegiroModel

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


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
        "filter_post_data_parameters": [
            ("username", "MOCK_USERNAME"),
            ("password", "MOCK_PASSWORD"),
            ("oneTimePassword", "MOCK_ONE_TIME_PASSWORD"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, kwargs, mocked_func, mock_return",
    [
        (
            "cancel",
            dict(order_id="MOCK_ORDER_ID"),
            "delete_order",
            True,
        ),
        (
            "companynews",
            dict(isin="MOCK_ISIN"),
            "get_news_by_company",
            trading_pb2.NewsByCompany(),
        ),
        (
            "create_check",
            dict(order=trading_pb2.Order()),
            "check_order",
            trading_pb2.Order.CheckingResponse(),
        ),
        (
            "create_confirm",
            dict(confirmation_id="MOCK_CONFIRMATION_ID", order=trading_pb2.Order()),
            "confirm_order",
            trading_pb2.Order.ConfirmationResponse(),
        ),
        (
            "lastnews",
            dict(limit=1),
            "get_latest_news",
            trading_pb2.LatestNews(),
        ),
        (
            "logout",
            dict(),
            "logout",
            True,
        ),
        (
            "lookup",
            dict(limit=1, offset=2, search_text="MOCK_SEARCH_TXT"),
            "product_search",
            trading_pb2.ProductSearch(),
        ),
        (
            "topnews",
            dict(),
            "get_top_news_preview",
            trading_pb2.TopNewsPreview(),
        ),
        (
            "update",
            dict(order=trading_pb2.Order()),
            "update_order",
            trading_pb2.Update.Orders(),
        ),
    ],
)
def test_call_func(func, kwargs, mocked_func, mock_return, mocker):
    model = DegiroModel()

    # MOCK MOCKED_FUNC
    mock_func = mocker.Mock(return_value=mock_return)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute=mocked_func,
        new=mock_func,
    )

    result = getattr(model, func)(**kwargs)

    mock_func.assert_called_once()
    assert isinstance(result, type(mock_return))


@pytest.mark.vcr(record_mode="none")
def test_pending(mocker):
    model = DegiroModel()

    # MOCK API FUNCTION
    mock_func = mocker.Mock(return_value=trading_pb2.Update())
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_update",
        new=mock_func,
    )

    result = model.pending()

    mock_func.assert_called_once()
    assert isinstance(result, trading_pb2.Update.Orders)


@pytest.mark.vcr(record_mode="none")
def test_update_pending_order(mocker):
    model = DegiroModel()

    # MOCK API FUNCTION
    mock_update = trading_pb2.Update()
    mock_update.orders.values.extend(
        [
            trading_pb2.Order(
                id="MOCK_ORDER_ID",
                product_id=1,
                size=2,
                price=3,
            ),
        ]
    )
    mock_func = mocker.Mock(return_value=mock_update)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_update",
        new=mock_func,
    )

    result = model.update_pending_order(order_id="MOCK_ORDER_ID")

    mock_func.assert_called_once()
    assert isinstance(result, trading_pb2.Order)


@pytest.mark.vcr(record_mode="none")
def test_update_pending_order_no_order_id(mocker):
    model = DegiroModel()

    # MOCK API FUNCTION
    mock_update = trading_pb2.Update()
    mock_update.orders.values.extend(
        [
            trading_pb2.Order(
                product_id=1,
                size=2,
                price=3,
            ),
        ]
    )
    mock_func = mocker.Mock(return_value=mock_update)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_update",
        new=mock_func,
    )

    result = model.update_pending_order(order_id="MOCK_ORDER_ID")

    mock_func.assert_called_once()
    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_update_pending_order_none(mocker):
    model = DegiroModel()

    # MOCK API FUNCTION
    mock_update = trading_pb2.Update()
    mock_func = mocker.Mock(return_value=mock_update)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_update",
        new=mock_func,
    )

    result = model.update_pending_order(order_id="MOCK_ORDER_ID")

    mock_func.assert_called_once()
    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_hold_positions_empty_update(mocker):
    model = DegiroModel()

    # MOCK API FUNCTION
    mock_update = trading_pb2.Update()
    mock_func = mocker.Mock(return_value=mock_update)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_update",
        new=mock_func,
    )

    result = model.hold_positions()

    assert isinstance(result, pd.DataFrame)


@pytest.mark.vcr(record_mode="none")
def test_login_default_credentials():
    model = DegiroModel()

    credentials = model.login_default_credentials()

    assert isinstance(credentials, trading_pb2.Credentials)


@pytest.mark.vcr(record_mode="none")
def test_login(mocker):
    model = DegiroModel()

    # MOCK CONNECT
    mock_connect = mocker.Mock()
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="connect",
        new=mock_connect,
    )

    # MOCK GET_CLIENT_DETAILS
    mock_client_details_table = {
        "data": {
            "intAccount": 12345,
        }
    }
    mock_get_client_details = mocker.Mock(return_value=mock_client_details_table)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="get_client_details",
        new=mock_get_client_details,
    )

    model.login(credentials=trading_pb2.Credentials())

    mock_connect.assert_called_once()
    mock_get_client_details.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "kwargs, expected",
    [
        (
            dict(price=10, size=None, up_to=22),
            2,
        ),
        (
            dict(price=10, size=2, up_to=None),
            2,
        ),
    ],
)
def test_create_calculate_size(expected, kwargs):
    model = DegiroModel()

    result = model.create_calculate_size(**kwargs)

    assert result == expected


@pytest.mark.vcr(record_mode="none")
def test_create_calculate_product_id_product_id():
    model = DegiroModel()

    result = model.create_calculate_product_id(product=1, symbol=None)

    assert result == 1


@pytest.mark.vcr(record_mode="none")
def test_create_calculate_product_id_product_symbol(mocker):
    model = DegiroModel()

    result = model.create_calculate_product_id(product=1, symbol=None)

    assert result == 1

    # MOCK CONNECT
    product_search = trading_pb2.ProductSearch()
    product = product_search.products.add()
    product["id"] = 1
    product["symbol"] = "MOCK_SYMBOL"
    mock_product_search = mocker.Mock(return_value=product_search)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="product_search",
        new=mock_product_search,
    )

    result = model.create_calculate_product_id(product=None, symbol="MOCK_SYMBOL")

    assert result == 1


@pytest.mark.vcr(record_mode="none")
def test_create_calculate_product_id_product_symbol_no_result(mocker):
    model = DegiroModel()

    result = model.create_calculate_product_id(product=1, symbol=None)

    assert result == 1

    # MOCK CONNECT
    product_search = trading_pb2.ProductSearch()
    product = product_search.products.add()
    product["id"] = 1
    product["symbol"] = "MOCK_WRONG_SYMBOL"
    mock_product_search = mocker.Mock(return_value=product_search)
    mocker.patch.object(
        target=model.__dict__["_DegiroModel__trading_api"],
        attribute="product_search",
        new=mock_product_search,
    )

    result = model.create_calculate_product_id(product=None, symbol="MOCK_SYMBOL")

    assert result is None
