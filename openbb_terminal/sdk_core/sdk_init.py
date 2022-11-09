# flake8: noqa pylint: disable=R0402,C0412,unused-import
# noqa: F401

# Alternative
import warnings
import openbb_terminal.alternative.covid.covid_model as alt_covid_model
import openbb_terminal.alternative.covid.covid_view as alt_covid_view
import openbb_terminal.alternative.oss.github_model as alt_oss_github_model
import openbb_terminal.alternative.oss.github_view as alt_oss_github_view
import openbb_terminal.alternative.oss.runa_model as alt_oss_runa_model
import openbb_terminal.alternative.oss.runa_view as alt_oss_runa_view

# Common Behavioural Analysis
from openbb_terminal.common.behavioural_analysis import (
    finbrain_model as stocks_ba_finbrain_model,
    finbrain_view as stocks_ba_finbrain_view,
    google_model as stocks_ba_google_model,
    google_view as stocks_ba_google_view,
    reddit_model as stocks_ba_reddit_model,
    reddit_view as stocks_ba_reddit_view,
    sentimentinvestor_model as stocks_ba_sentimentinvestor_model,
    sentimentinvestor_view as stocks_ba_sentimentinvestor_view,
    stocktwits_model as stocks_ba_stocktwits_model,
    stocktwits_view as stocks_ba_stocktwits_view,
    twitter_model as stocks_ba_twitter_model,
    twitter_view as stocks_ba_twitter_view,
)

# Common
from openbb_terminal.common import (
    common_model,
    newsapi_model as common_newsapi_model,
    newsapi_view as common_newsapi_view,
    feedparser_model as common_feedparser_model,
    feedparser_view as common_feedparser_view,
)

# Common Quantitative Analysis
from openbb_terminal.common.quantitative_analysis import (
    qa_view as common_qa_view,
    qa_model as common_qa_model,
    rolling_model as common_qa_rolling_model,
    rolling_view as common_qa_rolling_view,
)

# Common Technical Analysis
from openbb_terminal.common.technical_analysis import (
    custom_indicators_model as common_ta_custom_indicators_model,
    custom_indicators_view as common_ta_custom_indicators_view,
    momentum_model as common_ta_momentum_model,
    momentum_view as common_ta_momentum_view,
    overlap_view as common_ta_overlap_view,
    overlap_model as common_ta_overlap_model,
    trend_indicators_model as common_ta_trend_indicators_model,
    trend_indicators_view as common_ta_trend_indicators_view,
    volatility_model as common_ta_volatility_model,
    volatility_view as common_ta_volatility_view,
    volume_model as common_ta_volume_model,
    volume_view as common_ta_volume_view,
)

# Cryptocurrency Defi
from openbb_terminal.cryptocurrency.defi import (
    coindix_model as crypto_defi_coindix_model,
    coindix_view as crypto_defi_coindix_view,
    cryptosaurio_model as crypto_defi_cryptosaurio_model,
    cryptosaurio_view as crypto_defi_cryptosaurio_view,
    graph_model as crypto_defi_graph_model,
    graph_view as crypto_defi_graph_view,
    llama_model as crypto_defi_llama_model,
    llama_view as crypto_defi_llama_view,
    smartstake_model as crypto_defi_smartstake_model,
    smartstake_view as crypto_defi_smartstake_view,
    substack_model as crypto_defi_substack_model,
    substack_view as crypto_defi_substack_view,
    terraengineer_model as crypto_defi_terraengineer_model,
    terraengineer_view as crypto_defi_terraengineer_view,
    terramoney_fcd_model as crypto_defi_terramoney_fcd_model,
    terramoney_fcd_view as crypto_defi_terramoney_fcd_view,
)

# Cryptocurrency Discovery
from openbb_terminal.cryptocurrency.discovery import (
    coinmarketcap_model as crypto_disc_coinmarketcap_model,
    coinmarketcap_view as crypto_disc_coinmarketcap_view,
    coinpaprika_model as crypto_disc_coinpaprika_model,
    coinpaprika_view as crypto_disc_coinpaprika_view,
    dappradar_model as crypto_disc_dappradar_model,
    dappradar_view as crypto_disc_dappradar_view,
    pycoingecko_model as crypto_disc_pycoingecko_model,
    pycoingecko_view as crypto_disc_pycoingecko_view,
)


# Cryptocurrency Due Diligence
from openbb_terminal.cryptocurrency.due_diligence import (
    binance_model as crypto_dd_binance_model,
    binance_view as crypto_dd_binance_view,
    coinbase_model as crypto_dd_coinbase_model,
    coinbase_view as crypto_dd_coinbase_view,
    ccxt_model as crypto_dd_ccxt_model,
    coinglass_model as crypto_dd_coinglass_model,
    coinglass_view as crypto_dd_coinglass_view,
    coinpaprika_model as crypto_dd_coinpaprika_model,
    coinpaprika_view as crypto_dd_coinpaprika_view,
    cryptopanic_view as crypto_dd_cryptopanic_view,
    finbrain_crypto_view as crypto_dd_crypto_finbrain_view,
    glassnode_model as crypto_dd_glassnode_model,
    glassnode_view as crypto_dd_glassnode_view,
    messari_model as crypto_dd_messari_model,
    messari_view as crypto_dd_messari_view,
    santiment_model as crypto_dd_santiment_model,
    santiment_view as crypto_dd_santiment_view,
    pycoingecko_model as crypto_dd_pycoingecko_model,
    pycoingecko_view as crypto_dd_pycoingecko_view,
)

# Cryptocurrency NFT
from openbb_terminal.cryptocurrency.nft import (
    opensea_model as crypto_nft_opensea_model,
    opensea_view as crypto_nft_opensea_view,
)
from openbb_terminal.cryptocurrency.nft import (
    nftpricefloor_model as crypto_nft_pricefloor_model,
    nftpricefloor_view as crypto_nft_pricefloor_view,
)

# Cryptocurrency Onchain
from openbb_terminal.cryptocurrency.onchain import (
    bitquery_model as crypto_onchain_bitquery_model,
    bitquery_view as crypto_onchain_bitquery_view,
    blockchain_model as crypto_onchain_blockchain_model,
    blockchain_view as crypto_onchain_blockchain_view,
    ethgasstation_model as crypto_onchain_ethgasstation_model,
    ethgasstation_view as crypto_onchain_ethgasstation_view,
    ethplorer_model as crypto_onchain_ethplorer_model,
    ethplorer_view as crypto_onchain_ethplorer_view,
    whale_alert_model as crypto_onchain_whale_alert_model,
    whale_alert_view as crypto_onchain_whale_alert_view,
)

# Cryptocurrency Overview
from openbb_terminal.cryptocurrency.overview import (
    blockchaincenter_model as crypto_ov_blockchaincenter_model,
    blockchaincenter_view as crypto_ov_blockchaincenter_view,
    coinbase_model as crypto_ov_coinbase_model,
    coinbase_view as crypto_ov_coinbase_view,
    coinpaprika_model as crypto_ov_coinpaprika_model,
    coinpaprika_view as crypto_ov_coinpaprika_view,
    cryptopanic_model as crypto_ov_cryptopanic_model,
    cryptopanic_view as crypto_ov_cryptopanic_view,
    glassnode_model as crypto_ov_glassnode_model,
    glassnode_view as crypto_ov_glassnode_view,
    loanscan_model as crypto_ov_loanscan_model,
    loanscan_view as crypto_ov_loanscan_view,
    pycoingecko_model as crypto_ov_pycoingecko_model,
    pycoingecko_view as crypto_ov_pycoingecko_view,
    rekt_model as crypto_ov_rekt_model,
    rekt_view as crypto_ov_rekt_view,
    withdrawalfees_model as crypto_ov_withdrawalfees_model,
    withdrawalfees_view as crypto_ov_withdrawalfees_view,
)


# Cryptocurrency Tools
from openbb_terminal.cryptocurrency.tools import (
    tools_model as crypto_tools_model,
    tools_view as crypto_tools_view,
)


# Econometrics
from openbb_terminal.econometrics import (
    econometrics_model,
    econometrics_view,
    regression_model as econometrics_regression_model,
    regression_view as econometrics_regression_view,
)


# Economy
from openbb_terminal.economy import (
    econdb_model as economy_econdb_model,
    econdb_view as economy_econdb_view,
    alphavantage_model as economy_alphavantage_model,
    alphavantage_view as economy_alphavantage_view,
    finviz_model as economy_finviz_model,
    finviz_view as economy_finviz_view,
    fred_model as economy_fred_model,
    fred_view as economy_fred_view,
    investingcom_view as economy_investingcom_view,
    investingcom_model as economy_investingcom_model,
    nasdaq_model as economy_nasdaq_model,
    nasdaq_view as economy_nasdaq_view,
    wsj_model as economy_wsj_model,
    yfinance_model as economy_yfinance_model,
    yfinance_view as economy_yfinance_view,
)


# ETF's
from openbb_terminal.etf import (
    financedatabase_model as etf_financedatabase_model,
    financedatabase_view as etf_financedatabase_view,
    stockanalysis_model as etf_stockanalysis_model,
    stockanalysis_view as etf_stockanalysis_view,
    yfinance_model as etf_yfinance_model,
    yfinance_view as etf_yfinance_view,
)
import openbb_terminal.etf.discovery.wsj_model as etf_disc_wsj_model
import openbb_terminal.etf.discovery.wsj_view as etf_disc_wsj_view
import openbb_terminal.etf.screener.screener_model as etf_scr_model
import openbb_terminal.etf.screener.screener_view as etf_scr_view


# Forex
from openbb_terminal.forex import (
    av_model as forex_av_model,
    av_view as forex_av_view,
    fxempire_model as forex_fxempire_model,
    fxempire_view as forex_fxempire_view,
)
import openbb_terminal.forex.oanda.oanda_model as forex_oanda_model
import openbb_terminal.forex.oanda.oanda_view as forex_oanda_view


# Mutual Funds
from openbb_terminal.mutual_funds import (
    investpy_model as mutual_funds_investpy_model,
    investpy_view as mutual_funds_investpy_view,
)

# Portfolio
from openbb_terminal.portfolio import (
    portfolio_model,
    portfolio_view,
)
from openbb_terminal.portfolio.portfolio_optimization import (
    excel_model as portfolio_optimization_excel_model,
    optimizer_model as portfolio_optimization_optimizer_model,
    optimizer_view as portfolio_optimization_optimizer_view,
)

# stocks.bt.emacross:
#     import openbb_terminal.stocks.backtesting.bt_model.emacross_strategy
#     import openbb_terminal.stocks.backtesting.bt_view.display_emacross
#
# stocks.bt.ema:
#     import openbb_terminal.stocks.backtesting.bt_model.ema_strategy
#     import openbb_terminal.stocks.backtesting.bt_view.display_simple_ema
#
# stocks.bt.rsi:
#     import openbb_terminal.stocks.backtesting.bt_model.rsi_strategy
#     import openbb_terminal.stocks.backtesting.bt_view.display_rsi_strategy
#


# Stocks -Behavioral Analysis
from openbb_terminal.stocks.behavioural_analysis import (
    finnhub_model as stocks_ba_finnhub_model,
    finnhub_view as stocks_ba_finnhub_view,
)


# Stocks - Comparison Analysis
from openbb_terminal.stocks.comparison_analysis import (
    finbrain_model as stocks_ca_finbrain_model,
    finbrain_view as stocks_ca_finbrain_view,
    finnhub_model as stocks_ca_finnhub_model,
    finviz_compare_model as stocks_ca_finviz_compare_model,
    marketwatch_model as stocks_ca_marketwatch_model,
    marketwatch_view as stocks_ca_marketwatch_view,
    polygon_model as stocks_ca_polygon_model,
    yahoo_finance_model as stocks_ca_yahoo_finance_model,
    yahoo_finance_view as stocks_ca_yahoo_finance_view,
)


# Stocks - Dark Pool Shorts
from openbb_terminal.stocks.dark_pool_shorts import (
    finra_model as stocks_dps_finra_model,
    finra_view as stocks_dps_finra_view,
    ibkr_model as stocks_dps_ibkr_model,
    nyse_model as stocks_dps_nyse_model,
    nyse_view as stocks_dps_nyse_view,
    quandl_model as stocks_dps_quandl_model,
    quandl_view as stocks_dps_quandl_view,
    sec_model as stocks_dps_sec_model,
    sec_view as stocks_dps_sec_view,
    shortinterest_model as stocks_dps_shortinterest_model,
    stockgrid_model as stocks_dps_stockgrid_model,
    stockgrid_view as stocks_dps_stockgrid_view,
    stocksera_model as stocks_dps_stocksera_model,
    stocksera_view as stocks_dps_stocksera_view,
    yahoofinance_model as stocks_dps_yahoofinance_model,
)


# Stocks - Fundamental Discovery
from openbb_terminal.stocks.discovery import (
    ark_model as stocks_disc_ark_model,
    finnhub_model as stocks_disc_finnhub_model,
    nasdaq_model as stocks_disc_nasdaq_model,
    seeking_alpha_model as stocks_disc_seeking_alpha_model,
    shortinterest_model as stocks_disc_shortinterest_model,
    yahoofinance_model as stocks_disc_yahoofinance_model,
)


# Stocks - Due Diligence
from openbb_terminal.stocks.due_diligence import (
    ark_model as stocks_dd_ark_model,
    business_insider_model as stocks_dd_business_insider_model,
    business_insider_view as stocks_dd_business_insider_view,
    csimarket_model as stocks_dd_csimarket_model,
    finnhub_model as stocks_dd_finnhub_model,
    finnhub_view as stocks_dd_finnhub_view,
    finviz_model as stocks_dd_finviz_model,
    fmp_model as stocks_dd_fmp_model,
    marketwatch_model as stocks_dd_marketwatch_model,
    marketwatch_view as stocks_dd_marketwatch_view,
)

# Stocks - Fundamental Analysis
from openbb_terminal.stocks.fundamental_analysis import (
    av_model as stocks_fa_av_model,
    av_view as stocks_fa_av_view,
    business_insider_model as stocks_fa_business_insider_model,
    dcf_model as stocks_fa_dcf_model,
    eclect_us_model as stocks_fa_eclect_us_model,
    fmp_model as stocks_fa_fmp_model,
    finviz_model as stocks_fa_finviz_model,
    polygon_model as stocks_fa_polygon_model,
    polygon_view as stocks_fa_polygon_view,
    yahoo_finance_model as stocks_fa_yahoo_finance_model,
    yahoo_finance_view as stocks_fa_yahoo_finance_view,
)


# Government
from openbb_terminal.stocks.government import (
    quiverquant_model as stocks_gov_quiverquant_model,
    quiverquant_view as stocks_gov_quiverquant_view,
)


# Stocks - Insider Trading
from openbb_terminal.stocks.insider import (
    businessinsider_model as stocks_insider_businessinsider_model,
    businessinsider_view as stocks_insider_businessinsider_view,
    finviz_model as stocks_insider_finviz_model,
    finviz_view as stocks_insider_finviz_view,
    openinsider_model as stocks_insider_openinsider_model,
    openinsider_view as stocks_insider_openinsider_view,
)


# Stocks - Options
from openbb_terminal.stocks.options import (
    alphaquery_model as stocks_options_alphaquery_model,
    alphaquery_view as stocks_options_alphaquery_view,
    barchart_model as stocks_options_barchart_model,
    barchart_view as stocks_options_barchart_view,
    chartexchange_model as stocks_options_chartexchange_model,
    chartexchange_view as stocks_options_chartexchange_view,
    fdscanner_model as stocks_options_fdscanner_model,
    fdscanner_view as stocks_options_fdscanner_view,
    nasdaq_model as stocks_options_nasdaq_model,
    nasdaq_view as stocks_options_nasdaq_view,
    tradier_model as stocks_options_tradier_model,
    tradier_view as stocks_options_tradier_view,
    yfinance_model as stocks_options_yfinance_model,
    yfinance_view as stocks_options_yfinance_view,
)
import openbb_terminal.stocks.options.hedge.hedge_model as stocks_options_hedge_model
import openbb_terminal.stocks.options.hedge.hedge_view as stocks_options_hedge_view
from openbb_terminal.stocks.options.screen import (
    syncretism_model as stocks_options_screen_syncretism_model,
    syncretism_view as stocks_options_screen_syncretism_view,
)


# Stocks - Quantitative Analysis
import openbb_terminal.stocks.quantitative_analysis.factors_model as stocks_qa_factors_model
import openbb_terminal.stocks.quantitative_analysis.factors_view as stocks_qa_factors_view


# Stocks - Screener
from openbb_terminal.stocks.screener import (
    finviz_model as stocks_screener_finviz_model,
    finviz_view as stocks_screener_finviz_view,
    yahoofinance_model as stocks_screener_yahoofinance_model,
    yahoofinance_view as stocks_screener_yahoofinance_view,
)


# Stocks - Sector Industry Analysis
from openbb_terminal.stocks.sector_industry_analysis import (
    financedatabase_model as stocks_sia_financedatabase_model,
    financedatabase_view as stocks_sia_financedatabase_view,
    stockanalysis_model as stocks_sia_stockanalysis_model,
    stockanalysis_view as stocks_sia_stockanalysis_view,
)


# Stocks - Technical Analysis
from openbb_terminal.stocks.technical_analysis import (
    finbrain_model as stocks_ta_finbrain_model,
    finbrain_view as stocks_ta_finbrain_view,
    finviz_model as stocks_ta_finviz_model,
    finviz_view as stocks_ta_finviz_view,
    tradingview_model as stocks_ta_tradingview_model,
    tradingview_view as stocks_ta_tradingview_view,
)


# Stocks - Trading Hours
from openbb_terminal.stocks.tradinghours import (
    bursa_model as stocks_th_bursa_model,
    bursa_view as stocks_th_bursa_view,
)


# Futures
from openbb_terminal.futures import (
    yfinance_model as futures_yfinance_model,
    yfinance_view as futures_yfinance_view,
)


# Stocks Helpers
from openbb_terminal.stocks import (
    stocks_helper,
    stocks_views,
    cboe_model as stocks_cboe_model,
    cboe_view as stocks_cboe_view,
)

# Crypto Helpers
import openbb_terminal.cryptocurrency.cryptocurrency_helpers as crypto_helpers


# Forex Helpers
import openbb_terminal.forex.forex_helper as forex_helpers


# Keys
import openbb_terminal.keys_model as keys_model


# Forecast Extras
try:
    import darts  # pyright: reportMissingImports=false

    # If you just import darts this will pass during pip install, this creates
    # Failures later on, also importing utils ensures that darts is installed correctly
    from darts import utils

    forecasting = True
    from openbb_terminal.forecast import (
        forecast_model,
        forecast_view,
        expo_model as forecast_expo_model,
        expo_view as forecast_expo_view,
        theta_model as forecast_theta_model,
        theta_view as forecast_theta_view,
        linregr_model as forecast_linregr_model,
        linregr_view as forecast_linregr_view,
        regr_model as forecast_regr_model,
        regr_view as forecast_regr_view,
        rnn_model as forecast_rnn_model,
        rnn_view as forecast_rnn_view,
        brnn_model as forecast_brnn_model,
        brnn_view as forecast_brnn_view,
        nbeats_model as forecast_nbeats_model,
        nbeats_view as forecast_nbeats_view,
        tcn_model as forecast_tcn_model,
        tcn_view as forecast_tcn_view,
        trans_model as forecast_trans_model,
        trans_view as forecast_trans_view,
        tft_model as forecast_tft_model,
        tft_view as forecast_tft_view,
        nhits_model as forecast_nhits_model,
        nhits_view as forecast_nhits_view,
    )
except ImportError:
    forecasting = False
