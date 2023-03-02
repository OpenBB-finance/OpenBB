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
LOGGING_APP_NAME = (
    "gst_packaged_pypi"
    if "site-packages" in __file__
    else os.getenv("OPENBB_LOGGING_APP_NAME") or "gst"
)
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

# API Keys section

# https://www.alphavantage.co
API_KEY_ALPHAVANTAGE = os.getenv("OPENBB_API_KEY_ALPHAVANTAGE") or "REPLACE_ME"

# https://financialmodelingprep.com/developer
API_KEY_FINANCIALMODELINGPREP = (
    os.getenv("OPENBB_API_KEY_FINANCIALMODELINGPREP") or "REPLACE_ME"
)

# https://www.quandl.com/tools/api
API_KEY_QUANDL = os.getenv("OPENBB_API_KEY_QUANDL") or "REPLACE_ME"

# https://www.reddit.com/prefs/apps
API_REDDIT_CLIENT_ID = os.getenv("OPENBB_API_REDDIT_CLIENT_ID") or "REPLACE_ME"
API_REDDIT_CLIENT_SECRET = os.getenv("OPENBB_API_REDDIT_CLIENT_SECRET") or "REPLACE_ME"
API_REDDIT_USERNAME = os.getenv("OPENBB_API_REDDIT_USERNAME") or "REPLACE_ME"
API_REDDIT_USER_AGENT = os.getenv("OPENBB_API_REDDIT_USER_AGENT") or "REPLACE_ME"
API_REDDIT_PASSWORD = os.getenv("OPENBB_API_REDDIT_PASSWORD") or "REPLACE_ME"

# https://polygon.io
API_POLYGON_KEY = os.getenv("OPENBB_API_POLYGON_KEY") or "REPLACE_ME"

# https://developer.twitter.com
API_TWITTER_BEARER_TOKEN = os.getenv("OPENBB_API_TWITTER_BEARER_TOKEN") or "REPLACE_ME"

# https://fred.stlouisfed.org/docs/api/api_key.html
API_FRED_KEY = os.getenv("OPENBB_API_FRED_KEY") or "REPLACE_ME"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("OPENBB_API_NEWS_TOKEN") or "REPLACE_ME"

# Robinhood
RH_USERNAME = os.getenv("OPENBB_RH_USERNAME") or "REPLACE_ME"
RH_PASSWORD = os.getenv("OPENBB_RH_PASSWORD") or "REPLACE_ME"

# Degiro
DG_USERNAME = os.getenv("OPENBB_DG_USERNAME") or "REPLACE_ME"
DG_PASSWORD = os.getenv("OPENBB_DG_PASSWORD") or "REPLACE_ME"
DG_TOTP_SECRET = os.getenv("OPENBB_DG_TOTP_SECRET") or None

# https://developer.oanda.com
OANDA_ACCOUNT_TYPE = os.getenv("OPENBB_OANDA_ACCOUNT_TYPE") or "REPLACE_ME"
# "live" or "practice"
OANDA_ACCOUNT = os.getenv("OPENBB_OANDA_ACCOUNT") or "REPLACE_ME"
OANDA_TOKEN = os.getenv("OPENBB_OANDA_TOKEN") or "REPLACE_ME"

# https://tradier.com/products/market-data-api
API_TRADIER_TOKEN = os.getenv("OPENBB_API_TRADIER_TOKEN") or "REPLACE_ME"

# Selenium Webbrowser drivers can be found at https://selenium-python.readthedocs.io/installation.html
WEBDRIVER_TO_USE = "chrome"
PATH_TO_SELENIUM_DRIVER = ""  # Replace with "PATH"

# https://coinmarketcap.com/api/
API_CMC_KEY = os.getenv("OPENBB_API_CMC_KEY") or "REPLACE_ME"

# https://www.binance.com/en/
API_BINANCE_KEY = os.getenv("OPENBB_API_BINANCE_KEY") or "REPLACE_ME"
API_BINANCE_SECRET = os.getenv("OPENBB_API_BINANCE_SECRET") or "REPLACE_ME"

# https://finnhub.io
API_FINNHUB_KEY = os.getenv("OPENBB_API_FINNHUB_KEY") or "REPLACE_ME"

# https://iexcloud.io
API_IEX_TOKEN = os.getenv("OPENBB_API_IEX_TOKEN") or "REPLACE_ME"

# https://www.sentimentinvestor.com
API_SENTIMENTINVESTOR_TOKEN = (
    os.getenv("OPENBB_API_SENTIMENTINVESTOR_TOKEN") or "REPLACE_ME"
)

# https://pro.coinbase.com/profile/api
API_COINBASE_KEY = os.getenv("OPENBB_API_COINBASE_KEY") or "REPLACE_ME"
API_COINBASE_SECRET = os.getenv("OPENBB_API_COINBASE_SECRET") or "REPLACE_ME"
API_COINBASE_PASS_PHRASE = os.getenv("OPENBB_API_COINBASE_PASS_PHRASE") or "REPLACE_ME"

# https://alpaca.markets/docs/api-documentation/api-v2/
# OPENBB_APCA_API_BASE_URL, OPENBB_APCA_API_KEY_ID and OPENBB_APCA_API_SECRET_KEY need to be set as env variable

# https://docs.whale-alert.io/
API_WHALE_ALERT_KEY = os.getenv("OPENBB_API_WHALE_ALERT_KEY") or "REPLACE_ME"

# https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key
API_GLASSNODE_KEY = os.getenv("OPENBB_API_GLASSNODE_KEY") or "REPLACE_ME"

# https://coinglass.github.io/API-Reference/#api-key
API_COINGLASS_KEY = os.getenv("OPENBB_API_COINGLASS_KEY") or "REPLACE_ME"

# https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API
API_ETHPLORER_KEY = os.getenv("OPENBB_API_ETHPLORER_KEY") or "freekey"

# https://cryptopanic.com/developers/api/
API_CRYPTO_PANIC_KEY = os.getenv("OPENBB_API_CRYPTO_PANIC_KEY") or "REPLACE_ME"

# https://bitquery.io/pricing
API_BITQUERY_KEY = os.getenv("OPENBB_API_BITQUERY_KEY") or "REPLACE_ME"

# https://terra.smartstake.io/
API_SMARTSTAKE_KEY = os.getenv("OPENBB_API_SMARTSTAKE_KEY") or "REPLACE_ME"
API_SMARTSTAKE_TOKEN = os.getenv("OPENBB_API_SMARTSTAKE_TOKEN") or "REPLACE_ME"

# https://messari.io/
API_MESSARI_KEY = os.getenv("OPENBB_API_MESSARI_KEY") or "REPLACE_ME"

# https://sdk.flipsidecrypto.xyz/shroomdk
API_SHROOM_KEY = os.getenv("OPENBB_API_SHROOM_KEY") or "REPLACE_ME"

# https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api
API_GITHUB_KEY = os.getenv("OPENBB_API_GITHUB_KEY") or "REPLACE_ME"

# https://academy.santiment.net/products-and-plans/create-an-api-key/
API_SANTIMENT_KEY = os.getenv("OPENBB_API_SANTIMENT_KEY") or "REPLACE_ME"

# https://eodhistoricaldata.com/r/?ref=869U7F4J
API_EODHD_KEY = os.getenv("OPENBB_API_EODHD_KEY") or "REPLACE_ME"

# https://tokenterminal.com
API_TOKEN_TERMINAL_KEY = os.getenv("OPENBB_API_TOKEN_TERMINAL_KEY") or "REPLACE_ME"

# https://stocksera.pythonanywhere.com/accounts/developers
API_STOCKSERA_KEY = os.getenv("OPENBB_API_STOCKSERA_KEY") or "REPLACE_ME"

# https://my.openbb.co
OPENBB_PERSONAL_ACCESS_TOKEN = (
    os.getenv("OPENBB_OPENBB_PERSONAL_ACCESS_TOKEN") or "REPLACE_ME"
)

# https://intrinio.com/starter-plan
API_INTRINIO_KEY = os.getenv("OPENBB_API_INTRINIO_KEY") or "REPLACE_ME"

# https://databento.com/
API_DATABENTO_KEY = os.getenv("OPENBB_API_DATABENTO_KEY") or "REPLACE_ME"
