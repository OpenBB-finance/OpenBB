"""Feature Flags Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from typing import List

# IMPORTATION THIRDPARTY
from dotenv import set_key
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


class FeatureFlagsController(BaseController):
    """Feature Flags Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "logcollection",
        "tab",
        "cls",
        "color",
        "ion",
        "watermark",
        "cmdloc",
        "promptkit",
        "predict",
        "thoughts",
        "reporthtml",
        "exithelp",
        "rcontext",
        "rich",
        "richpanel",
        "tbhint",
    ]
    PATH = "/featflags/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("featflags/")
        mt.add_info("_info_")
        mt.add_raw("\n")
        mt.add_setting("logcollection", obbff.LOG_COLLECTION)
        mt.add_setting("tab", obbff.USE_TABULATE_DF)
        mt.add_setting("cls", obbff.USE_CLEAR_AFTER_CMD)
        mt.add_setting("color", obbff.USE_COLOR)
        mt.add_setting("promptkit", obbff.USE_PROMPT_TOOLKIT)
        mt.add_setting("predict", obbff.ENABLE_PREDICT)
        mt.add_setting("thoughts", obbff.ENABLE_THOUGHTS_DAY)
        mt.add_setting("reporthtml", obbff.OPEN_REPORT_AS_HTML)
        mt.add_setting("exithelp", obbff.ENABLE_EXIT_AUTO_HELP)
        mt.add_setting("rcontext", obbff.REMEMBER_CONTEXTS)
        mt.add_setting("rich", obbff.ENABLE_RICH)
        mt.add_setting("richpanel", obbff.ENABLE_RICH_PANEL)
        mt.add_setting("ion", obbff.USE_ION)
        mt.add_setting("watermark", obbff.USE_WATERMARK)
        mt.add_setting("cmdloc", obbff.USE_CMD_LOCATION_FIGURE)
        mt.add_setting("tbhint", obbff.TOOLBAR_HINT)

        console.print(text=mt.menu_text, menu="Feature Flags")

    @log_start_end(log=logger)
    def call_logcollection(self, _):
        """Process logcollection command"""
        obbff.LOG_COLLECTION = not obbff.LOG_COLLECTION
        set_key(obbff.ENV_FILE, "OPENBB_LOG_COLLECTION", str(obbff.LOG_COLLECTION))
        console.print("")

    @log_start_end(log=logger)
    def call_tab(self, _):
        """Process tab command"""
        obbff.USE_TABULATE_DF = not obbff.USE_TABULATE_DF
        set_key(obbff.ENV_FILE, "OPENBB_USE_TABULATE_DF", str(obbff.USE_TABULATE_DF))
        console.print("")

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        obbff.USE_CLEAR_AFTER_CMD = not obbff.USE_CLEAR_AFTER_CMD
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_CLEAR_AFTER_CMD",
            str(obbff.USE_CLEAR_AFTER_CMD),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_color(self, _):
        """Process color command"""
        obbff.USE_COLOR = not obbff.USE_COLOR
        set_key(obbff.ENV_FILE, "OPENBB_USE_COLOR", str(obbff.USE_COLOR))
        console.print("")

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        obbff.USE_PROMPT_TOOLKIT = not obbff.USE_PROMPT_TOOLKIT
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_PROMPT_TOOLKIT",
            str(obbff.USE_PROMPT_TOOLKIT),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_predict(self, _):
        """Process predict command"""
        obbff.ENABLE_PREDICT = not obbff.ENABLE_PREDICT
        set_key(obbff.ENV_FILE, "OPENBB_ENABLE_PREDICT", str(obbff.ENABLE_PREDICT))
        console.print("")

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        obbff.ENABLE_THOUGHTS_DAY = not obbff.ENABLE_THOUGHTS_DAY
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_THOUGHTS_DAY",
            str(obbff.ENABLE_THOUGHTS_DAY),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        obbff.OPEN_REPORT_AS_HTML = not obbff.OPEN_REPORT_AS_HTML
        set_key(
            obbff.ENV_FILE,
            "OPENBB_OPEN_REPORT_AS_HTML",
            str(obbff.OPEN_REPORT_AS_HTML),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        obbff.ENABLE_EXIT_AUTO_HELP = not obbff.ENABLE_EXIT_AUTO_HELP
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_EXIT_AUTO_HELP",
            str(obbff.ENABLE_EXIT_AUTO_HELP),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        obbff.REMEMBER_CONTEXTS = not obbff.REMEMBER_CONTEXTS
        set_key(
            obbff.ENV_FILE,
            "OPENBB_REMEMBER_CONTEXTS",
            str(obbff.REMEMBER_CONTEXTS),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        obbff.USE_DATETIME = not obbff.USE_DATETIME
        set_key(obbff.ENV_FILE, "OPENBB_USE_DATETIME", str(obbff.USE_DATETIME))
        console.print("")

    @log_start_end(log=logger)
    def call_rich(self, _):
        """Process rich command"""
        obbff.ENABLE_RICH = not obbff.ENABLE_RICH
        set_key(obbff.ENV_FILE, "OPENBB_ENABLE_RICH", str(obbff.ENABLE_RICH))
        console.print("")

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        obbff.ENABLE_RICH_PANEL = not obbff.ENABLE_RICH_PANEL
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_RICH_PANEL",
            str(obbff.ENABLE_RICH_PANEL),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_ion(self, _):
        """Process ion command"""
        obbff.USE_ION = not obbff.USE_ION
        set_key(obbff.ENV_FILE, "OPENBB_USE_ION", str(obbff.USE_ION))
        console.print("")

    @log_start_end(log=logger)
    def call_watermark(self, _):
        """Process watermark command"""
        obbff.USE_WATERMARK = not obbff.USE_WATERMARK
        set_key(obbff.ENV_FILE, "OPENBB_USE_WATERMARK", str(obbff.USE_WATERMARK))
        console.print("")

    @log_start_end(log=logger)
    def call_cmdloc(self, _):
        """Process cmdloc command"""
        obbff.USE_CMD_LOCATION_FIGURE = not obbff.USE_CMD_LOCATION_FIGURE
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_CMD_LOCATION_FIGURE",
            str(obbff.USE_CMD_LOCATION_FIGURE),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_tbhint(self, _):
        """Process tbhint command"""
        if obbff.TOOLBAR_HINT:
            console.print("Will take effect when running terminal next.")
        obbff.TOOLBAR_HINT = not obbff.TOOLBAR_HINT
        set_key(
            obbff.ENV_FILE,
            "OPENBB_TOOLBAR_HINT",
            str(obbff.TOOLBAR_HINT),
        )
        console.print("")
