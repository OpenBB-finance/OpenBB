# IMPORTATION THIRDPARTY
import pandas as pd
import trading.helpers.payload_handler as payload_handler

from trading.pb.trading_pb2 import (
    LatestNews,
    NewsByCompany,
    Order,
    ProductSearch,
    TopNewsPreview,
    Update,
)

class DegiroView:
    @staticmethod
    def help_display():
        print(
            "Degiro:\n"
            "   cancel      cancel an order using the `id`\n"
            "   companynews view news about a company with it's isin\n"
            "   create      create an order.\n"
            "   hold        view holdings\n"
            "   lastnews    view latest news\n"
            "   login       connect to degiro's api\n"
            "   logout      disconnect from degiro's api\n"
            "   lookup      view search for a product by name\n"
            "   pending     view pending orders\n"
            "   q           quit degiro integration\n"
            "   quit        quit the app\n"
            "   topnews     view top news preview\n"
            "   update      view top news preview\n"
        )

    @staticmethod
    def cancel_display_success(order_id: str):
        print(f"Following `Order` was canceled : {order_id}")

    @staticmethod
    def cancel_display_fail(order_id: str):
        print(f"Following `Order` cancelation failed : {order_id}")

    @staticmethod
    def create_display_canceled():
        print("`Order` creation canceled.\n")

    @staticmethod
    def create_display_check(
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
    def companynews_display(news_by_company: NewsByCompany):
        news_dict = payload_handler.message_to_dict(
            message=news_by_company,
        )
        for article in news_dict["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("isins", article["isins"])
            print("---")

    @staticmethod
    def create_display_created_order(order: Order):
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
            "The following `Order` was created :",
            order_df[fields],
        )

    @staticmethod
    def create_message_ask_confirmation():
        return "\nDo you confirm this `Order`?\n"

    @staticmethod
    def hold_display_no_position():
        print("0 position found.")

    @staticmethod
    def hold_display_positions(positions: pd.DataFrame):
        selected_columns = [
            "symbol",
            "size",
            "price",
            "closePrice",
            "breakEvenPrice",
        ]
        formatted_columns = [
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

    @staticmethod
    def lastnews_display(latest_news: LatestNews):
        news_dict = payload_handler.message_to_dict(
            message=latest_news,
        )
        for article in news_dict["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("---")

    @staticmethod
    def login_display_success():
        print("You are now logged in !")

    @staticmethod
    def logout_display_fail():
        print("You are now logged out !")

    @staticmethod
    def logout_display_success():
        print("You are now logged out !")

    @staticmethod
    def lookup_display(product_search: ProductSearch):
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
    def lookup_display_no_result():
        print("0 result found.")

    @staticmethod
    def pending_display(orders: Update.Orders):
        orders_dict = payload_handler.message_to_dict(message=orders)
        orders_df = pd.DataFrame(orders_dict["values"])
        print(orders_df)

    @staticmethod
    def pending_display_no_result():
        print("No pending orders.")

    @staticmethod
    def q_display():
        print("Quit Degiro integration.")

    @staticmethod
    def quit_display():
        print("Quit the app.")

    @staticmethod
    def topnews_display(top_news: TopNewsPreview):
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

    @staticmethod
    def update_display_fail():
        print("`Order` update failed.")

    @staticmethod
    def update_display_not_found(order_id: str):
        print("The following `order` was not found:", order_id)
    
    @staticmethod
    def update_display_success():
        print("`Order` updated .")
