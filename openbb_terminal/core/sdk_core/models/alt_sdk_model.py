# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class AltRoot(Category):
    """Alternative Module

    Attributes:
        `hn`: Get top stories from HackerNews.\n
        `hn_chart`: View top stories from HackerNews.\n
    """

    _location_path = "alt"

    def __init__(self):
        super().__init__()
        self.hn = lib.alt_hackernews_model.get_stories
        self.hn_chart = lib.alt_hackernews_view.display_stories


class AltCovid(Category):
    """Covid Module.

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

    _location_path = "alt.covid"

    def __init__(self):
        super().__init__()
        self.global_cases = lib.alt_covid_model.get_global_cases
        self.global_deaths = lib.alt_covid_model.get_global_deaths
        self.ov = lib.alt_covid_model.get_covid_ov
        self.ov_chart = lib.alt_covid_view.display_covid_ov
        self.slopes = lib.alt_covid_model.get_case_slopes
        self.slopes_chart = lib.alt_covid_view.display_case_slopes
        self.stat = lib.alt_covid_model.get_covid_stat
        self.stat_chart = lib.alt_covid_view.display_covid_stat


class AltOss(Category):
    """Oss Module.

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

    _location_path = "alt.oss"

    def __init__(self):
        super().__init__()
        self._make_request = lib.alt_oss_runa_model._make_request
        self._retry_session = lib.alt_oss_runa_model._retry_session
        self.github_data = lib.alt_oss_github_model.get_github_data
        self.history = lib.alt_oss_github_model.get_stars_history
        self.history_chart = lib.alt_oss_github_view.display_star_history
        self.ross = lib.alt_oss_runa_model.get_startups
        self.ross_chart = lib.alt_oss_runa_view.display_rossindex
        self.search = lib.alt_oss_github_model.search_repos
        self.summary = lib.alt_oss_github_model.get_repo_summary
        self.summary_chart = lib.alt_oss_github_view.display_repo_summary
        self.top = lib.alt_oss_github_model.get_top_repos
        self.top_chart = lib.alt_oss_github_view.display_top_repos


class AltRealestate(Category):
    """Realestate Module.

    Attributes:
        `get_estate_sales`: All sales for specified postcode.\n
        `get_region_stats`: Get regional house price statistics.\n
        `get_towns_sold_prices`: Get towns sold house price data.\n
    """

    _location_path = "alt.realestate"

    def __init__(self):
        super().__init__()
        self.get_estate_sales = lib.alt_realestate_landRegistry_model.get_estate_sales
        self.get_region_stats = lib.alt_realestate_landRegistry_model.get_region_stats
        self.get_towns_sold_prices = (
            lib.alt_realestate_landRegistry_model.get_towns_sold_prices
        )
