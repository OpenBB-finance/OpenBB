# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class FundsRoot(Category):
    """OpenBB SDK Mutual Funds Module

    Attributes:
        `info_chart`: Display fund information.  Finds name from symbol first if name is false\n
        `overview_chart`: Displays an overview of the main funds from a country.\n
        `search`: Search investpy for matching funds\n
        `search_chart`: Display results of searching for Mutual Funds\n
    """

    def __init__(self):
        super().__init__()
        self.info = lib.mutual_funds_investpy_model.get_fund_info
        self.info_chart = lib.mutual_funds_investpy_view.display_fund_info
        self.overview = lib.mutual_funds_investpy_model.get_overview
        self.overview_chart = lib.mutual_funds_investpy_view.display_overview
        self.search = lib.mutual_funds_investpy_model.search_funds
        self.search_chart = lib.mutual_funds_investpy_view.display_search
