# IMPORTATION STANDARD
import argparse

# IMPORTATION THIRDPARTY
from prompt_toolkit.completion import NestedCompleter
from trading.pb.trading_pb2 import (
    Credentials,
    Order,
)

# IMPORTATION INTERNAL
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.degiro_model import DegiroModel
from gamestonk_terminal.portfolio.degiro_view import DegiroView

# pylint: disable=no-member


class DegiroController:
    CHOICES = [
        "cancel",
        "companynews",
        "create",
        "hold",
        "lastnews",
        "login",
        "logout",
        "lookup",
        "pending",
        "q",
        "quit",
        "topnews",
        "update",
    ]

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

        self.__degiro_parser = argparse.ArgumentParser(
            add_help=False,
            prog="degiro",
        )
        self.__degiro_parser.add_argument("cmd", choices=self.CHOICES)

    def cancel(self, l_args):
        """Cancel an order using the `id`."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # CANCEL ORDER
        order_id = ns_parser.id

        # DISPLAY DATA
        if degiro_model.cancel(order_id=order_id):
            DegiroView.cancel_display_success(order_id=order_id)
        else:
            DegiroView.cancel_display_fail(order_id=order_id)

    def companynews(self, l_args):
        """Display news related to a company using its ISIN."""

        # PARSE ARGS
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
        degiro_model = self.__degiro_model

        # FETCH DATA
        news_by_company = degiro_model.companynews(isin=ns_parser.isin)

        # DISPLAY DATA
        DegiroView.companynews_display(news_by_company=news_by_company)

    def create(self, l_args):
        """Create an order."""

        # GET CONSTANTS
        ORDER_ACTION = self.ORDER_ACTION
        ORDER_DURATION = self.ORDER_DURATION
        ORDER_TYPE = self.ORDER_TYPE

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="create",
        )
        parser.add_argument(
            "-a",
            "--action",
            choices=ORDER_ACTION.keys(),
            default="buy",
            help="Action wanted.",
            required=False,
            type=str,
        )
        product_group = parser.add_mutually_exclusive_group(
            required=True,
        )
        product_group.add_argument(
            "-prod",
            "--product",
            help="Id of the product wanted.",
            required=False,
            type=int,
        )
        product_group.add_argument(
            "-sym",
            "--symbol",
            help="Symbol wanted.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required=True,
            type=float,
        )
        size_group = parser.add_mutually_exclusive_group(required=True)
        size_group.add_argument(
            "-s",
            "--size",
            help="Price wanted.",
            required=False,
            type=int,
        )
        size_group.add_argument(
            "-up",
            "--up-to",
            help="Up to price.",
            required=False,
            type=float,
        )
        parser.add_argument(
            "-d",
            "--duration",
            default="gtd",
            choices=ORDER_DURATION.keys(),
            help="Duration of the Order.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-t",
            "--type",
            choices=ORDER_TYPE.keys(),
            default="limit",
            help="Type of the Order.",
            required=False,
            type=str,
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # SETUP ORDER
        action = self.ORDER_ACTION[ns_parser.action]
        order_type = self.ORDER_TYPE[ns_parser.type]
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
        time_type = self.ORDER_DURATION[ns_parser.duration]
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
        DegiroView.create_display_check(
            order=order,
            checking_response=checking_response,
        )

        # USER INPUT
        message_ask = DegiroView.create_message_ask_confirmation()
        confirmation = input(message_ask)

        # EXECUTE ORDER
        if confirmation in ["y", "yes"]:
            confirmation_id = checking_response.confirmation_id
            confirmation_response = degiro_model.create_confirm(
                confirmation_id=confirmation_id,
                order=order,
            )
            order.id = confirmation_response.orderId
            DegiroView.create_display_created_order(order=order)
        else:
            DegiroView.create_display_canceled()

    def help(self):
        """Show the help menu."""

        DegiroView.help_display()

    def hold(self, _):
        """Display held products."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH HELD PRODUCTS
        positions = degiro_model.hold_positions()

        if len(positions) == 0:
            DegiroView.hold_display_no_position()
        else:
            DegiroView.hold_display_positions(positions=positions)

    def lastnews(self, l_args):
        """Display latest news."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lastnews",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            type=int,
            help="Number of news to display.",
            required=False,
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)
        latest_news = degiro_model.lastnews(limit=ns_parser.limit)

        # DISPLAY DATA
        DegiroView.lastnews_display(latest_news=latest_news)

    def login(self, l_args):
        """Connect to Degiro's API."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # PARSE ARGS
        default_credentials = degiro_model.login_default_credentials()
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="login",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=default_credentials.username,
            help="Username in Degiro's account.",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            default=default_credentials.password,
            help="Password in Degiro's account.",
        )
        parser.add_argument(
            "-o",
            "--otp",
            type=int,
            default=None,
            help="One time password (2FA).",
        )
        parser.add_argument(
            "-s",
            "--topt-secret",
            type=str,
            default=None,
            help="TOTP SECRET (2FA).",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if ns_parser:
            credentials = Credentials()
            credentials.CopyFrom(default_credentials)
            credentials.username = ns_parser.username
            credentials.password = ns_parser.password

            if ns_parser.otp is not None:
                credentials.one_time_password = ns_parser.otp
            if ns_parser.topt_secret is not None:
                credentials.totp_secret_key = ns_parser.topt_secret

            degiro_model.login(credentials=credentials)

            DegiroView.login_display_success()

    def logout(self, _):
        """Log out from Degiro's API."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # CALL API
        if degiro_model.logout():
            DegiroView.logout_display_success()
        else:
            DegiroView.logout_display_fail()

    def lookup(self, l_args):
        """Search for products by their name."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

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

        # FECTH DATA
        product_search = degiro_model.lookup(
            limit=ns_parser.limit,
            offset=ns_parser.offset,
            search_text=ns_parser.search_text,
        )

        # DISPLAY DATA
        if len(product_search.products) > 0:
            DegiroView.lookup_display(product_search=product_search)
        else:
            DegiroView.lookup_display_no_result()

    def pending(self, _):
        """Display pending orders."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # SETUP REQUEST
        orders = degiro_model.pending()

        # DISPLAY DATA
        if len(orders.values) > 0:
            DegiroView.pending_display(orders=orders)
        else:
            DegiroView.pending_display_no_result()

    def q(self, _):
        """Process Q command - quit the menu."""

        DegiroView.q_display()

        return False

    def quit(self, _):
        """Process Quit command - quit the program."""

        DegiroView.quit_display()

        return True

    def topnews(self, _):
        """Display top news."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # FETCH DATA
        top_news = degiro_model.topnews()

        # DISPLAY DATA
        DegiroView.topnews_display(top_news=top_news)

    def update(self, l_args):
        """Update an order."""

        # GET ATTRIBUTES
        degiro_model = self.__degiro_model

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="update",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required=True,
            type=float,
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        # FETCH DATA
        order = degiro_model.update_pending_order(
            order_id=ns_parser.id,
        )

        if order is None:
            DegiroView.update_display_not_found(order_id=ns_parser.id)
        else:
            # SETUP ORDER
            order.price = ns_parser.price

            if degiro_model.update(order=order):
                DegiroView.update_display_success()
            else:
                DegiroView.update_display_fail()

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

    # SETUP CONTROLLER
    degiro_controller = DegiroController()
    degiro_controller.help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in degiro_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (pa)>(degiro)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (pa)>(degiro)> ")

        try:
            process_input = degiro_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
