__docformat__ = "numpy"

# pylint: disable=R1710

import logging
from typing import List, Optional, Set

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.coinbase import coinbase_controller
from openbb_terminal.portfolio.brokers.degiro import degiro_controller
from openbb_terminal.portfolio.brokers.robinhood import robinhood_controller
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class BrokersController(BaseController):
    """Brokers Controller class"""

    CHOICES_COMMANDS: List = []
    CHOICES_MENUS = ["cb", "ally", "rh", "degiro"]
    PATH = "/portfolio/bro/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.broker_list: Set = set()
        self.merged_holdings = None

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/bro/")
        mt.add_menu("degiro")
        mt.add_menu("rh")
        mt.add_menu("cb")
        console.print(text=mt.menu_text, menu="Portfolio - Brokers")

    @log_start_end(log=logger)
    def call_degiro(self, _):
        """Process degiro command."""
        self.queue = self.load_class(degiro_controller.DegiroController, self.queue)

    @log_start_end(log=logger)
    def call_rh(self, _):
        """Process rh command."""
        self.queue = self.load_class(
            robinhood_controller.RobinhoodController, self.queue
        )

    @log_start_end(log=logger)
    def call_cb(self, _):
        """Process coinbase command."""
        self.queue = self.load_class(coinbase_controller.CoinbaseController, self.queue)

    # TODO: Consistent way of merging across brokers including crypto
    # def call_login(self, other_args):
    #    """Process login command"""
    #    logged_in = False
    #    if not other_args:
    #        console.print("Please enter brokers you wish to login to")
    #        console.print("")
    #        return
    #    for broker in other_args:
    #        if broker in self.BROKERS:
    #            api = broker + "_api"
    #            try:
    #                # pylint: disable=eval-used
    #                eval(api + ".login()")
    #                self.broker_list.add(broker)
    #                logged_in = True
    #            except Exception as e:
    #                console.print("")
    #                console.print(f"Error at broker : {broker}")
    #                console.print(e)
    #                console.print("Make sure credentials are defined in config_terminal.py ")
    #                console.print("")
    #        else:
    #            console.print(f"{broker} not supported")
