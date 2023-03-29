# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class FundsRoot(Category):
    """Mutual Funds Module

    Attributes:
        `carbon`: Search mstarpy for carbon metrics\n
        `exclusion`: Search mstarpy exclusion policy in esgData\n
        `historical`: Get historical fund, category, index price\n
        `historical_chart`: Display historical fund, category, index price\n
        `holdings`: Search mstarpy for holdings\n
        `load`: Search mstarpy for matching funds\n
        `search`: Search mstarpy for matching funds\n
        `sector`: Get fund, category, index sector breakdown\n
        `sector_chart`: Display fund, category, index sector breakdown\n
    """

    _location_path = "funds"

    def __init__(self):
        super().__init__()
        self.carbon = lib.funds_mstarpy_model.load_carbon_metrics
        self.exclusion = lib.funds_mstarpy_model.load_exclusion_policy
        self.historical = lib.funds_mstarpy_model.get_historical
        self.historical_chart = lib.funds_mstarpy_view.display_historical
        self.holdings = lib.funds_mstarpy_model.load_holdings
        self.load = lib.funds_mstarpy_model.load_funds
        self.search = lib.funds_mstarpy_model.search_funds
        self.sector = lib.funds_mstarpy_model.get_sector
        self.sector_chart = lib.funds_mstarpy_view.display_sector
