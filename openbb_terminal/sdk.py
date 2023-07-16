"""OpenBB Terminal SDK."""


# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #


# flake8: noqa


# pylint: disable=unused-import,wrong-import-order


# pylint: disable=C0302,W0611,R0902,R0903,C0412,C0301,not-callable


import logging


import openbb_terminal.config_terminal as cfg


from openbb_terminal import helper_funcs as helper  # noqa: F401


from openbb_terminal.core.plots.plotly_helper import theme  # noqa: F401


from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin


from openbb_terminal.dashboards.dashboards_controller import DashboardsController


from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401


from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401


from openbb_terminal.reports.reports_controller import ReportController


import openbb_terminal.core.sdk.sdk_init as lib


from openbb_terminal.core.sdk import (
    controllers as ctrl,
    models as model,
)


from openbb_terminal.core.session.current_system import get_current_system


from openbb_terminal.core.session.current_user import is_local


from openbb_terminal.terminal_helper import is_auth_enabled


cfg.setup_config_terminal(is_sdk=True)


logger = logging.getLogger(__name__)


cfg.theme.applyMPLstyle()


class OpenBBSDK:
    """OpenBB SDK Class.

    Attributes:
        `login`: Login and load user info.\n
        `logout`: Logout and clear session.\n
        `news`: Access news from either feedparser or biztoc for a given term or from specified sources\n
        `whoami`: Display user info.\n
    """

    __version__ = get_current_system().VERSION

    def __init__(self):
        SDKLogger()
        self.login = lib.sdk_session.login
        self.logout = lib.sdk_session.logout
        self.news = lib.common_news_sdk_helper.news
        self.whoami = lib.sdk_session.whoami
        SDKLogger._try_to_login(self)

    @property
    def alt(self):
        """Alternative Submodule

        Submodules:
            `covid`: Covid Module
            `oss`: Oss Module
            `realestate`: Realestate Module

        Attributes:
            `hn`: Get top stories from HackerNews.\n
            `hn_chart`: View top stories from HackerNews.\n
        """

        return ctrl.AltController()

    @property
    def crypto(self):
        """Cryptocurrency Submodule

        Submodules:
            `dd`: Due Diligence Module
            `defi`: DeFi Module
            `disc`: Discovery Module
            `nft`: NFT Module
            `onchain`: OnChain Module
            `ov`: Overview Module
            `tools`: Tools Module

        Attributes:
            `candle`: Plot candle chart from dataframe. [Source: Binance]\n
            `chart`: Load data for Technical Analysis\n
            `find`: Find similar coin by coin name,symbol or id.\n
            `load`: Load crypto currency to get data for\n
            `price`: Returns price and confidence interval from pyth live feed. [Source: Pyth]\n
        """

        return ctrl.CryptoController()

    @property
    def econometrics(self):
        """Econometrics Submodule

        Attributes:
            `bgod`: Calculate test statistics for autocorrelation\n
            `bgod_chart`: Show Breusch-Godfrey autocorrelation test\n
            `bols`: The between estimator is an alternative, usually less efficient estimator, can can be used to\n
            `bpag`: Calculate test statistics for heteroscedasticity\n
            `bpag_chart`: Show Breusch-Pagan heteroscedasticity test\n
            `clean`: Clean up NaNs from the dataset\n
            `coint`: Calculate cointegration tests between variable number of input series\n
            `coint_chart`: Estimates long-run and short-run cointegration relationship for series y and x and apply\n
            `comparison`: Compare regression results between Panel Data regressions.\n
            `dwat`: Calculate test statistics for Durbin Watson autocorrelation\n
            `dwat_chart`: Show Durbin-Watson autocorrelation tests\n
            `fdols`: First differencing is an alternative to using fixed effects when there might be correlation.\n
            `fe`: When effects are correlated with the regressors the RE and BE estimators are not consistent.\n
            `garch`: Calculates volatility forecasts based on GARCH.\n
            `garch_chart`: Plots the volatility forecasts based on GARCH\n
            `get_regression_data`: This function creates a DataFrame with the required regression data as\n
            `granger`: Calculate granger tests\n
            `granger_chart`: Show granger tests\n
            `load`: Load custom file into dataframe.\n
            `norm`: The distribution of returns and generate statistics on the relation to the normal curve.\n
            `norm_chart`: Determine the normality of a timeseries.\n
            `ols`: Performs an OLS regression on timeseries data. [Source: Statsmodels]\n
            `options`: Obtain columns-dataset combinations from loaded in datasets that can be used in other commands\n
            `options_chart`: Plot custom data\n
            `panel`: Based on the regression type, this function decides what regression to run.\n
            `panel_chart`: Based on the regression type, this function decides what regression to run.\n
            `pols`: PooledOLS is just plain OLS that understands that various panel data structures.\n
            `re`: The random effects model is virtually identical to the pooled OLS model except that is accounts for the\n
            `root`: Calculate test statistics for unit roots\n
            `root_chart`: Determine the normality of a timeseries.\n
            `vif`: Calculates VIF (variance inflation factor), which tests collinearity.\n
        """

        return model.EconometricsRoot()

    @property
    def economy(self):
        """Economy Submodule

        Attributes:
            `available_indices`: Get available indices\n
            `balance`: General government deficit is defined as the balance of income and expenditure of government,\n
            `balance_chart`: General government balance is defined as the balance of income and expenditure of government,\n
            `bigmac`: Display Big Mac Index for given countries\n
            `bigmac_chart`: Display Big Mac Index for given countries\n
            `ccpi`: Inflation measured by consumer price index (CPI) is defined as the change in the prices\n
            `ccpi_chart`: Inflation measured by consumer price index (CPI) is defined as the change in the prices\n
            `country_codes`: Get available country codes for Bigmac index\n
            `cpi`: Obtain CPI data from FRED. [Source: FRED]\n
            `cpi_chart`: Inflation measured by consumer price index (CPI) is defined as the change in\n
            `currencies`: Scrape data for global currencies\n
            `debt`: General government debt-to-GDP ratio measures the gross debt of the general\n
            `debt_chart`: General government debt-to-GDP ratio measures the gross debt of the general\n
            `events`: Get economic calendar for countries between specified dates\n
            `fgdp`: Real gross domestic product (GDP) is GDP given in constant prices and\n
            `fgdp_chart`: Real gross domestic product (GDP) is GDP given in constant prices and\n
            `fred`: Get Series data. [Source: FRED]\n
            `fred_chart`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
            `fred_notes`: Get series notes. [Source: FRED]\n
            `future`: Get futures data. [Source: Finviz]\n
            `futures`: Get futures data.\n
            `gdp`: Gross domestic product (GDP) is the standard measure of the value added created\n
            `gdp_chart`: Gross domestic product (GDP) is the standard measure of the value added created\n
            `get_groups`: Get group available\n
            `glbonds`: Scrape data for global bonds\n
            `index`: Get data on selected indices over time [Source: Yahoo Finance]\n
            `index_chart`: Load (and show) the selected indices over time [Source: Yahoo Finance]\n
            `indices`: Get the top US indices\n
            `macro`: This functions groups the data queried from the EconDB database [Source: EconDB]\n
            `macro_chart`: Show the received macro data about a company [Source: EconDB]\n
            `macro_countries`: This function returns the available countries and respective currencies.\n
            `macro_parameters`: This function returns the available macro parameters with detail.\n
            `overview`: Scrape data for market overview\n
            `perfmap`: Opens Finviz map website in a browser. [Source: Finviz]\n
            `performance`: Get group (sectors, industry or country) performance data. [Source: Finviz]\n
            `revenue`: Governments collect revenues mainly for two purposes: to finance the goods\n
            `revenue_chart`: Governments collect revenues mainly for two purposes: to finance the goods\n
            `rgdp`: Gross domestic product (GDP) is the standard measure of the value added\n
            `rgdp_chart`: Gross domestic product (GDP) is the standard measure of the value added\n
            `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
            `spending`: General government spending provides an indication of the size\n
            `spending_chart`: General government spending provides an indication of the size\n
            `treasury`: Get treasury rates from Federal Reserve\n
            `treasury_chart`: Display U.S. Treasury rates [Source: EconDB]\n
            `trust`: Trust in government refers to the share of people who report having confidence in\n
            `trust_chart`: Trust in government refers to the share of people who report having confidence in\n
            `usbonds`: Scrape data for us bonds\n
            `usdli`: The USD Liquidity Index is defined as: [WALCL - WLRRAL - WDTGAL]. It is expressed in billions of USD.\n
            `usdli_chart`: Display US Dollar Liquidity\n
            `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
        """

        return model.EconomyRoot()

    @property
    def etf(self):
        """Etf Submodule

        Submodules:
            `disc`: Discovery Module

        Attributes:
            `candle`: Show candle plot of loaded ticker.\n
            `compare`: Compare selected ETFs\n
            `etf_by_category`: Return a selection of ETFs based on category filtered by total assets.\n
            `etf_by_name`: Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]\n
            `holdings`: Get ETF holdings\n
            `ld`: Return a selection of ETFs based on description filtered by total assets.\n
            `ln`: Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
            `load`: Load a symbol to perform analysis using the string above as a template.\n
            `news`: Get news for a given term. [Source: NewsAPI]\n
            `news_chart`: Prints table showing news for a given term. [Source: NewsAPI]\n
            `overview`: Get overview data for selected etf\n
            `symbols`: Gets all etf names and symbols\n
            `weights`: Return sector weightings allocation of ETF. [Source: FinancialModelingPrep]\n
        """

        return ctrl.EtfController()

    @property
    def fixedincome(self):
        """Fixedincome Submodule

        Attributes:
            `ameribor`: Obtain data for American Interbank Offered Rate (AMERIBOR)\n
            `cp`: Obtain Commercial Paper data\n
            `dwpcr`: Obtain data for the Discount Window Primary Credit Rate.\n
            `ecb`: Obtain data for ECB interest rates.\n
            `ecbycrv`: Gets euro area yield curve data from ECB.\n
            `estr`: Obtain data for Euro Short-Term Rate (ESTR)\n
            `fed`: Obtain data for Effective Federal Funds Rate.\n
            `ffrmc`: Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate\n
            `hqm`: The HQM yield curve represents the high quality corporate bond market, i.e.,\n
            `icebofa`: Get data for ICE BofA US Corporate Bond Indices.\n
            `icespread`: Get data for ICE BofA US Corporate Bond Spreads\n
            `iorb`: Obtain data for Interest Rate on Reserve Balances.\n
            `moody`: Get data for Moody Corporate Bond Index\n
            `projection`: Obtain data for the Federal Reserve's projection of the federal funds rate.\n
            `sofr`: Obtain data for Secured Overnight Financing Rate (SOFR)\n
            `sonia`: Obtain data for Sterling Overnight Index Average (SONIA)\n
            `spot`: The spot rate for any maturity is the yield on a bond that provides\n
            `tbffr`: Get data for Selected Treasury Bill Minus Federal Funds Rate.\n
            `tmc`: Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.\n
            `treasury`: Gets interest rates data from selected countries (3 month and 10 year)\n
            `usrates`: Plot various treasury rates from the United States\n
            `ycrv`: Gets yield curve data from FRED.\n
            `ycrv_chart`: Display yield curve based on US Treasury rates for a specified date.\n
        """

        return model.FixedincomeRoot()

    @property
    def forecast(self):
        """Forecasting Submodule

        Attributes:
            `anom`: Get Quantile Anomaly Detection Data\n
            `anom_chart`: Display Quantile Anomaly Detection\n
            `atr`: Calculate the Average True Range of a variable based on a a specific stock ticker.\n
            `autoarima`: Performs Automatic ARIMA forecasting\n
            `autoarima_chart`: Display Automatic ARIMA model.\n
            `autoces`: Performs Automatic Complex Exponential Smoothing forecasting\n
            `autoces_chart`: Display Automatic Complex Exponential Smoothing Model\n
            `autoets`: Performs Automatic ETS forecasting\n
            `autoets_chart`: Display Automatic ETS (Error, Trend, Sesonality) Model\n
            `autoselect`: Performs Automatic Statistical forecasting\n
            `autoselect_chart`: Display Automatic Statistical Forecasting Model\n
            `brnn`: Performs Block RNN forecasting\n
            `brnn_chart`: Display BRNN forecast\n
            `clean`: Clean up NaNs from the dataset\n
            `combine`: Adds the given column of df2 to df1\n
            `corr`: Returns correlation for a given df\n
            `corr_chart`: Plot correlation coefficients for dataset features\n
            `delete`: Delete a column from a dataframe\n
            `delta`: Calculate the %change of a variable based on a specific column\n
            `desc`: Returns statistics for a given df\n
            `desc_chart`: Show descriptive statistics for a dataframe\n
            `ema`: A moving average provides an indication of the trend of the price movement\n
            `expo`: Performs Probabilistic Exponential Smoothing forecasting\n
            `expo_chart`: Display Probabilistic Exponential Smoothing forecast\n
            `export`: Export a dataframe to a file\n
            `linregr`: Perform Linear Regression Forecasting\n
            `linregr_chart`: Display Linear Regression Forecasting\n
            `load`: Load custom file into dataframe.\n
            `mom`: A momentum oscillator, which measures the percentage change between the current\n
            `mstl`: Performs MSTL forecasting\n
            `mstl_chart`: Display MSTL Model\n
            `nbeats`: Perform NBEATS Forecasting\n
            `nbeats_chart`: Display NBEATS forecast\n
            `nhits`: Performs Nhits forecasting\n
            `nhits_chart`: Display Nhits forecast\n
            `plot`: Plot data from a dataset\n
            `plot_chart`: Plot data from a dataset\n
            `regr`: Perform Regression Forecasting\n
            `regr_chart`: Display Regression Forecasting\n
            `rename`: Rename a column in a dataframe\n
            `rnn`: Perform RNN forecasting\n
            `rnn_chart`: Display RNN forecast\n
            `roc`: A momentum oscillator, which measures the percentage change between the current\n
            `rsi`: A momentum indicator that measures the magnitude of recent price changes to evaluate\n
            `rwd`: Performs Random Walk with Drift forecasting\n
            `rwd_chart`: Display Random Walk with Drift Model\n
            `season_chart`: Plot seasonality from a dataset\n
            `seasonalnaive`: Performs Seasonal Naive forecasting\n
            `seasonalnaive_chart`: Display SeasonalNaive Model\n
            `show`: Show a dataframe in a table\n
            `signal`: A price signal based on short/long term price.\n
            `sto`: Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing\n
            `tcn`: Perform TCN forecasting\n
            `tcn_chart`: Display TCN forecast\n
            `tft`: Performs Temporal Fusion Transformer forecasting\n
            `tft_chart`: Display Temporal Fusion Transformer forecast\n
            `theta`: Performs Theta forecasting\n
            `theta_chart`: Display Theta forecast\n
            `trans`: Performs Transformer forecasting\n
            `trans_chart`: Display Transformer forecast\n
        """

        return model.ForecastRoot()

    @property
    def forex(self):
        """Forex Submodule

        Submodules:
            `oanda`: Oanda Module

        Attributes:
            `candle`: Show candle plot for fx data.\n
            `fwd`: Gets forward rates from fxempire\n
            `get_currency_list`: Load AV currency codes from a local file.\n
            `load`: Load forex for two given symbols.\n
            `quote`: Get forex quote.\n
        """

        return ctrl.ForexController()

    @property
    def funds(self):
        """Mutual Funds Submodule

        Attributes:
            `carbon`: Search mstarpy for carbon metrics\n
            `exclusion`: Search mstarpy exclusion policy in esgData\n
            `historical`: Get historical fund, category, index price\n
            `historical_chart`: Display historical fund, category, index price\n
            `holdings`: Search mstarpy for holdings\n
            `load`: Search mstarpy for matching funds\n
            `search`: Search mstarpy for matching funds\n
            `sector`: Get fund, category, index sector breakdown\n
            `sector_chart`: Display fund, category, index sector breakdown\n
        """

        return model.FundsRoot()

    @property
    def futures(self):
        """Futures Submodule

        Attributes:
            `curve`: Get curve futures [Source: Yahoo Finance]\n
            `curve_chart`: Display curve futures [Source: Yahoo Finance]\n
            `historical`: Get historical futures data\n
            `historical_chart`: Display historical futures [Source: Yahoo Finance]\n
            `search`: Get search futures [Source: Yahoo Finance]\n
        """

        return model.FuturesRoot()

    @property
    def keys(self):
        """Keys Submodule

        Attributes:
            `av`: Set Alpha Vantage key\n
            `binance`: Set Binance key\n
            `bitquery`: Set Bitquery key\n
            `biztoc`: Set BizToc key\n
            `cmc`: Set Coinmarketcap key\n
            `coinbase`: Set Coinbase key\n
            `coinglass`: Set Coinglass key.\n
            `cpanic`: Set Cpanic key.\n
            `databento`: Set DataBento key\n
            `degiro`: Set Degiro key\n
            `eodhd`: Set Eodhd key.\n
            `ethplorer`: Set Ethplorer key.\n
            `finnhub`: Set Finnhub key\n
            `fmp`: Set Financial Modeling Prep key\n
            `fred`: Set FRED key\n
            `get_keys_info`: Get info on available APIs to use in set_keys.\n
            `github`: Set GitHub key.\n
            `glassnode`: Set Glassnode key.\n
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
            `smartstake`: Set Smartstake key.\n
            `stocksera`: Set Stocksera key.\n
            `tokenterminal`: Set Token Terminal key.\n
            `tradier`: Set Tradier key\n
            `twitter`: Set Twitter key\n
            `ultima`: Set Ultima Insights key\n
            `walert`: Set Walert key\n
        """

        return model.KeysRoot()

    @property
    def portfolio(self):
        """Portfolio Submodule

        Submodules:
            `alloc`: Alloc Module
            `metric`: Metric Module
            `po`: Portfolio Optimization Module

        Attributes:
            `bench`: Load benchmark into portfolio\n
            `distr`: Display daily returns\n
            `distr_chart`: Display daily returns\n
            `dret`: Get daily returns\n
            `dret_chart`: Display daily returns\n
            `es`: Get portfolio expected shortfall\n
            `holdp`: Get holdings of assets (in percentage)\n
            `holdp_chart`: Display holdings of assets (in percentage)\n
            `holdv`: Get holdings of assets (absolute value)\n
            `holdv_chart`: Display holdings of assets (absolute value)\n
            `load`: Get PortfolioEngine object\n
            `maxdd`: Calculate the drawdown (MDD) of historical series.  Note that the calculation is done\n
            `maxdd_chart`: Display maximum drawdown curve\n
            `mret`: Get monthly returns\n
            `mret_chart`: Display monthly returns\n
            `om`: Get omega ratio\n
            `om_chart`: Display omega ratio\n
            `perf`: Get portfolio performance vs the benchmark\n
            `rbeta`: Get rolling beta using portfolio and benchmark returns\n
            `rbeta_chart`: Display rolling beta\n
            `rsharpe`: Get rolling sharpe ratio\n
            `rsharpe_chart`: Display rolling sharpe\n
            `rsort`: Get rolling sortino\n
            `rsort_chart`: Display rolling sortino\n
            `rvol`: Get rolling volatility\n
            `rvol_chart`: Display rolling volatility\n
            `show`: Get portfolio transactions\n
            `summary`: Get portfolio and benchmark returns summary\n
            `var`: Get portfolio VaR\n
            `yret`: Get yearly returns\n
            `yret_chart`: Display yearly returns\n
        """

        return ctrl.PortfolioController()

    @property
    def qa(self):
        """Quantitative Analysis Submodule

        Attributes:
            `acf`: Plots Auto and Partial Auto Correlation of returns and change in returns\n
            `bw`: Plots box and whisker plots\n
            `calculate_adjusted_var`: Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)\n
            `cdf`: Plots Cumulative Distribution Function\n
            `cusum`: Plots Cumulative sum algorithm (CUSUM) to detect abrupt changes in data\n
            `decompose`: Perform seasonal decomposition\n
            `es`: Gets Expected Shortfall for specified stock dataframe.\n
            `es_chart`: Prints table showing expected shortfall.\n
            `hist`: Plots histogram of data\n
            `kurtosis`: Kurtosis Indicator\n
            `kurtosis_chart`: Plots rolling kurtosis\n
            `line`: Display line plot of data\n
            `normality`: Look at the distribution of returns and generate statistics on the relation to the normal curve.\n
            `normality_chart`: Prints table showing normality statistics\n
            `omega`: Get the omega series\n
            `omega_chart`: Plots the omega ratio\n
            `qqplot`: Plots QQ plot for data against normal quantiles\n
            `quantile`: Overlay Median & Quantile\n
            `quantile_chart`: Plots rolling quantile\n
            `rolling`: Return rolling mean and standard deviation\n
            `rolling_chart`: Plots mean std deviation\n
            `sharpe`: Calculates the sharpe ratio\n
            `sharpe_chart`: Plots Calculated the sharpe ratio\n
            `skew`: Skewness Indicator\n
            `skew_chart`: Plots rolling skew\n
            `sortino`: Calculates the sortino ratio\n
            `sortino_chart`: Plots the sortino ratio\n
            `spread`: Standard Deviation and Variance\n
            `spread_chart`: Plots rolling spread\n
            `summary`: Print summary statistics\n
            `summary_chart`: Prints table showing summary statistics\n
            `unitroot`: Calculate test statistics for unit roots\n
            `unitroot_chart`: Prints table showing unit root test calculations\n
            `var`: Gets value at risk for specified stock dataframe.\n
            `var_chart`: Prints table showing VaR of dataframe.\n
        """

        return model.QaRoot()

    @property
    def stocks(self):
        """Stocks Submodule

        Submodules:
            `ba`: Behavioral Analysis Module
            `ca`: Comparison Analysis Module
            `disc`: Discovery Module
            `dps`: Darkpool Shorts Module
            `fa`: Fundamental Analysis Module
            `gov`: Government Module
            `ins`: Insiders Module
            `options`: Options Module
            `qa`: Quantitative Analysis Module
            `screener`: Screener Module
            `ta`: Technical Analysis Module
            `th`: Trading Hours Module

        Attributes:
            `candle`: Show candle plot of loaded ticker.\n
            `load`: Load a symbol to perform analysis using the string above as a template.\n
            `news`: Get news for a given term and source. [Source: Ultima Insights News Monitor]\n
            `process_candle`: Process DataFrame into candle style plot.\n
            `quote`: Gets ticker quote from FMP\n
            `quote_chart`: Financial Modeling Prep ticker(s) quote.\n
            `search`: Search selected query for tickers.\n
            `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
        """

        return ctrl.StocksController()

    @property
    def ta(self):
        """Technical Analysis Submodule

        Attributes:
            `ad`: Calculate AD technical indicator\n
            `ad_chart`: Plots AD technical indicator\n
            `adosc`: Calculate AD oscillator technical indicator\n
            `adosc_chart`: Plots AD Osc Indicator\n
            `adx`: ADX technical indicator\n
            `adx_chart`: Plots ADX indicator\n
            `aroon`: Aroon technical indicator\n
            `aroon_chart`: Plots Aroon indicator\n
            `atr`: Average True Range\n
            `atr_chart`: Plots ATR\n
            `bbands`: Calculate Bollinger Bands\n
            `bbands_chart`: Plots bollinger bands\n
            `cci`: Commodity channel index\n
            `cci_chart`: Plots CCI Indicator\n
            `cg`: Center of gravity\n
            `cg_chart`: Plots center of gravity Indicator\n
            `clenow`: Gets the Clenow Volatility Adjusted Momentum.  this is defined as the regression coefficient on log prices\n
            `clenow_chart`: Prints table and plots clenow momentum\n
            `cones`: Returns a DataFrame of realized volatility quantiles.\n
            `cones_chart`: Plots the realized volatility quantiles for the loaded ticker.\n
            `demark`: Get the integer value for demark sequential indicator\n
            `demark_chart`: Plot demark sequential indicator\n
            `donchian`: Calculate Donchian Channels\n
            `donchian_chart`: Plots donchian channels\n
            `ema`: Gets exponential moving average (EMA) for stock\n
            `fib`: Calculate Fibonacci levels\n
            `fib_chart`: Plots Calculated fibonacci retracement levels\n
            `fisher`: Fisher Transform\n
            `fisher_chart`: Plots Fisher Indicator\n
            `hma`: Gets hull moving average (HMA) for stock\n
            `kc`: Keltner Channels\n
            `kc_chart`: Plots Keltner Channels Indicator\n
            `ma`: Plots MA technical indicator\n
            `ma_chart`: Plots MA technical indicator\n
            `macd`: Moving average convergence divergence\n
            `macd_chart`: Plots MACD signal\n
            `obv`: On Balance Volume\n
            `obv_chart`: Plots OBV technical indicator\n
            `rsi`: Relative strength index\n
            `rsi_chart`: Plots RSI Indicator\n
            `rvol_garman_klass`: Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.\n
            `rvol_hodges_tompkins`: Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.\n
            `rvol_parkinson`: Parkinson volatility uses the high and low price of the day rather than just close to close prices.\n
            `rvol_rogers_satchell`: Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.\n
            `rvol_std`: Standard deviation measures how widely returns are dispersed from the average return.\n
            `rvol_yang_zhang`: Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).\n
            `sma`: Gets simple moving average (SMA) for stock\n
            `standard_deviation`: Standard deviation measures how widely returns are dispersed from the average return.\n
            `stoch`: Stochastic oscillator\n
            `stoch_chart`: Plots stochastic oscillator signal\n
            `vwap`: Gets volume weighted average price (VWAP)\n
            `vwap_chart`: Plots VWMA technical indicator\n
            `wma`: Gets weighted moving average (WMA) for stock\n
            `zlma`: Gets zero-lagged exponential moving average (ZLEMA) for stock\n
        """

        return model.TaRoot()


class SDKLogger:
    def __init__(self) -> None:
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not get_current_system().LOGGING_SUPPRESS:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging() -> None:
        # pylint: disable=C0415
        from openbb_terminal.core.session.current_system import set_system_variable
        from openbb_terminal.core.log.generation.settings_logger import log_all_settings
        from openbb_terminal.loggers import setup_logging

        set_system_variable("LOGGING_SUB_APP", "sdk")
        setup_logging()
        log_all_settings()

    @staticmethod
    def _try_to_login(sdk: "OpenBBSDK"):
        if is_local() and is_auth_enabled():
            try:
                sdk.login(silent=True)
            except Exception:
                pass


openbb = OpenBBSDK()
