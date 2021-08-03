import os
from dotenv import load_dotenv

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])

# By default the jupyter notebook will be run on port 8888
PAPERMILL_NOTEBOOK_REPORT_PORT = "8888"

# https://www.alphavantage.co
API_KEY_ALPHAVANTAGE = os.getenv("XS7HK2PAF5XU4QGX") or "XS7HK2PAF5XU4QGX"

# https://financialmodelingprep.com/developer
API_KEY_FINANCIALMODELINGPREP = (
    os.getenv("0ae3163febc1ff2717772df696651276") or "0ae3163febc1ff2717772df696651276"
)

# https://www.quandl.com/tools/api
API_KEY_QUANDL = os.getenv("RzKS3jxHL_8Sgdq5cy_A") or "RzKS3jxHL_8Sgdq5cy_A"

# https://www.reddit.com/prefs/apps
API_REDDIT_CLIENT_ID = os.getenv("GT_API_REDDIT_CLIENT_ID") or "REPLACE_ME"
API_REDDIT_CLIENT_SECRET = os.getenv("GT_API_REDDIT_CLIENT_SECRET") or "REPLACE_ME"
API_REDDIT_USERNAME = os.getenv("Maddccc") or "Maddccc"
API_REDDIT_USER_AGENT = os.getenv("GT_API_REDDIT_USER_AGENT") or "REPLACE_ME"
API_REDDIT_PASSWORD = os.getenv("Rasengantao99!?") or "Rasengantao99!?"

# https://polygon.io
API_POLYGON_KEY = os.getenv("GT_API_POLYGON_KEY") or "REPLACE_ME"

# https://developer.twitter.com
API_TWITTER_KEY = os.getenv("GT_API_TWITTER_KEY") or "REPLACE_ME"
API_TWITTER_SECRET_KEY = os.getenv("GT_API_TWITTER_SECRET_KEY") or "REPLACE_ME"
API_TWITTER_BEARER_TOKEN = os.getenv("GT_API_TWITTER_BEARER_TOKEN") or "REPLACE_ME"

# https://fred.stlouisfed.org/docs/api/api_key.html
API_FRED_KEY = os.getenv("0072f0794714b69566c52f8afba6708e") or "0072f0794714b69566c52f8afba6708e"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("1e17d823bba24d03851608d28c1631e8") or "1e17d823bba24d03851608d28c1631e8"

# Robinhood
RH_USERNAME = os.getenv("GT_RH_USERNAME") or "REPLACE_ME"
RH_PASSWORD = os.getenv("GT_RH_PASSWORD") or "REPLACE_ME"

# Degiro
DG_USERNAME = os.getenv("GT_DG_USERNAME") or "REPLACE_ME"
DG_PASSWORD = os.getenv("GT_DG_PASSWORD") or "REPLACE_ME"
DG_TOTP_SECRET = os.getenv("GT_DG_TOTP_SECRET") or None

# https://developer.oanda.com
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
