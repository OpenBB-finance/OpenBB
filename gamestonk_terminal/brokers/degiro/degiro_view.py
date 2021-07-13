# IMPORTATION THIRDPARTY
from argparse import Namespace
import pandas as pd
import degiro_connector.trading.helpers.payload_handler as payload_handler

from degiro_connector.trading.pb.trading_pb2 import (
    Credentials,
    LatestNews,
    NewsByCompany,
    Order,
    ProductSearch,
    TopNewsPreview,
    Update,
)

# IMPORTATION INTERNAL
from gamestonk_terminal.brokers.degiro.degiro_model import DegiroModel

# pylint: disable=no-member


class DegiroView:
    ORDER_ACTION = {
        "buy": Order.Action.BUY,
        "sell": Order.Action.SELL,
    }

    ORDER_DURATION = {
        "gtd": Order.TimeType.GOOD_TILL_DAY,
        "gtc": Order.TimeType.GOOD_TILL_CANCELED,
    }

    ORDER_TYPE = {
        "limit": Order.OrderType.LIMIT,
        "market": Order.OrderType.MARKET,
        "stop-limit": Order.OrderType.STOP_LIMIT,
        "stop-loss": Order.OrderType.STOP_LOSS,
    }

    def __init__(self):
        self.__degiro_model = DegiroModel()

    @staticmethod
    def help_display():
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/brokers/degiro"
        )
        print(
            "\nDegiro:\n"
            "   help         show this help menu again\n"
            "   q            quit degiro standalone menu\n"
            "   quit         quit the app\n"
            "\n"
            "   login        connect to degiro's api\n"
            "   logout       disconnect from degiro's api\n"
            "\n"
            "   hold         view holdings\n"
            "   lookup       view search for a product by name\n"
            "\n"
            "   create       create an order\n"
            "   update       update an order\n"
            "   cancel       cancel an order using the id\n"
            "   pending      view pending orders\n"
            "\n"
            "   companynews  view news about a company with it's isin\n"
            "   lastnews     view latest news\n"
            "   topnews      view top news preview\n"
        )

    def cancel(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # CANCEL ORDER
        order_id = ns_parser.id

        # DISPLAY DATA
        if degiro_model.cancel(order_id=order_id):
            DegiroView.__cancel_display_success(order_id=order_id)
        else:
            DegiroView.__cancel_display_fail(order_id=order_id)

    @staticmethod
    def __cancel_display_success(order_id: str):
        print(f"Following `Order` was canceled : {order_id}")

    @staticmethod
    def __cancel_display_fail(order_id: str):
        print(f"Following `Order` cancellation failed : {order_id}")

    def companynews(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        news_by_company = degiro_model.companynews(isin=ns_parser.isin)

        # DISPLAY DATA
        DegiroView.__companynews_display(news_by_company=news_by_company)

    @staticmethod
    def __companynews_display(news_by_company: NewsByCompany):
        news_dict = payload_handler.message_to_dict(
            message=news_by_company,
        )
        for article in news_dict["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("isins", article["isins"])
            print("---")

    def create(self, ns_parser: Namespace):
        # GET CONSTANTS
        ORDER_ACTION = self.ORDER_ACTION
        ORDER_DURATION = self.ORDER_DURATION
        ORDER_TYPE = self.ORDER_TYPE

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # SETUP ORDER
        action = ORDER_ACTION[ns_parser.action]
        order_type = ORDER_TYPE[ns_parser.type]
        price = ns_parser.price
        product_id = degiro_model.create_calculate_product_id(
            product=ns_parser.product,
            symbol=ns_parser.symbol,
        )
        size = degiro_model.create_calculate_size(
            price=ns_parser.price,
            size=ns_parser.size,
            up_to=ns_parser.up_to,
        )
        time_type = ORDER_DURATION[ns_parser.duration]
        order = Order(
            action=action,
            order_type=order_type,
            price=price,
            product_id=product_id,
            size=size,
            time_type=time_type,
        )

        # CHECK ORDER
        checking_response = degiro_model.create_check(order=order)
        DegiroView.__create_display_check(
            order=order,
            checking_response=checking_response,
        )

        # USER INPUT
        message_ask = DegiroView.__create_message_ask_confirmation()
        confirmation = input(message_ask)

        # EXECUTE ORDER
        if confirmation in ["y", "yes"]:
            confirmation_id = checking_response.confirmation_id
            confirmation_response = degiro_model.create_confirm(
                confirmation_id=confirmation_id,
                order=order,
            )
            order.id = confirmation_response.orderId
            DegiroView.__create_display_created_order(order=order)
        else:
            DegiroView.__create_display_canceled()

    @staticmethod
    def __create_display_canceled():
        print("`Order` creation canceled.\n")

    @staticmethod
    def __create_display_check(
        order: Order,
        checking_response: Order.CheckingResponse,
    ):
        checking_response_dict = payload_handler.message_to_dict(
            message=checking_response,
        )
        order_dict = payload_handler.message_to_dict(message=order)
        order_df = pd.DataFrame([order_dict])
        fields = [
            "action",
            "order_type",
            "price",
            "product_id",
            "size",
            "time_type",
        ]
        fees = pd.DataFrame(checking_response_dict["transaction_fees"])

        print(
            "The following `Order` will be created :\n\n",
            order_df[fields],
            "\n\nFree new space :",
            checking_response_dict["free_space_new"],
            "\n\nFees :\n\n",
            fees,
        )

    @staticmethod
    def __create_display_created_order(order: Order):
        order_dict = payload_handler.message_to_dict(message=order)
        order_df = pd.DataFrame([order_dict])
        fields = [
            "id",
            "action",
            "order_type",
            "price",
            "product_id",
            "size",
            "time_type",
        ]

        print(
            "The following `Order` was created :\n",
            order_df[order_df.columns.intersection(fields)],
        )

    @staticmethod
    def __create_message_ask_confirmation():
        return "\nDo you confirm this `Order`?\n"

    def hold(self, ns_parser: Namespace):
        _ = ns_parser

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH HELD PRODUCTS
        positions = degiro_model.hold_positions()

        if len(positions) == 0:
            DegiroView.__hold_display_no_position()
        else:
            DegiroView.__hold_display_positions(positions=positions)

    @staticmethod
    def __hold_display_no_position():
        print("0 position found.")

    @staticmethod
    def __hold_display_positions(positions: pd.DataFrame):
        selected_columns = [
            "id",
            "symbol",
            "size",
            "price",
            "closePrice",
            "breakEvenPrice",
        ]
        formatted_columns = [
            "Product Id",
            "Stonk",
            "Size",
            "Last Price",
            "Close Price",
            "Break Even Price",
        ]
        fmt_positions = positions[selected_columns].copy(deep=True)
        fmt_positions.columns = formatted_columns

        fmt_positions["% Change"] = positions["price"]
        fmt_positions["% Change"] -= fmt_positions["Break Even Price"]
        fmt_positions["% Change"] /= fmt_positions["Break Even Price"]
        fmt_positions["% Change"] = fmt_positions["% Change"].round(3)

        print(fmt_positions)

    def lastnews(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model
        latest_news = degiro_model.lastnews(limit=ns_parser.limit)

        # DISPLAY DATA
        DegiroView.__lastnews_display(latest_news=latest_news)

    @staticmethod
    def __lastnews_display(latest_news: LatestNews):
        news_dict = payload_handler.message_to_dict(
            message=latest_news,
        )
        for article in news_dict["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("---")

    def login(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model
        default_credentials = degiro_model.login_default_credentials()

        credentials = Credentials()
        credentials.CopyFrom(default_credentials)
        credentials.username = ns_parser.username
        credentials.password = ns_parser.password

        if ns_parser.otp is not None:
            credentials.one_time_password = ns_parser.otp
        if ns_parser.topt_secret is not None:
            credentials.totp_secret_key = ns_parser.topt_secret

        degiro_model.login(credentials=credentials)

        DegiroView.__login_display_success()

    @staticmethod
    def __login_display_success():
        print("You are now logged in !")

    def logout(self, ns_parser: Namespace):
        _ = ns_parser

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # CALL API
        if degiro_model.logout():
            DegiroView.__logout_display_success()
        else:
            DegiroView.__logout_display_fail()

    @staticmethod
    def __logout_display_fail():
        print("Logged out failed.")

    @staticmethod
    def __logout_display_success():
        print("You are now logged out !")

    def lookup(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FECTH DATA
        product_search = degiro_model.lookup(
            limit=ns_parser.limit,
            offset=ns_parser.offset,
            search_text=ns_parser.search_text,
        )

        # DISPLAY DATA
        if len(product_search.products) > 0:
            DegiroView.__lookup_display(product_search=product_search)
        else:
            DegiroView.__lookup_display_no_result()

    @staticmethod
    def __lookup_display(product_search: ProductSearch):
        products_dict = payload_handler.message_to_dict(
            message=product_search,
        )
        products_df = pd.DataFrame(products_dict["products"])
        products_selected = products_df[
            [
                "id",
                "name",
                "isin",
                "symbol",
                "productType",
                "currency",
                "closePrice",
                "closePriceDate",
            ]
        ]
        print(products_selected)

    @staticmethod
    def __lookup_display_no_result():
        print("0 result found.")

    def pending(self, ns_parser: Namespace):
        _ = ns_parser

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # SETUP REQUEST
        orders = degiro_model.pending()

        # DISPLAY DATA
        if len(orders.values) > 0:
            DegiroView.__pending_display(orders=orders)
        else:
            DegiroView.__pending_display_no_result()

    @staticmethod
    def __pending_display(orders: Update.Orders):
        orders_dict = payload_handler.message_to_dict(message=orders)
        orders_df = pd.DataFrame(orders_dict["values"])
        fields = [
            "action",
            "currency",
            "id",
            "quantity",
            "order_type",
            "price",
            "product",
            "product_id",
            "stop_price",
            "total_order_value",
        ]
        print(orders_df[orders_df.columns.intersection(fields)])

    @staticmethod
    def __pending_display_no_result():
        print("No pending orders.")

    def topnews(self, ns_parser: Namespace):
        _ = ns_parser

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        top_news = degiro_model.topnews()

        # DISPLAY DATA
        DegiroView.__topnews_display(top_news=top_news)

    @staticmethod
    def __topnews_display(top_news: TopNewsPreview):
        news_dict = payload_handler.message_to_dict(
            message=top_news,
        )
        for article in news_dict["items"]:
            print("date", article["date"])
            print("lastUpdated", article["lastUpdated"])
            print("category", article["category"])
            print("title", article["title"])
            print("brief", article["brief"])
            print("---")

    def update(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        order = degiro_model.update_pending_order(
            order_id=ns_parser.id,
        )

        if order is None:
            DegiroView.__update_display_not_found(order_id=ns_parser.id)
        else:
            # SETUP ORDER
            order.price = ns_parser.price

            if degiro_model.update(order=order):
                DegiroView.__update_display_success()
            else:
                DegiroView.__update_display_fail()

    @staticmethod
    def __update_display_fail():
        print("`Order` update failed.")

    @staticmethod
    def __update_display_not_found(order_id: str):
        print("The following `order` was not found:", order_id)

    @staticmethod
    def __update_display_success():
        print("`Order` updated .")
