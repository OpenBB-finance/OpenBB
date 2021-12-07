import os

from dotenv import load_dotenv

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# Choose one of: stocks, options, crypto, economy, etf, portfolio, forex
DEFAULT_CONTEXT = ""

# Set to True to see full stack traces for debugging/error reporting
DEBUG_MODE = False

# By default the jupyter notebook will be run on port 8888
PAPERMILL_NOTEBOOK_REPORT_PORT = "8888"

# https://www.alphavantage.co
API_KEY_ALPHAVANTAGE = os.getenv("GT_API_KEY_ALPHAVANTAGE") or "REPLACE_ME"

# https://financialmodelingprep.com/developer
API_KEY_FINANCIALMODELINGPREP = (
    os.getenv("GT_API_KEY_FINANCIALMODELINGPREP") or "REPLACE_ME"
)

# https://www.quandl.com/tools/api
API_KEY_QUANDL = os.getenv("GT_API_KEY_QUANDL") or "REPLACE_ME"

# https://www.reddit.com/prefs/apps
API_REDDIT_CLIENT_ID = os.getenv("GT_API_REDDIT_CLIENT_ID") or "REPLACE_ME"
API_REDDIT_CLIENT_SECRET = os.getenv("GT_API_REDDIT_CLIENT_SECRET") or "REPLACE_ME"
API_REDDIT_USERNAME = os.getenv("GT_API_REDDIT_USERNAME") or "REPLACE_ME"
API_REDDIT_USER_AGENT = os.getenv("GT_API_REDDIT_USER_AGENT") or "REPLACE_ME"
API_REDDIT_PASSWORD = os.getenv("GT_API_REDDIT_PASSWORD") or "REPLACE_ME"

# https://polygon.io
API_POLYGON_KEY = os.getenv("GT_API_POLYGON_KEY") or "REPLACE_ME"

# https://developer.twitter.com
API_TWITTER_KEY = os.getenv("GT_API_TWITTER_KEY") or "REPLACE_ME"
API_TWITTER_SECRET_KEY = os.getenv("GT_API_TWITTER_SECRET_KEY") or "REPLACE_ME"
API_TWITTER_BEARER_TOKEN = os.getenv("GT_API_TWITTER_BEARER_TOKEN") or "REPLACE_ME"

# https://fred.stlouisfed.org/docs/api/api_key.html
API_FRED_KEY = os.getenv("GT_API_FRED_KEY") or "REPLACE_ME"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("GT_API_NEWS_TOKEN") or "REPLACE_ME"

# Robinhood
RH_USERNAME = os.getenv("GT_RH_USERNAME") or "REPLACE_ME"
RH_PASSWORD = os.getenv("GT_RH_PASSWORD") or "REPLACE_ME"

# Degiro
DG_USERNAME = os.getenv("GT_DG_USERNAME") or "REPLACE_ME"
DG_PASSWORD = os.getenv("GT_DG_PASSWORD") or "REPLACE_ME"
DG_TOTP_SECRET = os.getenv("GT_DG_TOTP_SECRET") or None

# https://developer.oanda.com
OANDA_ACCOUNT_TYPE = (
    os.getenv("GT_OANDA_ACCOUNT_TYPE") or "practice"
)  # "live" or "practice"
OANDA_ACCOUNT = os.getenv("GT_OANDA_ACCOUNT") or "REPLACE_ME"
OANDA_TOKEN = os.getenv("GT_OANDA_TOKEN") or "REPLACE_ME"

# https://tradier.com/products/market-data-api
TRADIER_TOKEN = os.getenv("GT_API_TRADIER_TOKEN") or "REPLACE_ME"

# Selenium Webbrowser drivers can be found at https://selenium-python.readthedocs.io/installation.html
WEBDRIVER_TO_USE = "chrome"
PATH_TO_SELENIUM_DRIVER = None  # Replace with "PATH"

# https://coinmarketcap.com/api/
API_CMC_KEY = os.getenv("GT_API_CMC_KEY") or "REPLACE_ME"

# https://www.binance.com/en/
API_BINANCE_KEY = os.getenv("GT_API_BINANCE_KEY") or "REPLACE_ME"
API_BINANCE_SECRET = os.getenv("GT_API_BINANCE_SECRET") or "REPLACE_ME"

# https://finnhub.io
API_FINNHUB_KEY = os.getenv("GT_API_FINNHUB_KEY") or "REPLACE_ME"

# https://iexcloud.io
API_IEX_TOKEN = os.getenv("GT_API_IEX_KEY") or "REPLACE_ME"

# https://www.sentimentinvestor.com
API_SENTIMENTINVESTOR_KEY = os.getenv("GT_API_SENTIMENTINVESTOR_KEY") or "REPLACE_ME"
API_SENTIMENTINVESTOR_TOKEN = (
    os.getenv("GT_API_SENTIMENTINVESTOR_TOKEN") or "REPLACE_ME"
)

# https://pro.coinbase.com/profile/api
API_COINBASE_KEY = os.getenv("GT_API_COINBASE_KEY") or "REPLACE_ME"
API_COINBASE_SECRET = os.getenv("GT_API_COINBASE_SECRET") or "REPLACE_ME"
API_COINBASE_PASS_PHRASE = os.getenv("GT_API_COINBASE_PASS_PHRASE") or "REPLACE_ME"

# https://alpaca.markets/docs/api-documentation/api-v2/
# GT_APCA_API_BASE_URL, GT_APCA_API_KEY_ID and GT_APCA_API_SECRET_KEY need to be set as env variable

# https://docs.whale-alert.io/
API_WHALE_ALERT_KEY = os.getenv("GT_API_WHALE_ALERT_KEY") or "REPLACE_ME"

# https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key
API_GLASSNODE_KEY = os.getenv("GT_API_GLASSNODE_KEY") or "REPLACE_ME"

# https://coinglass.github.io/API-Reference/#api-key
API_COINGLASS_KEY = os.getenv("GT_API_COINGLASS_KEY") or "REPLACE_ME"

# https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API
API_ETHPLORER_KEY = os.getenv("GT_API_ETHPLORER_KEY") or "freekey"

# https://cryptopanic.com/developers/api/
API_CRYPTO_PANIC_KEY = os.getenv("GT_API_CRYPTO_PANIC_KEY") or "REPLACE_ME"
