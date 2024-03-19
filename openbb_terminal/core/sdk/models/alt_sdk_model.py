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


class AltCompanieshouse(Category):
    """Companieshouse Module.

    Attributes:
        `download_filing_document`: Download company's filing document.\n
        `get_company_info`: Gets company info by company number\n
        `get_filing_document`: Download given filing document pdf\n
        `get_filings`: Gets information on filings for given company, e.g. accounts, etc\n
        `get_officers`: Gets information on company officers\n
        `get_persons_with_significant_control`: Gets information on persons with significant control over the company\n
        `get_search_results`: All companies with searchStr in their name.\n
    """

    _location_path = "alt.companieshouse"

    def __init__(self):
        super().__init__()
        self.download_filing_document = (
            lib.alt_companieshouse_companieshouse_view.download_filing_document
        )
        self.get_charges = lib.alt_companieshouse_companieshouse_view.display_charges
        self.get_company_info = (
            lib.alt_companieshouse_companieshouse_model.get_company_info
        )
        self.get_filing_document = (
            lib.alt_companieshouse_companieshouse_model.get_filing_document
        )
        self.get_filings = lib.alt_companieshouse_companieshouse_model.get_filings
        self.get_officers = lib.alt_companieshouse_companieshouse_model.get_officers
        self.get_persons_with_significant_control = (
            lib.alt_companieshouse_companieshouse_model.get_persons_with_significant_control
        )
        self.get_search_results = (
            lib.alt_companieshouse_companieshouse_model.get_search_results
        )


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
