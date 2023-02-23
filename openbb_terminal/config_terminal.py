# IMPORTATION STANDARD
import os

# IMPORTATION INTERNAL
from openbb_terminal.base_helpers import load_env_vars, strtobool
from .helper_classes import TerminalStyle as _TerminalStyle


SENSITIVE_KEYS = [
    "RH_USERNAME",
    "RH_PASSWORD",
    "DG_USERNAME",
    "DG_PASSWORD",
    "DG_TOTP_SECRET",
    "OANDA_ACCOUNT_TYPE",
    "OANDA_ACCOUNT",
    "OANDA_TOKEN",
]

# Network requests
# Set request timeout
REQUEST_TIMEOUT = load_env_vars("OPENBB_REQUEST_TIMEOUT", int, 5)

# Terminal UX section
MPL_STYLE = os.getenv("OPENBB_MPLSTYLE") or "dark"
PMF_STYLE = os.getenv("OPENBB_PMFSTYLE") or "dark"
RICH_STYLE = os.getenv("OPENBB_RICHSTYLE") or "dark"

theme = _TerminalStyle(
    MPL_STYLE,
    PMF_STYLE,
    RICH_STYLE,
)

# By default the jupyter notebook will be run on port 8888
PAPERMILL_NOTEBOOK_REPORT_PORT = (
    "8888"  # This setting is deprecated and seems to be unused
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


# Selenium Webbrowser drivers can be found at https://selenium-python.readthedocs.io/installation.html
WEBDRIVER_TO_USE = "chrome"
PATH_TO_SELENIUM_DRIVER = ""  # Replace with "PATH"
