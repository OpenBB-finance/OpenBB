# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class RootRoot(Category):
    """OpenBB SDK Root Module

    Attributes:
        `news`: Get news for a given term and source. [Source: Feedparser]\n
        `news_view`: Plots news for a given term and source. [Source: Feedparser]\n
    """

    def __init__(self):
        super().__init__()
        self.news = lib.common_feedparser_model.get_news
        self.news_view = lib.common_feedparser_view.display_news
