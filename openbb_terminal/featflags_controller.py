"""Feature Flags Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from typing import List, Optional, Union

# IMPORTATION THIRDPARTY
from dotenv import set_key

# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import SETTINGS_ENV_FILE
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.core.session.hub_model import patch_user_configs
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
    set_current_user,
)

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


class FeatureFlagsController(BaseController):
    """Feature Flags Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "retryload",
        "tab",
        "cls",
        "color",
        "ion",
        "watermark",
        "cmdloc",
        "promptkit",
        "thoughts",
        "reporthtml",
        "exithelp",
        "rcontext",
        "rich",
        "richpanel",
        "tbhint",
        "overwrite",
    ]
    PATH = "/featflags/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        current_user = get_current_user()

        mt = MenuText("featflags/")
        mt.add_info("_info_")
        mt.add_raw("\n")
        mt.add_setting("retryload", current_user.preferences.RETRY_WITH_LOAD)
        mt.add_setting("tab", current_user.preferences.USE_TABULATE_DF)
        mt.add_setting("cls", current_user.preferences.USE_CLEAR_AFTER_CMD)
        mt.add_setting("color", current_user.preferences.USE_COLOR)
        mt.add_setting("promptkit", current_user.preferences.USE_PROMPT_TOOLKIT)
        mt.add_setting("thoughts", current_user.preferences.ENABLE_THOUGHTS_DAY)
        mt.add_setting("reporthtml", current_user.preferences.OPEN_REPORT_AS_HTML)
        mt.add_setting("exithelp", current_user.preferences.ENABLE_EXIT_AUTO_HELP)
        mt.add_setting("rcontext", current_user.preferences.REMEMBER_CONTEXTS)
        mt.add_setting("rich", current_user.preferences.ENABLE_RICH)
        mt.add_setting("richpanel", current_user.preferences.ENABLE_RICH_PANEL)
        mt.add_setting("ion", current_user.preferences.USE_ION)
        mt.add_setting("watermark", current_user.preferences.USE_WATERMARK)
        mt.add_setting("cmdloc", current_user.preferences.USE_CMD_LOCATION_FIGURE)
        mt.add_setting("tbhint", current_user.preferences.TOOLBAR_HINT)
        mt.add_setting("overwrite", current_user.preferences.FILE_OVERWRITE)

        console.print(text=mt.menu_text, menu="Feature Flags")

    @staticmethod
    def set_feature_flag(name: str, value: Union[bool, str], force: bool = False):
        """Set feature flag

        Parameters
        ----------
        name : str
            Environment variable name
        value : str
            Environment variable value
        force : bool, optional
            Force remote storage of feature flag, by default False
        """

        current_user = get_current_user()
        sync_enabled = current_user.preferences.SYNC_ENABLED
        local_user = is_local()

        if local_user:
            set_key(str(SETTINGS_ENV_FILE), name, str(value))

        # Remove "OPENBB_" prefix from env_var
        if name.startswith("OPENBB_"):
            name = name[7:]

        # Set current_user.preferences.name = value
        setattr(current_user.preferences, name, value)
        set_current_user(current_user)

        # Send feature flag to server
        if not sync_enabled and sync_enabled or force:
            patch_user_configs(
                key=name,
                value=str(value),
                type_="settings",
                auth_header=current_user.profile.get_auth_header(),
            )

    def call_overwrite(self, _):
        """Process overwrite command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_FILE_OVERWITE", not get_current_user().preferences.FILE_OVERWRITE
        )

    def call_retryload(self, _):
        """Process retryload command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_RETRY_WITH_LOAD", not get_current_user().preferences.RETRY_WITH_LOAD
        )

    @log_start_end(log=logger)
    def call_tab(self, _):
        """Process tab command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_TABULATE_DF", not get_current_user().preferences.USE_TABULATE_DF
        )

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_CLEAR_AFTER_CMD",
            not get_current_user().preferences.USE_CLEAR_AFTER_CMD,
        )

    @log_start_end(log=logger)
    def call_color(self, _):
        """Process color command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_COLOR", not get_current_user().preferences.USE_COLOR
        )

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_PROMPT_TOOLKIT",
            not get_current_user().preferences.USE_PROMPT_TOOLKIT,
        )

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_ENABLE_THOUGHTS_DAY",
            not get_current_user().preferences.ENABLE_THOUGHTS_DAY,
        )

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_OPEN_REPORT_AS_HTML",
            not get_current_user().preferences.OPEN_REPORT_AS_HTML,
        )

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_ENABLE_EXIT_AUTO_HELP",
            not get_current_user().preferences.ENABLE_EXIT_AUTO_HELP,
        )

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_REMEMBER_CONTEXTS",
            not get_current_user().preferences.REMEMBER_CONTEXTS,
        )

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_DATETIME", not get_current_user().preferences.USE_DATETIME
        )

    @log_start_end(log=logger)
    def call_rich(self, _):
        """Process rich command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_ENABLE_RICH", not get_current_user().preferences.ENABLE_RICH
        )

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_ENABLE_RICH_PANEL",
            not get_current_user().preferences.ENABLE_RICH_PANEL,
        )

    @log_start_end(log=logger)
    def call_ion(self, _):
        """Process ion command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_ION", not get_current_user().preferences.USE_ION
        )

    @log_start_end(log=logger)
    def call_watermark(self, _):
        """Process watermark command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_WATERMARK", not get_current_user().preferences.USE_WATERMARK
        )

    @log_start_end(log=logger)
    def call_cmdloc(self, _):
        """Process cmdloc command"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_USE_CMD_LOCATION_FIGURE",
            not get_current_user().preferences.USE_CMD_LOCATION_FIGURE,
        )

    @log_start_end(log=logger)
    def call_tbhint(self, _):
        """Process tbhint command"""
        if get_current_user().preferences.TOOLBAR_HINT:
            console.print("Will take effect when running terminal next.")
        FeatureFlagsController.set_feature_flag(
            "OPENBB_TOOLBAR_HINT", not get_current_user().preferences.TOOLBAR_HINT
        )
