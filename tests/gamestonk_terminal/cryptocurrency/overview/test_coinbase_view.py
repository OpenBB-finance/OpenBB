from unittest import mock, TestCase
import vcr
from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinbase_view as dd_coinbase_view,
)
from gamestonk_terminal.portfolio.brokers.coinbase import (
    coinbase_view as bro_coinbase_view,
)
from gamestonk_terminal.cryptocurrency.overview import coinbase_view as ov_coinbase_view
from tests.helpers import check_print


# pylint: disable=unused-import


class TestCoinbaseView(TestCase):  # pragma: allowlist secret
    @check_print(assert_in="Open")
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.check_validity_of_product"
    )
    def test_display_candles(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = [
            [1631318400, 0.0715, 0.07314, 0.07155, 0.07245, 5957.08396321],
            [1631232000, 0.07088, 0.07476, 0.07382, 0.07159, 13264.33844153],
            [1631145600, 0.07369, 0.07669, 0.07599, 0.07378, 12462.35265359],
        ]
        dd_coinbase_view.display_candles("ETH-BTC", "1day", "")

    @check_print(assert_in="Value")
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.check_validity_of_product"
    )
    def test_display_stats(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = {
            "open": "3245.61000000",
            "high": "3392.11000000",
            "low": "3150.00000000",
            "volume": "26185.51325269",
            "last": "3333.19000000",
            "volume_30day": "1019451.11188405",
        }
        dd_coinbase_view.display_stats("ETH-USDT", "")

    @check_print(assert_in="price")
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinbase_model.check_validity_of_product"
    )
    def test_display_trades(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = [
            {
                "time": "2014-11-07T22:19:28.578544Z",
                "trade_id": 74,
                "price": "10.00000000",
                "size": "0.01000000",
                "side": "buy",
            },
            {
                "time": "2014-11-07T01:08:43.642366Z",
                "trade_id": 73,
                "price": "100.00000000",
                "size": "0.01000000",
                "side": "sell",
            },
        ]
        dd_coinbase_view.display_trades("ETH-USDT", limit=100, side=None, export="")

    @check_print(assert_in="product_id")
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model._check_account_validity"
    )
    def test_display_orders(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = [
            {
                "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
                "price": "0.10000000",
                "size": "0.01000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": False,
                "created_at": "2016-12-08T20:02:28.53864Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "open",
                "settled": False,
            },
            {
                "id": "b227e691-365c-470f-a860-a9b4a37dd1d8",
                "price": "1.00000000",
                "size": "1.00000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "type": "limit",
                "created_at": "2016-12-08T20:01:19.038644Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "pending",
                "settled": False,
            },
            {
                "id": "b24327e691-365c-470f-a860-a9b4a37dd1d8",
                "price": "2.00000000",
                "size": "1.00000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "type": "limit",
                "created_at": "2016-12-08T20:01:19.038644Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "pending",
                "settled": False,
            },
        ]
        bro_coinbase_view.display_orders(2, "created_at", descend=True, export="")

    @check_print(assert_in="crypto_address")
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model._check_account_validity"
    )
    def test_display_deposits(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = (
            [
                {
                    "id": "6cca6a14-a5e3-4219-9542-86123fc9d6c3",
                    "type": "deposit",
                    "created_at": "2019-06-18 01:37:48.78953+00",
                    "completed_at": "2019-06-18 01:37:49.756147+00",
                    "canceled_at": None,
                    "processed_at": "2019-06-18 01:37:49.756147+00",
                    "account_id": "bf091906-ca7f-499e-95fa-5bc15e918b46",
                    "user_id": "5eeac63c90b913bf3cf7c92e",
                    "user_nonce": None,
                    "amount": "40.00000000",
                    "details": {
                        "crypto_address": "testaddress",
                        "destination_tag": "379156162",
                        "coinbase_account_id": "7f8803e2-1be5-4a29-bfd2-3bc6645f5a24",
                        "destination_tag_name": "XRP Tag",
                        "crypto_transaction_id": "5eeac64cc46b34f5332e5326",
                        "coinbase_transaction_id": "5eeac652be6cf8b17f7625bd",
                        "crypto_transaction_hash": "testhash",
                    },
                },
                {
                    "id": "543cca6a14-a5e3-4219-9542-86123fc9d6c3",
                    "type": "deposit",
                    "created_at": "2019-06-18 01:37:48.78953+00",
                    "completed_at": "2019-06-18 01:37:49.756147+00",
                    "canceled_at": None,
                    "processed_at": "2019-06-18 01:37:49.756147+00",
                    "account_id": "bf091906-ca7f-499e-95fa-5bc15e918b46",
                    "user_id": "5eeac63c90b913bf3cf7c92e",
                    "user_nonce": None,
                    "amount": "50.00000000",
                    "details": {
                        "crypto_address": "12g",
                        "destination_tag": "379156162",
                        "coinbase_account_id": "7f8803e2-1be5-4a29-bfd2-3bc6645f5a24",
                        "destination_tag_name": "XRP Tag",
                        "crypto_transaction_id": "5eeac64cc46b34f5332e5326",
                        "coinbase_transaction_id": "5eeac652be6cf8b17f7625bd",
                        "crypto_transaction_hash": "324",
                    },
                },
            ],
        )
        bro_coinbase_view.display_deposits(
            2, "created_at", "deposit", descend=True, export=""
        )

    @check_print(assert_in="balance")
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model.make_coinbase_request"
    )
    @mock.patch(
        "gamestonk_terminal.portfolio.brokers.coinbase.coinbase_model._check_account_validity"
    )
    def test_display_history(self, mock_validity, mock_request):
        mock_validity.return_value = "ETH"
        mock_request.return_value = [
            {
                "id": "100",
                "created_at": "2014-11-07T08:19:27.028459Z",
                "amount": "0.001",
                "balance": "239.669",
                "type": "fee",
                "details": {
                    "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                    "trade_id": "74",
                    "product_id": "ETH-USD",
                },
            },
            {
                "id": "111",
                "created_at": "2014-11-07T08:19:27.028459Z",
                "amount": "0.001",
                "balance": "239.669",
                "type": "fee",
                "details": {
                    "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                    "trade_id": "75",
                    "product_id": "ETH-USD",
                },
            },
        ]
        bro_coinbase_view.display_history("ETH", "", 2)

    @check_print(assert_in="base_currency")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/cassettes/test_coinbase_view/test_trading_pairs.yaml",
        record_mode="new_episodes",
    )
    def test_display_trading_pairs(self):
        ov_coinbase_view.display_trading_pairs(10, "base_currency", False, "")
