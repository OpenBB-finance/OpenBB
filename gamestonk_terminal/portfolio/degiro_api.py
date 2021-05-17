# IMPORTATION STANDARD
import argparse

# IMPORTATION THIRDPARTY
import pandas as pd
import quotecast.helpers.pb_handler as pb_handler

from prompt_toolkit.completion import NestedCompleter
from trading.api import API as TradingAPI
from trading.pb.trading_pb2 import (
    Credentials,
    LatestNews,
    NewsByCompany,
    ProductsInfo,
    ProductSearch,
    Update,
)

# IMPORTATION INTERNAL
import gamestonk_terminal.config_terminal as config

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session


class DegiroController:
    CHOICES = [
        "companynews",
        "hold",
        "lastnews",
        "login",
        "logout",
        "lookup",
        "pending",
        "q",
        "quit",
        "topnews",
    ]

    @staticmethod
    def filter_current_positions(
        portfolio: Update.Portfolio,
    ) -> pd.DataFrame:
        """Filter the positions in order to keep only held ones.

        Parameters
        ----------
        portfolio : Update.Portfolio
            Portfolio returned from the API.

        Returns
        -------
        pd.DataFrame
            Filtered portfolio.
        """

        # CONVERT TO DATAFRAME
        portfolio_dict = pb_handler.message_to_dict(message=portfolio)
        positions = pd.DataFrame(portfolio_dict["values"])

        # SETUP MASK
        mask_product = positions["positionType"] == "PRODUCT"
        mask_not_empty = positions["size"] > 0
        mask_current_position = mask_product & mask_not_empty

        # FILTER
        positions = positions[mask_current_position]

        return positions

    def __init__(self, credentials: Credentials):
        self.__trading_api = TradingAPI(credentials=credentials)

        self.__degiro_parser = argparse.ArgumentParser(
            add_help=False,
            prog="degiro",
        )
        self.__degiro_parser.add_argument("cmd", choices=self.CHOICES)

    def q(self, _):
        """Process Q command - quit the menu"""

        return False

    def quit(self, _):
        """Process Quit command - quit the program"""

        return True

    def fetch_additional_information(
        self,
        positions: pd.DataFrame,
    ) -> pd.DataFrame:
        """Fetch extra information about the positions like :
            - name
            - isin
            - symbol
            - ...

        Parameters
        ----------
        positions : pd.DataFrame
            Positions from which we want extra fields.

        Returns
        -------
        pd.DataFrame
            Positions with additional data.
        """

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # EXTRACT POSITIONS IDS
        positions_ids = positions["id"].astype("int32").tolist()

        # FETCH EXTRA DATA
        request = ProductsInfo.Request()
        request.products.extend(positions_ids)
        products_info_pb = trading_api.get_products_info(
            request=request,
            raw=False,
        )

        # CONVERT TO DICT
        products_info_dict = pb_handler.message_to_dict(
            message=products_info_pb,
        )

        # CONVERT TO DATAFRAME
        products_info = pd.DataFrame(products_info_dict["values"].values())

        # MERGE DATA WITH POSITIONS
        positions_full = pd.merge(positions, products_info, on="id")

        return positions_full

    def fetch_current_positions(self) -> pd.DataFrame:
        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # FETCH HELD PRODUCTS
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(
                    option=Update.Option.PORTFOLIO,
                    last_updated=0,
                ),
            ]
        )

        update_pb = trading_api.get_update(
            request_list=request_list,
            raw=False,
        )
        positions_partial = self.filter_current_positions(
            portfolio=update_pb.portfolio,
        )

        # FETCH ADDITIONAL DATA ON PRODUCTS
        positions = self.fetch_additional_information(
            positions=positions_partial,
        )

        return positions

    def help(self):
        message = (
            "Degiro:\n"
            "    companynews view news about a company with it's isin\n"
            "    hold        view holdings\n"
            "    lastnews    view latest news\n"
            "    login       connect to degiro api\n"
            "    lookup      view search for a product by name\n"
            "    pending     view pending orders\n"
            "    topnews     view top news preview\n"
        )

        print(message)

    def login(self, _):
        """Connect to Degiro's API."""

        trading_api = self.__trading_api

        trading_api.connect()
        self.setup_extra_credentials()

        print("You are now logged in !")

    def logout(self, _):
        """Log out from Degiro's API."""

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        trading_api.logout()

        print("You are now logged out !")

    def setup_extra_credentials(self):
        trading_api = self.__trading_api
        client_details_table = trading_api.get_client_details()
        int_account = client_details_table["data"]["intAccount"]
        trading_api.credentials.int_account = int_account

    def hold(self, _):
        """Display held products."""

        # FETCH HELD PRODUCTS
        positions = self.fetch_current_positions()

        # FORMAT DATAFRAME
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
        fmt_positions["% Change"] -= fmt_positions["Close Price"]
        fmt_positions["% Change"] /= fmt_positions["Close Price"]
        fmt_positions["% Change"] = fmt_positions["% Change"].round(3)

        # DISPLAY DATAFRAME
        print(fmt_positions)

    def topnews(self, _):
        """Display pending orders."""

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # FETCH DATA
        news = trading_api.get_top_news_preview(raw=True)

        # DISPLAY DATA
        for article in news["data"]["items"]:
            print("date", article["date"])
            print("lastUpdated", article["lastUpdated"])
            print("category", article["category"])
            print("title", article["title"])
            print("brief", article["brief"])
            print("---")

    def lookup(self, l_args):
        """Search for products by their name."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lookup",
        )
        parser.add_argument(
            "search_text",
            type=str,
            help="Name of the company or a text.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=10,
            help="Number of result expected (0 for unlimited).",
        )
        parser.add_argument(
            "-o",
            "--offset",
            type=int,
            default=0,
            help="To use an offset.",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # SETUP REQUEST
        limit = ns_parser.limit
        offset = ns_parser.offset
        search_text = ns_parser.search_text
        request_lookup = ProductSearch.RequestLookup(
            search_text=search_text,
            limit=limit,
            offset=offset,
        )

        # FETCH DATA
        products = trading_api.product_search(
            request=request_lookup,
            raw=True,
        )

        # DISPLAY DATA
        if "products" in products:
            products_df = pd.DataFrame(products["products"])
            products_selected = products_df[
                [
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
        else:
            print("0 results found.")

    def lastnews(self, _):
        """Display latest news."""

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # SETUP REQUEST
        request = LatestNews.Request(
            offset=0,
            languages="en,fr",
            limit=20,
        )

        # FETCH DATA
        news = trading_api.get_latest_news(request=request, raw=True)

        # DISPLAY DATA
        for article in news["data"]["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("---")

    def companynews(self, l_args):
        """Display news related to a company using its ISIN."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "isin",
            type=str,
            help="ISIN code of the company.",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # SETUP REQUEST
        isin = ns_parser.isin
        request = NewsByCompany.Request(
            isin=isin,
            limit=10,
            offset=0,
            languages="en,fr",
        )

        # FETCH DATA
        news = trading_api.get_news_by_company(
            request=request,
            raw=True,
        )

        # DISPLAY DATA
        for article in news["data"]["items"]:
            print("date", article["date"])
            print("title", article["title"])
            print("content", article["content"])
            print("isins", article["isins"])
            print("---")

    def pending(self, _):
        """Display pending orders."""

        # GET ATTRIBUTES
        trading_api = self.__trading_api

        # SETUP REQUEST
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.ORDERS, last_updated=0),
            ]
        )

        # FETCH DATA
        update = trading_api.get_update(request_list=request_list)

        # FORMAT DATA
        update_dict = pb_handler.message_to_dict(message=update)
        orders_df = pd.DataFrame(update_dict["orders"]["values"])

        # DISPLAY DATA
        if orders_df.shape[0] == 0:
            print("No pending orders.")
        else:
            print(orders_df)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        try:
            degiro_parser = self.__degiro_parser

            (known_args, other_args) = degiro_parser.parse_known_args(an_input.split())

            return getattr(
                self,
                known_args.cmd,
                lambda: "Command not recognized!",
            )(other_args)
        except Exception as e:
            print(e)
            print("")

            return None


def menu():
    """Degiro Menu"""

    # SETUP CREDENTIALS
    credentials = Credentials(
        int_account=None,
        username=config.DG_USERNAME,
        password=config.DG_PASSWORD,
        one_time_password=config.DG_TOTP,
        totp_secret_key=config.DG_TOTP_SECRET,
    )

    # SETUP CONTROLLER
    degiro_controller = DegiroController(credentials=credentials)
    degiro_controller.help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in degiro_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (pa) > (degiro)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (pa) > (degiro)> ")

        try:
            process_input = degiro_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
