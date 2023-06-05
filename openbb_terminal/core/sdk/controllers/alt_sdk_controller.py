# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import alt_sdk_model as model


class AltController(model.AltRoot):
    """Alternative Module.

    Submodules:
        `covid`: Covid Module
        `oss`: Oss Module
        `realestate`: Realestate Module

    Attributes:
        `hn`: Get top stories from HackerNews.\n
        `hn_chart`: View top stories from HackerNews.\n
    """

    @property
    def covid(self):
        """Alternative Covid Submodule

        Attributes:
            `global_cases`: Get historical cases for given country.\n
            `global_deaths`: Get historical deaths for given country.\n
            `ov`: Get historical cases and deaths by country.\n
            `ov_chart`: Prints table showing historical cases and deaths by country.\n
            `slopes`: Load cases and find slope over period.\n
            `slopes_chart`: Prints table showing countries with the highest case slopes.\n
            `stat`: Show historical cases and deaths by country.\n
            `stat_chart`: Prints table showing historical cases and deaths by country.\n
        """

        return model.AltCovid()

    @property
    def oss(self):
        """Alternative Oss Submodule

        Attributes:
            `_make_request`: Helper method to scrap.\n
            `_retry_session`: Helper methods that retries to make request.\n
            `github_data`: Get repository stats.\n
            `history`: Get repository star history.\n
            `history_chart`: Plots repo summary [Source: https://api.github.com].\n
            `ross`: Get startups from ROSS index [Source: https://runacap.com/].\n
            `ross_chart`: Plots list of startups from ross index [Source: https://runacap.com/]\n
            `search`: Get repos sorted by stars or forks. Can be filtered by categories.\n
            `summary`: Get repository summary.\n
            `summary_chart`: Prints table showing repo summary [Source: https://api.github.com].\n
            `top`: Get repos sorted by stars or forks. Can be filtered by categories.\n
            `top_chart`: Plots repo summary [Source: https://api.github.com].\n
        """

        return model.AltOss()

    @property
    def realestate(self):
        """Alternative Realestate Submodule

        Attributes:
            `get_estate_sales`: All sales for specified postcode.\n
            `get_region_stats`: Get regional house price statistics.\n
            `get_towns_sold_prices`: Get towns sold house price data.\n
        """

        return model.AltRealestate()
