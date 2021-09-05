#!/bin/bash

clear

echo "Setting up the Terminal Launcher"

read -r -s PAPERMILL_NOTEBOOK_REPORT_PORT
read -r -s TERMINAL_PATH
read -r -s PATH_TO_SELENIUM_DRIVER
read -r -s WEBDRIVER_TO_USE

echo "Setting up application features"

read -r -s GTFF_USE_CLEAR_AFTER_CMD
read -r -s GTFF_USE_COLOR
read -r -s GTFF_USE_FLAIR
read -r -s GTFF_USE_ION
read -r -s GTFF_USE_PROMPT_TOOLKIT
read -r -s GTFF_ENABLE_PREDICT
read -r -s GTFF_USE_PLOT_AUTOSCALING
read -r -s GTFF_ENABLE_THOUGHTS_DAY
read -r -s GTFF_ENABLE_QUICK_EXIT

echo "Setting up API keys"

read -r -s GT_API_KEY_ALPHAVANTAGE
read -r -s GT_API_KEY_FINANCIALMODELINGPREP
read -r -s GT_API_KEY_QUANDL
read -r -s GT_API_REDDIT_CLIENT_ID
read -r -s GT_API_REDDIT_CLIENT_SECRET
read -r -s GT_API_REDDIT_USERNAME
read -r -s GT_API_REDDIT_USER_AGENT
read -r -s GT_API_REDDIT_PASSWORD
read -r -s GT_API_POLYGON_KEY
read -r -s GT_API_TWITTER_KEY
read -r -s GT_API_TWITTER_SECRET_KEY
read -r -s GT_API_TWITTER_BEARER_TOKEN
read -r -s GT_API_FRED_KEY
read -r -s GT_API_NEWS_TOKEN
read -r -s GT_RH_USERNAME
read -r -s GT_RH_PASSWORD
read -r -s GT_DG_USERNAME
read -r -s GT_DG_PASSWORD
read -r -s GT_DG_TOTP_SECRET
read -r -s GT_OANDA_ACCOUNT_TYPE
read -r -s GT_OANDA_ACCOUNT
read -r -s GT_OANDA_TOKEN
read -r -s GT_API_TRADIER_TOKEN
read -r -s GT_API_CMC_KEY
read -r -s GT_API_BINANCE_KEY
read -r -s GT_API_BINANCE_SECRET
read -r -s GT_API_FINNHUB_KEY
read -r -s GT_API_IEX_KEY
read -r -s GT_API_SENTIMENTINVESTOR_KEY
read -r -s GT_API_SENTIMENTINVESTOR_TOKEN
