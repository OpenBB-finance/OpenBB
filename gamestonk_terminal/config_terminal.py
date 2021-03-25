import os

# https://www.alphavantage.co
API_KEY_ALPHAVANTAGE = "YG6O8II69KI4442A"

# https://financialmodelingprep.com/developer
API_KEY_FINANCIALMODELINGPREP = "9367508cfa9057d92ed34833fb5ca391"

# https://www.quandl.com/tools/api
API_KEY_QUANDL = "CDqeCd-8K7ZbbW6MsXze"

# https://www.reddit.com/prefs/apps
API_REDDIT_CLIENT_ID = "QONuVuzTVM7GMw"
API_REDDIT_CLIENT_SECRET = "JbE0qH33MG-cPXeLf7VUQHovDsk3Rw"
API_REDDIT_USERNAME = "Zealousideal_Bet_166"
API_REDDIT_USER_AGENT = os.getenv("GT_API_REDDIT_USER_AGENT") or "REPLACE_ME"
API_REDDIT_PASSWORD = "000000"

# https://developer.twitter.com
API_TWITTER_KEY = "79bGybWWZSSjrFHV82TWmkkwq"
API_TWITTER_SECRET_KEY = "t4ehddBLuapQjgjVsn1SGceZsCTR3aj8rtqnxdXfX4ArIKK5ZK"
API_TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJeOMwEAAAAAJznaPHgB8ihCD3Tnf4zOQ%2B0DnlQ%3DTref2q3tyOENH50lIcbne0lcA1jZGoiiwiJCAdlhYj3I2sjVpJ"

# https://polygon.io
API_POLYGON_KEY = "XcTGzVQnpae584IN9UW9lmC0wFmCWNfZ"

# https://fred.stlouisfed.org/docs/api/api_key.html
API_FRED_KEY = os.getenv("GT_FRED_API_KEY") or "REPLACE_ME"

# https://newsapi.org
API_NEWS_TOKEN = "77cec90bcdae40559cd9d8edf7dd89d3"

# Robinhood
RH_USERNAME = os.getenv("GT_RH_USERNAME") or "REPLACE_ME"
RH_PASSWORD = os.getenv("GT_RH_PASSWORD") or "REPLACE_ME"
