"""OpenBB Terminal SDK."""
# flake8: noqa
# pylint: disable=unused-import,wrong-import-order
# pylint: disable=C0302,W0611,R0902,R0903,C0412,C0301,not-callable
import logging

import openbb_terminal.config_terminal as cfg
from openbb_terminal import helper_funcs as helper  # noqa: F401
from openbb_terminal.config_terminal import theme

from openbb_terminal.core.log.generation.settings_logger import log_all_settings
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin
from openbb_terminal.dashboards.dashboards_controller import DashboardsController
from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401
from openbb_terminal.loggers import setup_logging
from openbb_terminal.portfolio.portfolio_model import PortfolioModel as Portfolio
from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401
from openbb_terminal.reports.reports_controller import ReportController

from openbb_terminal.sdk_core.sdk_helpers import check_suppress_logging
from openbb_terminal.sdk_core import (
    controllers as ctrl,
    models as model,
)

logger = logging.getLogger(__name__)
theme.applyMPLstyle()

SUPPRESS_LOGGING_CLASSES = {
    ReportController: "ReportController",
    DashboardsController: "DashboardsController",
}


class OpenBBSDK:
    """OpenBB SDK Class."""

    def __init__(self, suppress_logging: bool = False):
        self.__suppress_logging = suppress_logging
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not self.__suppress_logging:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging():
        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()

    @property
    def alt(self):
        """OpenBB SDK Alt Submodule

        Submodules:
            `covid`: Covid Module
            `oss`: Oss Module
        """

        return ctrl.AltController()

    @property
    def common(self):
        """OpenBB SDK Common Submodule

        Submodules:
            `qa`: Quantitative Analysis Module
            `ta`: Technical Analysis Module

        Attributes:
            `news`: Get news for a given term and source. [Source: Feedparser]\n
            `news_view`: Plots news for a given term and source. [Source: Feedparser]\n
        """

        return ctrl.CommonController()

    @property
    def crypto(self):
        """OpenBB SDK Crypto Submodule

        Submodules:
            `dd`: Due Diligence Module
            `defi`: DeFi Module
            `disc`: Discovery Module
            `nft`: NFT Module
            `onchain`: OnChain Module
            `ov`: Overview Module
            `tools`: Tools Module

        Attributes:
            `candles`: Plot candle chart from dataframe. [Source: Binance]\n
            `chart`: Load data for Technical Analysis\n
            `find`: Find similar coin by coin name,symbol or id.\n
            `load`: Load crypto currency to get data for\n
        """

        return ctrl.CryptoController()

    @property
    def econometrics(self):
        """OpenBB SDK Econometrics Submodule

        Attributes:
            `bgod`: Calculate test statistics for autocorrelation\n
            `bgod_view`: Show Breusch-Godfrey autocorrelation test\n
            `bols`: The between estimator is an alternative, usually less efficient estimator, can can be used to\n
            `bpag`: Calculate test statistics for heteroscedasticity\n
            `bpag_view`: Show Breusch-Pagan heteroscedasticity test\n
            `clean`: Clean up NaNs from the dataset\n
            `comparison`: Compare regression results between Panel Data regressions.\n
            `dwat`: Calculate test statistics for Durbing Watson autocorrelation\n
            `dwat_view`: Show Durbin-Watson autocorrelation tests\n
            `fdols`: First differencing is an alternative to using fixed effects when there might be correlation.\n
            `fe`: When effects are correlated with the regressors the RE and BE estimators are not consistent.\n
            `get_regression_data`: This function creates a DataFrame with the required regression data as\n
            `granger`: Calculate granger tests\n
            `granger_view`: Show granger tests\n
            `load`: Load custom file into dataframe.\n
            `norm`: The distribution of returns and generate statistics on the relation to the normal curve.\n
            `norm_view`: Determine the normality of a timeseries.\n
            `ols`: Performs an OLS regression on timeseries data. [Source: Statsmodels]\n
            `options`: Obtain columns-dataset combinations from loaded in datasets that can be used in other commands\n
            `options_view`: Plot custom data\n
            `panel`: Based on the regression type, this function decides what regression to run.\n
            `panel_view`: Based on the regression type, this function decides what regression to run.\n
            `pols`: PooledOLS is just plain OLS that understands that various panel data structures.\n
            `re`: The random effects model is virtually identical to the pooled OLS model except that is accounts for the\n
            `root`: Calculate test statistics for unit roots\n
            `root_view`: Determine the normality of a timeseries.\n
        """

        return model.EconometricsRoot()

    @property
    def economy(self):
        """OpenBB SDK Economy Submodule

        Attributes:
            `available_indices`: Get available indices\n
            `bigmac`: Display Big Mac Index for given countries\n
            `bigmac_view`: Display Big Mac Index for given countries\n
            `country_codes`: Get available country codes for Bigmac index\n
            `cpi`: Get Consumer Price Index from Alpha Vantage\n
            `cpi_view`: Display US consumer price index (CPI) from AlphaVantage\n
            `currencies`: Scrape data for global currencies\n
            `events`: Get economic calendar [Source: Investing.com]\n
            `fred_notes`: Get series notes. [Source: FRED]\n
            `fred_series`: Get Series data. [Source: FRED]\n
            `fred_series_view`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
            `fred_yeild_curve`: Gets yield curve data from FRED\n
            `fred_yeild_curve_view`: Display yield curve based on US Treasury rates for a specified date.\n
            `friend_ids`: Get Series IDs. [Source: FRED]\n
            `future`: Get futures data. [Source: Finviz]\n
            `futures`: Scrape data for top commodities\n
            `gdp`: Get annual or quarterly Real GDP for US\n
            `gdp_view`: Display US GDP from AlphaVantage\n
            `gdpc`: Real GDP per Capita for United States\n
            `gdpc_view`: Display US GDP per Capita from AlphaVantage\n
            `get_events_countries`: Get available countries for events command.\n
            `get_ycrv_countries`: Get available countries for ycrv command.\n
            `glbonds`: Scrape data for global bonds\n
            `index`: Get data on selected indices over time [Source: Yahoo Finance]\n
            `index_view`: Load (and show) the selected indices over time [Source: Yahoo Finance]\n
            `indices`: Get the top US indices\n
            `inf`: Get historical Inflation for United States from AlphaVantage\n
            `inf_view`: Display US Inflation from AlphaVantage\n
            `macro`: This functions groups the data queried from the EconDB database [Source: EconDB]\n
            `macro_view`: Show the received macro data about a company [Source: EconDB]\n
            `macro_countries`: This function returns the available countries and respective currencies.\n
            `macro_parameters`: This function returns the available macro parameters with detail.\n
            `overview`: Scrape data for market overview\n
            `performance`: Get group (sectors, industry or country) performance data. [Source: Finviz]\n
            `performance_view`: View group (sectors, industry or country) performance data. [Source: Finviz]\n
            `prefmap`: Opens Finviz map website in a browser. [Source: Finviz]\n
            `rtps`: Get real-time performance sector data\n
            `rtps_view`: Display Real-Time Performance sector. [Source: AlphaVantage]\n
            `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
            `spectrum`: Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]\n
            `spectrum_view`: Display finviz spectrum in system viewer [Source: Finviz]\n
            `spread`: Get spread matrix. [Source: Investing.com]\n
            `spread_view`: Display spread matrix. [Source: Investing.com]\n
            `treasury`: Get U.S. Treasury rates [Source: EconDB]\n
            `treasury_view`: Display U.S. Treasury rates [Source: EconDB]\n
            `treasury_maturities`: Get treasury maturity options [Source: EconDB]\n
            `tyld`: Get historical yield for a given maturity\n
            `tyld_view`: Display historical treasury yield for given maturity\n
            `unemp`: Get historical unemployment for United States\n
            `unemp_view`: Display US unemployment AlphaVantage\n
            `usbonds`: Scrape data for us bonds\n
            `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
            `ycrv`: Get yield curve for specified country. [Source: Investing.com]\n
            `ycrv_view`: Display yield curve for specified country. [Source: Investing.com]\n
        """

        return model.EconomyRoot()

    @property
    def etf(self):
        """OpenBB SDK Etf Submodule

        Submodules:
            `disc`: Discovery Module
            `scr`: Scr Module

        Attributes:
            `by_category`: Return a selection of ETFs based on category filtered by total assets.\n
            `by_category_view`: Display a selection of ETFs based on a category filtered by total assets.\n
            `by_name`: Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]\n
            `by_name_view`: Display ETFs matching search string. [Source: StockAnalysis]\n
            `candle`: Show candle plot of loaded ticker.\n
            `holdings`: Get ETF holdings\n
            `ld`: Return a selection of ETFs based on description filtered by total assets.\n
            `ld_view`: Display a selection of ETFs based on description filtered by total assets.\n
            `ln`: Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
            `ln_view`: Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
            `load`: Load a symbol to perform analysis using the string above as a template.\n
            `news`: Get news for a given term. [Source: NewsAPI]\n
            `news_view`: Prints table showing news for a given term. [Source: NewsAPI]\n
            `overview`: Get overview data for selected etf\n
            `overview_view`: Print etf overview information\n
            `summary`: Return summary description of ETF. [Source: Yahoo Finance]\n
            `summary_view`: Display ETF description summary. [Source: Yahoo Finance]\n
            `symbols`: Gets all etf names and symbols\n
            `weights`: Return sector weightings allocation of ETF. [Source: Yahoo Finance]\n
            `weights_view`: Display sector weightings allocation of ETF. [Source: Yahoo Finance]\n
        """

        return ctrl.EtfController()

    @property
    def forecast(self):
        """OpenBB SDK Forecast Submodule

        Attributes:
            `atr`: Calculate the Average True Range of a variable based on a a specific stock ticker.\n
            `brnn`: Performs Block RNN forecasting\n
            `brnn_view`: Display BRNN forecast\n
            `clean`: Clean up NaNs from the dataset\n
            `combine`: Adds the given column of df2 to df1\n
            `corr`: Returns correlation for a given df\n
            `corr_view`: Plot correlation coefficients for dataset features\n
            `delta`: Calculate the %change of a variable based on a specific column\n
            `desc`: Returns statistics for a given df\n
            `ema`: A moving average provides an indication of the trend of the price movement\n
            `expo`: Performs Probabilistic Exponential Smoothing forecasting\n
            `expo_view`: Display Probabilistic Exponential Smoothing forecast\n
            `linregr`: Perform Linear Regression Forecasting\n
            `linregr_view`: Display Linear Regression Forecasting\n
            `load`: Load custom file into dataframe.\n
            `mom`: A momentum oscillator, which measures the percentage change between the current\n
            `nbeats`: Perform NBEATS Forecasting\n
            `nbeats_view`: Display NBEATS forecast\n
            `nhits`: Performs Nhits forecasting\n
            `nhits_view`: Display Nhits forecast\n
            `plot`: Plot data from a dataset\n
            `regr`: Perform Regression Forecasting\n
            `regr_view`: Display Regression Forecasting\n
            `rename`: Rename a column in a dataframe\n
            `rnn`: Perform RNN forecasting\n
            `rnn_view`: Display RNN forecast\n
            `roc`: A momentum oscillator, which measures the percentage change between the current\n
            `rsi`: A momentum indicator that measures the magnitude of recent price changes to evaluate\n
            `season`: Plot seasonality from a dataset\n
            `signal`: A price signal based on short/long term price.\n
            `sto`: Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing\n
            `tcn`: Perform TCN forecasting\n
            `tcn_view`: Display TCN forecast\n
            `tft`: Performs Temporal Fusion Transformer forecasting\n
            `tft_view`: Display Temporal Fusion Transformer forecast\n
            `theta`: Performs Theta forecasting\n
            `theta_view`: Display Theta forecast\n
            `trans`: Performs Transformer forecasting\n
            `trans_view`: Display Transformer forecast\n
        """

        return model.ForecastRoot()

    @property
    def forex(self):
        """OpenBB SDK Forex Submodule

        Submodules:
            `oanda`: Oanda Module

        Attributes:
            `candle`: Show candle plot for fx data.\n
            `get_currency_list`: Load AV currency codes from a local file.\n
            `hist`: Get historical forex data.\n
            `load`: Load forex for two given symbols.\n
            `quote`: Get current exchange rate quote from alpha vantage.\n
            `quote_view`: Display current forex pair exchange rate.\n
        """

        return ctrl.ForexController()

    @property
    def funds(self):
        """OpenBB SDK Funds Submodule

        Attributes:
            `info_view`: Display fund information.  Finds name from symbol first if name is false\n
            `overview_view`: Displays an overview of the main funds from a country.\n
            `search`: Search investpy for matching funds\n
            `search_view`: Display results of searching for Mutual Funds\n
        """

        return model.FundsRoot()

    @property
    def futures(self):
        """OpenBB SDK Futures Submodule

        Attributes:
            `curve`: Get curve futures [Source: Yahoo Finance]\n
            `curve_view`: Display curve futures [Source: Yahoo Finance]\n
            `historical`: Get historical futures [Source: Yahoo Finance]\n
            `historical_view`: Display historical futures [Source: Yahoo Finance]\n
            `search`: Get search futures [Source: Yahoo Finance]\n
            `search_view`: Display search futures [Source: Yahoo Finance]\n
        """

        return model.FuturesRoot()

    @property
    def keys(self):
        """OpenBB SDK Keys Submodule

        Attributes:
            `av`: Set Alpha Vantage key\n
            `binance`: Set Binance key\n
            `bitquery`: Set Bitquery key\n
            `cmc`: Set Coinmarketcap key\n
            `coinbase`: Set Coinbase key\n
            `coinglass`: Set Coinglass key.\n
            `cpanic`: Set Cpanic key.\n
            `degiro`: Set Degiro key\n
            `eodhd`: Set Eodhd key.\n
            `ethplorer`: Set Ethplorer key.\n
            `finnhub`: Set Finnhub key\n
            `fmp`: Set Financial Modeling Prep key\n
            `fred`: Set FRED key\n
            `get_keys_info`: Get info on available APIs to use in set_keys.\n
            `github`: Set GitHub key.\n
            `glassnode`: Set Glassnode key.\n
            `iex`: Set IEX Cloud key\n
            `messari`: Set Messari key.\n
            `mykeys`: Get currently set API keys.\n
            `news`: Set News key\n
            `oanda`: Set Oanda key\n
            `polygon`: Set Polygon key\n
            `quandl`: Set Quandl key\n
            `reddit`: Set Reddit key\n
            `rh`: Set Robinhood key\n
            `santiment`: Set Santiment key.\n
            `set_keys`: Set API keys in bundle.\n
            `shroom`: Set Shroom key\n
            `si`: Set Sentimentinvestor key.\n
            `smartstake`: Set Smartstake key.\n
            `tokenterminal`: Set Token Terminal key.\n
            `tradier`: Set Tradier key\n
            `twitter`: Set Twitter key\n
            `walert`: Set Walert key\n
        """

        return model.KeysRoot()

    @property
    def portfolio(self):
        """OpenBB SDK Portfolio Submodule

        Submodules:
            `metric`: Metric Module
            `po`: Portfolio Optimization Module

        Attributes:
            `load`: Get PortfolioEngine object\n
            `show`: Get portfolio transactions\n
            `bench`: Load benchmark into portfolio\n
            `distr`: Display daily returns\n
            `distr_view`: Display daily returns\n
            `dret`: Get daily returns\n
            `dret_view`: Display daily returns\n
            `es`: Get portfolio expected shortfall\n
            `holdp`: Get holdings of assets (in percentage)\n
            `holdp_view`: Display holdings of assets (in percentage)\n
            `holdv`: Get holdings of assets (absolute value)\n
            `holdv_view`: Display holdings of assets (absolute value)\n
            `maxdd`: Calculate the drawdown (MDD) of historical series.  Note that the calculation is done\n
            `maxdd_view`: Display maximum drawdown curve\n
            `mret`: Get monthly returns\n
            `mret_view`: Display monthly returns\n
            `om`: Get omega ratio\n
            `om_view`: Display omega ratio\n
            `perf`: Get portfolio performance vs the benchmark\n
            `rbeta`: Get rolling beta using portfolio and benchmark returns\n
            `rbeta_view`: Display rolling beta\n
            `rsharpe`: Get rolling sharpe ratio\n
            `rsharpe_view`: Display rolling sharpe\n
            `rsort`: Get rolling sortino\n
            `rsort_view`: Display rolling sortino\n
            `rvol`: Get rolling volatility\n
            `rvol_view`: Display rolling volatility\n
            `summary`: Get portfolio and benchmark returns summary\n
            `var`: Get portfolio VaR\n
            `yret`: Get yearly returns\n
            `yret_view`: Display yearly returns\n
        """

        return ctrl.PortfolioController()

    @property
    def stocks(self):
        """OpenBB SDK Stocks Submodule

        Submodules:
            `ba`: Behavioral Analysis Module
            `ca`: Comparison Analysis Module
            `dd`: Due Diligence Module
            `disc`: Discovery Module
            `dps`: Darkpool Shorts Module
            `fa`: Fundamental Analysis Module
            `gov`: Government Module
            `ins`: Insiders Module
            `options`: Options Module
            `qa`: Quantitative Analysis Module
            `screener`: Screener Module
            `sia`: Sector Industry Analysis Module
            `ta`: Technical Analysis Module
            `th`: Trading Hours Module

        Attributes:
            `candle`: Show candle plot of loaded ticker.\n
            `load`: Load a symbol to perform analysis using the string above as a template.\n
            `process_candle`: Process DataFrame into candle style plot.\n
            `quote`: Display quote from YahooFinance\n
            `search`: Search selected query for tickers.\n
            `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
        """

        return ctrl.StocksController()


openbb = OpenBBSDK(
    suppress_logging=check_suppress_logging(suppress_dict=SUPPRESS_LOGGING_CLASSES),
)
