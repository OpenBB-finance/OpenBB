# IMPORTATION THIRDPARTY
import logging
from argparse import Namespace
from typing import Optional

# IMPORTATION THIRDPARTY
import pandas as pd
from degiro_connector.core.helpers import pb_handler
from degiro_connector.trading.models.trading_pb2 import (
    LatestNews,
    NewsByCompany,
    Order,
    ProductSearch,
    TopNewsPreview,
    Update,
)

from openbb_terminal.decorators import check_api_key, log_start_end

# IMPORTATION INTERNAL
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.portfolio.brokers.degiro.degiro_model import DegiroModel
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=no-member


logger = logging.getLogger(__name__)


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

    @log_start_end(log=logger)
    def __init__(self):
        self.__degiro_model = DegiroModel()

    @staticmethod
    @log_start_end(log=logger)
    def help_display():
        mt = MenuText("portfolio/bro/degiro/")
        mt.add_cmd("login")
        mt.add_cmd("logout")
        mt.add_raw("\n")
        mt.add_cmd("hold")
        mt.add_cmd("lookup")
        mt.add_raw("\n")
        mt.add_cmd("create")
        mt.add_cmd("update")
        mt.add_cmd("cancel")
        mt.add_cmd("pending")
        mt.add_raw("\n")
        mt.add_cmd("companynews")
        mt.add_cmd("lastnews")
        mt.add_cmd("topnews")
        mt.add_cmd("paexport")
        console.print(text=mt.menu_text, menu="Portfolio - Brokers - Degiro")

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __cancel_display_success(order_id: str):
        console.print(f"Following `Order` was canceled : {order_id}")

    @staticmethod
    @log_start_end(log=logger)
    def __cancel_display_fail(order_id: str):
        console.print(f"Following `Order` cancellation failed : {order_id}")

    @log_start_end(log=logger)
    def companynews(
        self, symbol: str, limit: int = 10, offset: int = 0, languages: str = "en,fr"
    ):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        news_by_company = degiro_model.companynews(
            symbol=symbol, limit=limit, offset=offset, languages=languages
        )

        # DISPLAY DATA
        if news_by_company:
            DegiroView.__companynews_display(news_by_company=news_by_company)

    @staticmethod
    @log_start_end(log=logger)
    def __companynews_display(news_by_company: NewsByCompany):
        news_dict = pb_handler.message_to_dict(
            message=news_by_company,
        )
        for article in news_dict["items"]:
            console.print("date", article["date"])
            console.print("title", article["title"])
            console.print("content", article["content"])
            console.print("isins", article["isins"])
            console.print("---")

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __create_display_canceled():
        console.print("`Order` creation canceled.\n")

    @staticmethod
    @log_start_end(log=logger)
    def __create_display_check(
        order: Order,
        checking_response: Order.CheckingResponse,
    ):
        checking_response_dict = pb_handler.message_to_dict(
            message=checking_response,
        )
        order_dict = pb_handler.message_to_dict(message=order)
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

        console.print(
            "The following `Order` will be created :\n\n",
            order_df[fields],
            "\n\nFree new space :",
            checking_response_dict["free_space_new"],
            "\n\nFees :\n\n",
            fees,
        )

    @staticmethod
    @log_start_end(log=logger)
    def __create_display_created_order(order: Order):
        order_dict = pb_handler.message_to_dict(message=order)
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

        console.print(
            "The following `Order` was created :\n",
            order_df[order_df.columns.intersection(fields)],
        )

    @staticmethod
    @log_start_end(log=logger)
    def __create_message_ask_confirmation():
        return "\nDo you confirm this `Order`?\n"

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __hold_display_no_position():
        console.print("0 position found.")

    @staticmethod
    @log_start_end(log=logger)
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

        console.print(fmt_positions)

    @log_start_end(log=logger)
    def lastnews(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model
        latest_news = degiro_model.lastnews(limit=ns_parser.limit)

        # DISPLAY DATA
        DegiroView.__lastnews_display(latest_news=latest_news)

    @staticmethod
    @log_start_end(log=logger)
    def __lastnews_display(latest_news: LatestNews):
        news_dict = pb_handler.message_to_dict(
            message=latest_news,
        )
        for article in news_dict["items"]:
            console.print("date", article["date"])
            console.print("title", article["title"])
            console.print("content", article["content"])
            console.print("---")

    @log_start_end(log=logger)
    @check_api_key(["DG_USERNAME", "DG_PASSWORD"])
    def login(self, otp: Optional[int] = None):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model
        credentials = degiro_model.login_default_credentials()

        if otp is not None:
            credentials.one_time_password = otp

        degiro_model.login()

        if degiro_model.check_session_id():
            DegiroView.__login_display_success()

    @staticmethod
    @log_start_end(log=logger)
    def __login_display_success():
        console.print("You are now logged in !")

    @log_start_end(log=logger)
    def logout(self):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # CALL API
        if degiro_model.logout():
            DegiroView.__logout_display_success()
            DegiroModel.reset_sessionid_and_creds(self.__degiro_model)
        else:
            DegiroView.__logout_display_fail()

    @staticmethod
    @log_start_end(log=logger)
    def __logout_display_fail():
        console.print("Logged out failed.")

    @staticmethod
    @log_start_end(log=logger)
    def __logout_display_success():
        console.print("You are now logged out !")

    @log_start_end(log=logger)
    def lookup(self, ns_parser: Namespace):
        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
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
    @log_start_end(log=logger)
    def __lookup_display(product_search: ProductSearch):
        products_dict = pb_handler.message_to_dict(
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
        console.print(products_selected)

    @staticmethod
    @log_start_end(log=logger)
    def __lookup_display_no_result():
        console.print("0 result found.")

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __pending_display(orders: Update.Orders):
        orders_dict = pb_handler.message_to_dict(message=orders)
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
        console.print(orders_df[orders_df.columns.intersection(fields)])

    @staticmethod
    @log_start_end(log=logger)
    def __pending_display_no_result():
        console.print("No pending orders.")

    @log_start_end(log=logger)
    def topnews(self, ns_parser: Namespace):
        _ = ns_parser

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        top_news = degiro_model.topnews()

        # DISPLAY DATA
        if top_news:
            DegiroView.__topnews_display(top_news=top_news)

    @staticmethod
    @log_start_end(log=logger)
    def __topnews_display(top_news: TopNewsPreview):
        news_dict = pb_handler.message_to_dict(
            message=top_news,
        )
        for article in news_dict["items"]:
            console.print("date", article["date"])
            console.print("lastUpdated", article["lastUpdated"])
            console.print("category", article["category"])
            console.print("title", article["title"])
            console.print("brief", article["brief"])
            console.print("---")

    @log_start_end(log=logger)
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
    @log_start_end(log=logger)
    def __update_display_fail():
        console.print("`Order` update failed.")

    @staticmethod
    @log_start_end(log=logger)
    def __update_display_not_found(order_id: str):
        console.print("The following `order` was not found:", order_id)

    @staticmethod
    @log_start_end(log=logger)
    def __update_display_success():
        console.print("`Order` updated .")

    @log_start_end(log=logger)
    def transactions_export(self, ns_parser: Namespace):
        degiro_model = self.__degiro_model

        portfolio_df = degiro_model.get_transactions_export(
            start=ns_parser.start.date(),
            end=ns_parser.end.date(),
            currency=ns_parser.currency,
        )

        if portfolio_df is not None:
            print_rich_table(
                df=portfolio_df,
                headers=list(portfolio_df.columns),
                show_index=True,
                title="Degiro Transactions",
            )

            degiro_model.export_data(portfolio_df, ns_parser.export)

        else:
            console.print("Error while fetching or processing Transactions.")
