# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import i18n
from openbb_terminal.core.config import paths_helper

# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.base_helpers import load_env_vars, strtobool
from openbb_terminal.core.session.current_user import get_current_user
from .helper_classes import TerminalStyle as _TerminalStyle

LOCAL_KEYS = [
    "RH_USERNAME",
    "RH_PASSWORD",
    "DG_USERNAME",
    "DG_PASSWORD",
    "DG_TOTP_SECRET",
    "OANDA_ACCOUNT_TYPE",
    "OANDA_ACCOUNT",
    "OANDA_TOKEN",
    "API_TRADIER_TOKEN",
    "API_BINANCE_KEY",
    "API_BINANCE_SECRET",
    "API_COINBASE_KEY",
    "API_COINBASE_SECRET",
    "API_COINBASE_PASS_PHRASE",
]

# # Terminal UX section
current_user = get_current_user()
theme = _TerminalStyle(
    current_user.preferences.MPL_STYLE,
    current_user.preferences.PMF_STYLE,
    current_user.preferences.RICH_STYLE,
)

# Logging section

# USE IN LOG LINES + FOR FOLDER NAME INSIDE S3 BUCKET
if "site-packages" in __file__:
    LOGGING_APP_NAME = "gst_packaged_pypi"
else:
    LOGGING_APP_NAME = os.getenv("OPENBB_LOGGING_APP_NAME") or "gst"
# AWS KEYS
LOGGING_AWS_ACCESS_KEY_ID = (
    os.getenv("OPENBB_LOGGING_AWS_ACCESS_KEY_ID") or "REPLACE_ME"
)
LOGGING_AWS_SECRET_ACCESS_KEY = (
    os.getenv("OPENBB_LOGGING_AWS_SECRET_ACCESS_KEY") or "REPLACE_ME"
)
LOGGING_COMMIT_HASH = str(os.getenv("OPENBB_LOGGING_COMMIT_HASH", "REPLACE_ME"))
# D | H | M | S
LOGGING_FREQUENCY = os.getenv("OPENBB_LOGGING_FREQUENCY") or "H"
# stdout,stderr,noop,file
LOGGING_HANDLERS = os.getenv("OPENBB_LOGGING_HANDLERS") or "file"
LOGGING_ROLLING_CLOCK = load_env_vars("OPENBB_LOGGING_ROLLING_CLOCK", strtobool, False)
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
LOGGING_VERBOSITY = load_env_vars("OPENBB_LOGGING_VERBOSITY", int, 20)
# LOGGING SUB APP
LOGGING_SUB_APP = os.getenv("OPENBB_LOGGING_SUB_APP") or "terminal"
LOGGING_SUPPRESS = False


paths_helper.init_userdata()

# pylint: disable=no-member,c-extension-no-member

try:
    __import__("git")
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True


try:
    if not WITH_GIT:
        import pkg_resources

        version = pkg_resources.get_distribution("OpenBB").version
    else:
        raise Exception("Using git")
except Exception:
    version = "2.4.1"
VERSION = str(os.getenv("OPENBB_VERSION", version))

# # Select the terminal translation language
i18n_dict_location = MISCELLANEOUS_DIRECTORY / "i18n"
i18n.load_path.append(i18n_dict_location)
i18n.set("locale", get_current_user().preferences.USE_LANGUAGE)
i18n.set("filename_format", "{locale}.{format}")
