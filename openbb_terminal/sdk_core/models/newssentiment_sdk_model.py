# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class NewssentimentRoot(Category):
    """Newssentiment Module

    Attributes:
        `show_chart`: Display Onclusive Data. [Source: Invisage Plotform] \n
    """

    _location_path = "newssentiment"

    def __init__(self):
        super().__init__()
        self.show = lib.news_onclusivedata_model.get_data
        self.show_chart = lib.news_onclusivedata_view.display_articles_data
