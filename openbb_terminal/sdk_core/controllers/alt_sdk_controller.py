# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import alt_sdk_model as model


class AltController:
    """OpenBB SDK Alternative Module.

    Submodules:
        `covid`: Covid Module
        `oss`: Oss Module
    """

    @property
    def covid(self):
        """OpenBB SDK Alt Covid Submodule

        Submodules:
            `covid`: Covid Module

        Attributes:
            `global_cases`: Get historical cases for given country\n
            `global_deaths`: Get historical deaths for given country\n
            `ov`: Get historical cases and deaths by country\n
            `ov_view`: Show historical cases and deaths by country\n
            `slopes`: Load cases and find slope over period\n
            `stat`: Show historical cases and deaths by country\n
            `stat_view`: Show historical cases and deaths by country\n
        """

        return model.AltCovid()

    @property
    def oss(self):
        """OpenBB SDK Alt Oss Submodule

        Submodules:
            `oss`: Oss Module

        Attributes:
            `github_data`: Get repository stats\n
            `history`: Get repository star history\n
            `history_view`: Display repo summary [Source: https://api.github.com]\n
            `ross`: Get startups from ROSS index [Source: https://runacap.com/]\n
            `ross_view`: Display list of startups from ross index [Source: https://runacap.com/]\n
            `search`: Get repos sorted by stars or forks. Can be filtered by categories\n
            `summary`: Get repository summary\n
            `summary_view`: Display repo summary [Source: https://api.github.com]\n
            `top`: Get repos sorted by stars or forks. Can be filtered by categories\n
            `top_view`: Display repo summary [Source: https://api.github.com]\n
        """

        return model.AltOss()
