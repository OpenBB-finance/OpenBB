# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class Root(Category):
    """Module

    Attributes:
        `login`: Login and load user info.\n
        `logout`: Logout and clear session.\n
        `news`: Get news for a given term and source. [Source: Feedparser]\n
        `whoami`: Display user info.\n
    """

    _location_path = ""

    def __init__(self):
        super().__init__()
        self.login = lib.sdk_session.login
        self.logout = lib.sdk_session.logout
        self.news = lib.common_feedparser_model.get_news
        self.whoami = lib.sdk_session.whoami
