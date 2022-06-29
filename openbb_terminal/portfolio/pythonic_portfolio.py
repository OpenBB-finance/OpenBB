"""Pythonic portfolio"""
__docformat__ = "numpy"

import logging

import pandas as pd
import yfinance as yf

from openbb_terminal.rich_config import console

# Disable warning on pd chained assignments used to get benchmark quantity
pd.options.mode.chained_assignment = None  

logger = logging.getLogger(__name__)

class Portfolio:
    """
    Implements a Portfolio and related methods. A Portfolio is created by loading
    an orderbook into itself.

    Attributes
    -------


    Methods
    -------
    load_orderbook: Class method that loads orderbook into Portfolio object
        preprocess_orderbook: Method to preprocess, format and compute auxiliary fields
    
    load_benchmark: Adds benchmark ticker, info, prices and returns
        mimic_trades_for_benchmark: Mimic trades from the orderbook based on chosen benchmark assuming partial shares

    calculate_trades: Generates portfolio data from orderbook
        load_historical_prices: Loads historical adj close prices for tickers in list of trades
        populate_historical_trade_data:

    determine_reserves:

    determine_allocations:

    determine_metrics:
        set_risk_free_rate: Sets risk free rate
    """
    
    def __init__(self, orderbook: pd.DataFrame = pd.DataFrame()):
        """Initialize Portfolio class"""

        # Orderbook
        self.orderbook = orderbook

        # Portfolio
        self.tickers = {}
        self.inception_date = None
        self.static_data = pd.DataFrame()
        self.historical_trade_data = pd.DataFrame()
        self.holdings = pd.DataFrame()

        # Prices
        self.portfolio_historical_prices = pd.DataFrame()
        self.risk_free_rate = float(0)

        # Benchmark
        self.benchmark_ticker: str = ""
        self.benchmark_historical_prices = pd.DataFrame()
        self.benchmark_returns = pd.DataFrame()
        self.benchmark_orderbook = pd.DataFrame()


    @classmethod   
    def load_orderbook(cls, path: str):
        """Class method creates a Portfolio object by loading an orderbook into it

        Args:
            path (str): path to orderbook file
        """
        # Load orderbook from file
        if path.endswith(".xlsx"):
            orderbook = pd.read_excel(path)
        elif path.endswith(".csv"):
            orderbook = pd.read_csv(path)

        # Create Portfolio object
        portfolio = cls(orderbook)
        # Ask portfolio for orderbook preprocess
        portfolio.preprocess_orderbook()

        return portfolio

    def preprocess_orderbook(self):
        """Method to preprocess, format and compute auxiliary fields
        """
        if not self.orderbook.empty:

            # Convert Date to datetime
            self.orderbook["Date"] = pd.to_datetime(self.orderbook["Date"])

            # Sort orderbook by date
            self.orderbook = self.orderbook.sort_values(by="Date")
            
            # Capitalize Ticker and Type [of instrument...]
            self.orderbook["Ticker"] = self.orderbook["Ticker"].map(lambda x: x.upper())
            self.orderbook["Type"] = self.orderbook["Type"].map(lambda x: x.upper())

            # Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            self.orderbook["Side"] = self.orderbook["Side"].map(
                lambda x: 
                1 if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )

            # Convert quantity to signed integer
            self.orderbook["Quantity"] = self.orderbook["Quantity"] * self.orderbook["Side"]

            # Determining the investment/divestment value
            self.orderbook["Investment"] = self.orderbook["Quantity"] * self.orderbook["Price"]

            # Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.orderbook[self.orderbook.Type == "CRYPTOCURRENCY"]
            self.orderbook.loc[(self.orderbook.Type == "CRYPTOCURRENCY"), "Ticker"] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(crypto_trades.Ticker, crypto_trades.Currency)
            ]


            # Create tickers dictionary with structure {'Type': [Ticker]}
            for type in set(self.orderbook["Type"]):
                self.tickers[type] = list(self.orderbook[self.orderbook['Type'].isin([type])]["Ticker"])

            # Warn user if no cash deposit in account
            if "CASH" not in self.tickers.keys():
                logger.warning(
                    "No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account"
                )
                console.print(
                    "[red]No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account[/red]."
                )

            # Save orderbook inception date
            self.inception_date = self.orderbook["Date"][0]

            # Save trades static data
            self.static_data = self.orderbook.pivot(index="Ticker", columns=[], values=["Type", "Sector", "Industry", "Country"])

    def load_benchmark(self, ticker: str):
        """Adds benchmark dataframe

        Args:
            ticker (str): benchmark ticker to download data
        """
        self.benchmark_ticker = ticker
        self.benchmark_historical_prices = yf.download(ticker, start=self.inception_date, threads=False, progress=False)["Adj Close"]
        self.benchmark_returns = self.benchmark_historical_prices.pct_change().dropna()
        self.mimic_trades_for_benchmark()
        
    def mimic_trades_for_benchmark(self):
        """Mimic trades from the orderbook based on chosen benchmark assuming partial shares
        """
        # Create dataframe to store benchmark trades
        self.benchmark_orderbook = self.orderbook[["Date", "Type", "Investment"]].copy()
        # Set current price of benchmark
        self.benchmark_orderbook["Last price"] = self.benchmark_historical_prices[-1]
        self.benchmark_orderbook[
            [
                "Quantity", 
                "Trade price"
            ]
        ] = float(0)

        # Iterate over orderbook to replicate trades on benchmark (skip CASH)
        for index, trade in self.orderbook.iterrows():
            if trade["Type"] != "CASH":
                # Select date to search (if not in historical prices, get closest value)
                if trade["Date"] not in self.benchmark_historical_prices.index:
                    date = self.benchmark_historical_prices.index.searchsorted(trade["Date"])
                else:
                    date = trade["Date"]

                # Populate benchmark orderbook trades
                self.benchmark_orderbook["Trade price"][index] = self.benchmark_historical_prices[date]
                self.benchmark_orderbook["Quantity"][index] = trade["Investment"] / self.benchmark_orderbook["Trade price"][index]
               
        self.benchmark_orderbook["Investment"] = self.benchmark_orderbook["Trade price"] * self.benchmark_orderbook["Quantity"]
        self.benchmark_orderbook["Current value"] = self.benchmark_orderbook["Last price"] * self.benchmark_orderbook["Quantity"]
        self.benchmark_orderbook["% Return"] = self.benchmark_orderbook["Current value"] / self.benchmark_orderbook["Investment"] - 1
        self.benchmark_orderbook["Absolute Return"] = self.benchmark_orderbook["Current value"] - self.benchmark_orderbook["Investment"]
        # TODO: To add alpha here, we must pull prices from original trades and get last price
        # for each of those trades. Then just calculate returns and compare to benchmark
        self.benchmark_orderbook.fillna(0, inplace=True)

    def calculate_trades(self):
        """Generates portfolio data from orderbook
        """
        self.load_historical_prices()

        self.populate_historical_trade_data()


    def load_historical_prices(self):
        """Loads historical adj close prices for tickers in list of trades
        """
        for type in self.tickers.keys():
            if type == "STOCK":
                
                # Download yfinance data
                data = yf.download(
                        self.tickers[type],
                        start=self.inception_date,
                        progress=False
                    )["Adj Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    data = pd.DataFrame(data)
                    data.columns = self.tickers[type]

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [
                        self.portfolio_historical_prices, 
                        data
                    ], axis=1)

            elif type == "CRYPTOCURRENCY":
                
                # Download yfinance data
                data = yf.download(
                        self.tickers[type],
                        start=self.inception_date,
                        progress=False
                    )["Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    data = pd.DataFrame(data)
                    data.columns = self.tickers[type]
        
                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [
                        self.portfolio_historical_prices, 
                        data
                    ], axis=1)
                
            else:
                # Type not supported
                pass

            # Set CASH price to 1 by default
            self.portfolio_historical_prices["CASH"] = 1

            # Fill missing values with last known price
            self.portfolio_historical_prices.fillna(method='ffill', inplace=True)

    def populate_historical_trade_data(self):
        """Create a new dataframe to store historical prices by ticker
        """

        self.historical_trade_data = self.orderbook.pivot(
            index="Date",
            columns="Ticker",
            values=[
                "Type",
                "Sector",
                "Industry",
                "Country",
                "Price",
                "Quantity",
                "Fees",
                "Premium",
                "Investment",
                "Side",
                "Currency",
            ],
        )

        # Make historical prices columns a multi-index. This helps the merging.
        self.portfolio_historical_prices.columns = pd.MultiIndex.from_product(
            [["Close"], self.portfolio_historical_prices.columns]
        )

        # # Merge with historical close prices (and fillna)
        self.historical_trade_data = pd.merge(
            self.historical_trade_data,
            self.portfolio_historical_prices,
            how="right",
            left_index=True,
            right_index=True,
        ).fillna(0)

        # # Accumulate quantity held by trade date
        self.historical_trade_data["Quantity"] = self.historical_trade_data["Quantity"].cumsum()

        # For each type [STOCK, ETF, etc] calculate holdings value by trade date
        # and add it to historical_trade_data
        for type in self.tickers.keys():
            self.historical_trade_data[pd.MultiIndex.from_product([[type], self.tickers[type]])] = self.historical_trade_data["Quantity"][self.tickers[type]] * self.historical_trade_data["Close"][self.tickers[type]]
            # portfolio.historical_trade_data[pd.MultiIndex.from_product([[type], portfolio.tickers[type]])] = portfolio.historical_trade_data["Quantity"][portfolio.tickers[type]] * portfolio.historical_trade_data["Close"][portfolio.tickers[type]]


    def determine_reserves(self):
        """_summary_
        """
        #TODO: Add back cash dividends and deduct exchange costs
        pass

    def determine_allocations(self):
        """_summary_
        """
        #TODO: Calculate allocations: this method seems fine in it's
        # original form, which uses the allocation_model module
        pass

    def determine_metrics(self):
        """_summary_
        """
        pass

    def set_risk_free_rate(self, risk_free_rate: float):
        """Sets risk free rate

        Args:
            risk_free (float): risk free rate in decimal format
        """
        self.risk_free_rate = risk_free_rate

if __name__ == "__main__":
    path = "openbb_terminal/portfolio/portfolio_analysis/portfolios/Public_Equity_Orderbook.xlsx"
    portfolio = Portfolio.load_orderbook(path)
    # print(portfolio.tickers)
    # print(portfolio.inception_date)
    # print(portfolio.orderbook.head())
    # portfolio.set_risk_free_rate(0.035)
    # print(portfolio.risk_free_rate)
    portfolio.load_benchmark("SPY")
    # print(portfolio.benchmark_ticker)
    # print(portfolio.benchmark_historical_prices)
    # # print(portfolio.benchmark_returns)
    # print(portfolio.benchmark_orderbook)
    portfolio.load_historical_prices()
    print(portfolio.portfolio_historical_prices)
    # Ver com o Chavi porque é que o yfinance fica bloqueado
    # quando peço preços neste modulo... No Jupyter funciona bem..

# Load orderbook
# Load benchmark
# Calculate trades
# Determine reserves
# Determine allocations
# Determine key metrics and ratios