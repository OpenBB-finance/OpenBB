"""Pythonic portfolio"""
__docformat__ = "numpy"

import logging

import pandas as pd
import yfinance as yf
import numpy as np

from openbb_terminal.portfolio import allocation_model
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
    read_orderbook: Class method to read orderbook from file
        
    __set_orderbook:
        preprocess_orderbook: Method to preprocess, format and compute auxiliary fields
    
    load_benchmark: Adds benchmark ticker, info, prices and returns
        mimic_trades_for_benchmark: Mimic trades from the orderbook based on chosen benchmark assuming partial shares

    generate_portfolio_data: Generates portfolio data from orderbook
        load_portfolio_historical_prices: Loads historical adj close prices for tickers in list of trades
        populate_historical_trade_data: Create a new dataframe to store historical prices by ticker
        calculate_holdings: Calculate holdings from historical data

    calculate_reserves:

    calculate_allocations:

    set_risk_free_rate: Sets risk free rate

    calculate_metrics:
        
    """
    
    def __init__(self, orderbook: pd.DataFrame = pd.DataFrame()):
        """Initialize Portfolio class"""

        # Portfolio
        self.tickers = {}
        self.inception_date = None
        self.static_data = pd.DataFrame()
        self.historical_trade_data = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.itemized_holdings = pd.DataFrame()
        self.portfolio_trades = pd.DataFrame()

        self.portfolio_assets_allocation = pd.DataFrame()
        self.portfolio_regional_allocation = pd.DataFrame()
        self.portfolio_country_allocation = pd.DataFrame()

        # Prices
        self.portfolio_historical_prices = pd.DataFrame()
        self.risk_free_rate = float(0)

        # Benchmark
        self.benchmark_ticker: str = ""
        self.benchmark_info = None
        self.benchmark_historical_prices = pd.DataFrame()
        self.benchmark_returns = pd.DataFrame()
        self.benchmark_trades = pd.DataFrame()

        self.benchmark_assets_allocation = pd.DataFrame()
        self.benchmark_regional_allocation = pd.DataFrame()
        self.benchmark_country_allocation = pd.DataFrame()

        # Set and preprocess orderbook
        self.__set_orderbook(orderbook)

    def __set_orderbook(self, orderbook):
        self.__orderbook = orderbook
        self.preprocess_orderbook()
    
    def get_orderbook(self):
        try:
            return self.__orderbook
        except:
            logger.warning("No orderbook loaded")
            console.print("[red]No orderbook loaded.[/red]\n")
        
    @staticmethod
    def read_orderbook(path: str) -> pd.DataFrame:
        """Class method to read orderbook from file

        Args:
            path (str): path to orderbook file
        """
        # Load orderbook from file
        if path.endswith(".xlsx"):
            orderbook = pd.read_excel(path)
        elif path.endswith(".csv"):
            orderbook = pd.read_csv(path)

        return orderbook

    def preprocess_orderbook(self):
        """Method to preprocess, format and compute auxiliary fields
        """
        try:
            # Convert Date to datetime
            self.__orderbook["Date"] = pd.to_datetime(self.__orderbook["Date"])

            # Sort orderbook by date
            self.__orderbook = self.__orderbook.sort_values(by="Date")
            
            # Capitalize Ticker and Type [of instrument...]
            self.__orderbook["Ticker"] = self.__orderbook["Ticker"].map(lambda x: x.upper())
            self.__orderbook["Type"] = self.__orderbook["Type"].map(lambda x: x.upper())

            # Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            self.__orderbook["Side"] = self.__orderbook["Side"].map(
                lambda x: 
                1 if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )

            # Convert quantity to signed integer
            self.__orderbook["Quantity"] = self.__orderbook["Quantity"] * self.__orderbook["Side"]

            # Determining the investment/divestment value
            self.__orderbook["Investment"] = self.__orderbook["Quantity"] * self.__orderbook["Price"]

            # Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.__orderbook[self.__orderbook.Type == "CRYPTOCURRENCY"]
            self.__orderbook.loc[(self.__orderbook.Type == "CRYPTOCURRENCY"), "Ticker"] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(crypto_trades.Ticker, crypto_trades.Currency)
            ]


            # Create tickers dictionary with structure {'Type': [Ticker]}
            for type in set(self.__orderbook["Type"]):
                self.tickers[type] = list(set(self.__orderbook[self.__orderbook['Type'].isin([type])]["Ticker"]))

            # Create list with tickers except cash
            self.tickers_except_cash = list(set(self.__orderbook["Ticker"]))
            if "CASH" in self.tickers_except_cash: self.tickers_except_cash.remove("CASH")

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
            self.inception_date = self.__orderbook["Date"][0]

            # Save trades static data
            self.static_data = self.__orderbook.pivot(index="Ticker", columns=[], values=["Type", "Sector", "Industry", "Country"])

        except:
            raise Exception('Could not preprocess orderbook.') 

    def load_benchmark(self, ticker: str = "SPY"):
        """Adds benchmark dataframe

        Args:
            ticker (str): benchmark ticker to download data
        """
        self.benchmark_ticker = ticker
        self.benchmark_historical_prices = yf.download(ticker, start=self.inception_date, threads=False, progress=False)["Adj Close"]
        self.benchmark_returns = self.benchmark_historical_prices.pct_change().dropna()
        self.benchmark_info = yf.Ticker(ticker).info
        self.mimic_trades_for_benchmark()
        
    def mimic_trades_for_benchmark(self):
        """Mimic trades from the orderbook based on chosen benchmark assuming partial shares
        """
        # Create dataframe to store benchmark trades
        self.benchmark_trades = self.__orderbook[["Date", "Type", "Investment"]].copy()
        # Set current price of benchmark
        self.benchmark_trades["Last price"] = self.benchmark_historical_prices[-1]
        self.benchmark_trades[
            [
                "Benchmark Quantity", 
                "Trade price"
            ]
        ] = float(0)

        # Iterate over orderbook to replicate trades on benchmark (skip CASH)
        for index, trade in self.__orderbook.iterrows():
            if trade["Type"] != "CASH":
                # Select date to search (if not in historical prices, get closest value)
                if trade["Date"] not in self.benchmark_historical_prices.index:
                    date = self.benchmark_historical_prices.index.searchsorted(trade["Date"])
                else:
                    date = trade["Date"]

                # Populate benchmark orderbook trades
                self.benchmark_trades["Trade price"][index] = self.benchmark_historical_prices[date]
                self.benchmark_trades["Benchmark Quantity"][index] = trade["Investment"] / self.benchmark_trades["Trade price"][index]
               
        self.benchmark_trades["Benchmark Investment"] = self.benchmark_trades["Trade price"] * self.benchmark_trades["Benchmark Quantity"]
        self.benchmark_trades["Benchmark Value"] = self.benchmark_trades["Last price"] * self.benchmark_trades["Benchmark Quantity"]
        self.benchmark_trades["Benchmark % Return"] = self.benchmark_trades["Benchmark Value"] / self.benchmark_trades["Benchmark Investment"] - 1
        self.benchmark_trades["Benchmark Abs Return"] = self.benchmark_trades["Benchmark Value"] - self.benchmark_trades["Benchmark Investment"]
        # TODO: To add alpha here, we must pull prices from original trades and get last price
        # for each of those trades. Then just calculate returns and compare to benchmark
        self.benchmark_trades.fillna(0, inplace=True)

    def generate_portfolio_data(self):
        """Generates portfolio data from orderbook
        """
        self.load_portfolio_historical_prices()
        self.populate_historical_trade_data()
        self.calculate_holdings()

        # Determine the returns, replace inf values with NaN and then drop any missing values
        self.returns = self.historical_trade_data["Holdings"]["Total"].pct_change()
        self.returns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.returns = self.returns.dropna()

        # Determine invested amount, relative and absolute return based on last close
        last_price = self.historical_trade_data["Close"].iloc[-1]

        # self.portfolio_trades = pd.DataFrame(self.__orderbook["Date"])
        self.portfolio_trades = self.__orderbook.copy()
        self.portfolio_trades[
            [
                "Portfolio Investment",
                "Close",
                "Portfolio Value",
                "% Portfolio Return",
                "Abs Portfolio Return",
            ]
        ] = float(0)

        for index, trade in self.__orderbook.iterrows():
            if trade["Type"] != "CASH":
                self.portfolio_trades["Close"][index] = last_price[trade["Ticker"]]
                self.portfolio_trades["Portfolio Investment"][index] = trade["Investment"]
                self.portfolio_trades["Portfolio Value"][index] = (self.portfolio_trades["Close"][index] * trade["Quantity"])
                self.portfolio_trades["% Portfolio Return"][index] = (self.portfolio_trades["Portfolio Value"][index]/self.portfolio_trades["Portfolio Investment"][index]) - 1
                self.portfolio_trades["Abs Portfolio Return"].loc[index] = (self.portfolio_trades["Portfolio Value"][index]- self.portfolio_trades["Portfolio Investment"][index])


    def load_portfolio_historical_prices(self, use_close: bool = False):
        """Loads historical adj close prices for tickers in list of trades
        """

        for type in self.tickers.keys():
            if type == "STOCK" or type == "ETF":
                # Download yfinance data
                price_data = yf.download(
                        self.tickers[type],
                        start=self.inception_date,
                        progress=False
                    )["Close" if use_close else "Adj Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = self.tickers[type]

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [
                        self.portfolio_historical_prices, 
                        price_data
                    ], axis=1)

            elif type == "CRYPTOCURRENCY":
                
                # Download yfinance data
                price_data = yf.download(
                        self.tickers[type],
                        start=self.inception_date,
                        progress=False
                    )["Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = self.tickers[type]
        
                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [
                        self.portfolio_historical_prices, 
                        price_data
                    ], axis=1)

            elif type == "CASH":
                # Set CASH price to 1
                self.portfolio_historical_prices["CASH"] = 1

            else:
                raise Exception("Type not supported in the orderbook.")

            # Fill missing values with last known price
            self.portfolio_historical_prices.fillna(method='ffill', inplace=True)

    def populate_historical_trade_data(self):
        """Create a new dataframe to store historical prices by ticker
        """
        trade_data = self.__orderbook.pivot(
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
        self.portfolio_historical_prices.columns = pd.MultiIndex.from_product([["Close"], self.portfolio_historical_prices.columns])

        # Merge with historical close prices (and fillna)
        trade_data = pd.merge(
            trade_data,
            self.portfolio_historical_prices,
            how="right",
            left_index=True,
            right_index=True,
        ).fillna(0)

        # Accumulate quantity held by trade date
        trade_data["Quantity"] = trade_data["Quantity"].cumsum()

        self.historical_trade_data = trade_data


    def calculate_holdings(self):
        """Calculate holdings from historical data
        """
        trade_data = self.historical_trade_data
        
        # For each type [STOCK, ETF, etc] calculate holdings value by trade date
        # and add it to historical_trade_data
        for type in self.tickers.keys():
            trade_data[pd.MultiIndex.from_product([["Holdings"], self.tickers[type]])] = trade_data["Quantity"][self.tickers[type]] * trade_data["Close"][self.tickers[type]]

        # Find amount of cash held in account. If CASH exist within the Orderbook,
        # the cash hold is defined as deposited cash - stocks bought + stocks sold
        # Otherwise, the cash hold will equal the invested amount.
        if "CASH" in self.tickers:
            trade_data.loc[:, ("Holdings", "CASH")] = (trade_data["Investment"]["CASH"] 
                - trade_data["Investment"][self.tickers_except_cash].sum(axis=1) 
                - trade_data["Fees"].sum(axis=1)
                - trade_data["Premium"].sum(axis=1)
            ).cumsum()
        else:
            trade_data.loc[:, ("Holdings", "CASH")] = (trade_data["Investment"][self.tickers_except_cash].sum(axis=1)).cumsum()

        trade_data.loc[:, ("Holdings", "Total")] = (trade_data["Holdings"]["CASH"] + 
                                                        trade_data["Holdings"][self.tickers_except_cash].sum(axis=1)
                                                        )

        # IS THIS BEING USED ANYWHERE?
        # self.portfolio_value = portfolio["TotalHoldings"]

        for type in self.tickers.keys():
                self.itemized_holdings[type] = trade_data["Holdings"][self.tickers[type]].sum(axis=1)

        self.historical_trade_data = trade_data


    def calculate_reserves(self):
        """_summary_
        """
        #TODO: Add back cash dividends and deduct exchange costs
        pass

    def calculate_allocations(self):
        """Determine allocations based on assets, sectors, countries and regional."""
        
        # Determine asset allocation
        (
            self.benchmark_assets_allocation,
            self.portfolio_assets_allocation,
        ) = allocation_model.obtain_assets_allocation(
            self.benchmark_info, self.portfolio_trades
        )

        # Determine sector allocation
        (
            self.benchmark_sectors_allocation,
            self.portfolio_sectors_allocation,
        ) = allocation_model.obtain_sector_allocation(
            self.benchmark_info, self.portfolio_trades
        )

        # Determine regional and country allocations
        (
            self.benchmark_regional_allocation,
            self.benchmark_country_allocation,
        ) = allocation_model.obtain_benchmark_regional_and_country_allocation(
            self.benchmark_ticker
        )

        (
            self.portfolio_regional_allocation,
            self.portfolio_country_allocation,
        ) = allocation_model.obtain_portfolio_regional_and_country_allocation(
            self.portfolio_trades
        )


    def calculate_metrics(self):
        """_summary_
        """
        pass

    def set_risk_free_rate(self, risk_free_rate: float):
        """Sets risk free rate

        Args:
            risk_free (float): risk free rate in decimal format
        """
        self.risk_free_rate = risk_free_rate


# Determine reserves
# Determine allocations
# Determine key metrics and ratios