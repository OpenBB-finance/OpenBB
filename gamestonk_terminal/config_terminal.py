import os
from dotenv import load_dotenv

load_dotenv()

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
API_FRED_KEY = os.getenv("GT_FRED_API_KEY") or "b98e15f1fde39212bce9213f2e3e5afb"

# https://newsapi.org
API_NEWS_TOKEN = os.getenv("GT_API_NEWS_TOKEN") or "REPLACE_ME"

# Robinhood
RH_USERNAME = os.getenv("GT_RH_USERNAME") or "REPLACE_ME"
RH_PASSWORD = os.getenv("GT_RH_PASSWORD") or "REPLACE_ME"

# Degiro
DG_USERNAME = os.getenv("GT_DG_USERNAME") or "REPLACE_ME"
DG_PASSWORD = os.getenv("GT_DG_PASSWORD") or "REPLACE_ME"

# https://developer.oanda.com
OANDA_ACCOUNT = os.getenv("GT_OANDA_ACCOUNT") or "REPLACE ME"
OANDA_TOKEN = os.getenv("GT_OANDA_TOKEN") or "REPLACE ME"

# https://tradier.com/products/market-data-api
TRADIER_TOKEN = os.getenv("GT_TRADIER_TOKEN") or "REPLACE_ME"

# Selenium Webbrowser drivers can be found at https://selenium-python.readthedocs.io/installation.html
WEBDRIVER_TO_USE = "chrome"
PATH_TO_SELENIUM_DRIVER = None  # Replace with "PATH"

# https://coinmarketcap.com/api/
COINMARKETCAP_KEY = os.getenv("GT_CMC_API_KEY") or "REPLACE_ME"

# https://finnhub.io
API_FINNHUB_KEY = os.getenv("GT_API_FINNHUB_KEY") or "c23k26qad3ieeb1lftug"
