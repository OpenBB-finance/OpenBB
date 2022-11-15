# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class AltCovid(Category):
    """OpenBB SDK Covid Module.

    Attributes:
        `global_cases`: Get historical cases for given country.\n
        `global_deaths`: Get historical deaths for given country.\n
        `ov`: Get historical cases and deaths by country.\n
        `ov_print`: Prints table showing historical cases and deaths by country.\n
        `slopes`: Load cases and find slope over period.\n
        `slopes_print`: Prints table showing countries with the highest case slopes.\n
        `stat`: Show historical cases and deaths by country.\n
        `stat_print`: Prints table showing historical cases and deaths by country.\n
    """

    def __init__(self):
        super().__init__()
        self.global_cases = lib.alt_covid_model.get_global_cases
        self.global_deaths = lib.alt_covid_model.get_global_deaths
        self.ov = lib.alt_covid_model.get_covid_ov
        self.ov_print = lib.alt_covid_view.display_covid_ov
        self.slopes = lib.alt_covid_model.get_case_slopes
        self.slopes_print = lib.alt_covid_view.display_case_slopes
        self.stat = lib.alt_covid_model.get_covid_stat
        self.stat_print = lib.alt_covid_view.display_covid_stat


class AltOss(Category):
    """OpenBB SDK Oss Module.

    Attributes:
        `github_data`: Get repository stats.\n
        `history`: Get repository star history.\n
        `history_chart`: Plots repo summary [Source: https://api.github.com].\n
        `ross`: Get startups from ROSS index [Source: https://runacap.com/].\n
        `ross_chart`: Plots list of startups from ross index [Source: https://runacap.com/]\n
        `search`: Get repos sorted by stars or forks. Can be filtered by categories.\n
        `summary`: Get repository summary.\n
        `summary_print`: Prints table showing repo summary [Source: https://api.github.com].\n
        `top`: Get repos sorted by stars or forks. Can be filtered by categories.\n
        `top_chart`: Plots repo summary [Source: https://api.github.com].\n
    """

    def __init__(self):
        super().__init__()
        self.github_data = lib.alt_oss_github_model.get_github_data
        self.history = lib.alt_oss_github_model.get_stars_history
        self.history_chart = lib.alt_oss_github_view.display_star_history
        self.ross = lib.alt_oss_runa_model.get_startups
        self.ross_chart = lib.alt_oss_runa_view.display_rossindex
        self.search = lib.alt_oss_github_model.search_repos
        self.summary = lib.alt_oss_github_model.get_repo_summary
        self.summary_print = lib.alt_oss_github_view.display_repo_summary
        self.top = lib.alt_oss_github_model.get_top_repos
        self.top_chart = lib.alt_oss_github_view.display_top_repos
