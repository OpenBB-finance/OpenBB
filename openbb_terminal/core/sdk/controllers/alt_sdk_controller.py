# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import alt_sdk_model as model


class AltController(model.AltRoot):
    """Alternative Module.

    Submodules:
        `companieshouse`: Companieshouse Module
        `oss`: Oss Module
        `realestate`: Realestate Module

    Attributes:
        `hn`: Get top stories from HackerNews.\n
        `hn_chart`: View top stories from HackerNews.\n
    """

    @property
    def companieshouse(self):
        """Alternative Companieshouse Submodule

        Attributes:
            `download_filing_document`: Download company's filing document.\n
            `get_company_info`: Gets company info by company number\n
            `get_filing_document`: Download given filing document pdf\n
            `get_filings`: Gets information on filings for given company, e.g. accounts, etc\n
            `get_officers`: Gets information on company officers\n
            `get_persons_with_significant_control`: Gets information on persons with significant control over the company\n
            `get_search_results`: All companies with searchStr in their name.\n
        """

        return model.AltCompanieshouse()

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
