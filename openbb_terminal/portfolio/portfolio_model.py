"""Portfolio Model"""
__docformat__ = "numpy"

import contextlib
import logging
from typing import Dict, Any, Tuple, Union
import datetime

import numpy as np
import scipy
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from sklearn.metrics import r2_score
from pycoingecko import CoinGeckoAPI
from openbb_terminal.common.quantitative_analysis import qa_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio import portfolio_helper
from openbb_terminal.portfolio.allocation_model import get_allocation
from openbb_terminal.rich_config import console

# pylint: disable=E1136,W0201,R0902,C0302
# pylint: disable=unsupported-assignment-operation,redefined-outer-name,too-many-public-methods, consider-using-f-string

logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

pd.options.mode.chained_assignment = None


class PortfolioEngine:
    """
    Class for portfolio analysis in OpenBB
    Implements a Portfolio and related methods.

    Methods
    -------
    read_transactions: Class method to read transactions from file

    __set_transactions:
        __preprocess_transactions: Method to preprocess, format and compute auxiliary fields

    get_transactions: Outputs the formatted transactions DataFrame

    set_benchmark: Adds benchmark ticker, info, prices and returns
        mimic_trades_for_benchmark: Mimic trades from the transactions based on chosen benchmark assuming partial shares

    generate_portfolio_data: Generates portfolio data from transactions
        load_portfolio_historical_prices: Loads historical adj close prices for tickers in list of trades
        populate_historical_trade_data: Create a new dataframe to store historical prices by ticker
        calculate_value: Calculate value end of day from historical data

    set_risk_free_rate: Sets risk free rate

    calculate_reserves: Takes dividends into account for returns calculation

    calculate_allocation: Determine allocation based on assets, sectors, countries and regions.
    """

    def __init__(self, transactions: pd.DataFrame = pd.DataFrame()):
        """Initialize PortfolioEngine class"""

        # Portfolio
        self.empty = True
        self.tickers_list = None
        self.tickers: Dict[Any, Any] = {}
        self.inception_date = datetime.date(1970, 1, 1)
        self.historical_trade_data = pd.DataFrame()
        self.itemized_value = pd.DataFrame()
        self.portfolio_value = None
        self.portfolio_historical_prices = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.portfolio_trades = pd.DataFrame()
        self.risk_free_rate = float(0)
        self.portfolio_assets_allocation = pd.DataFrame()
        self.portfolio_sectors_allocation = pd.DataFrame()
        self.portfolio_regions_allocation = pd.DataFrame()
        self.portfolio_countries_allocation = pd.DataFrame()

        # Benchmark
        self.benchmark_ticker: str = ""
        self.benchmark_info = None
        self.benchmark_historical_prices = pd.DataFrame()
        self.benchmark_returns = pd.DataFrame()
        self.benchmark_trades = pd.DataFrame()
        self.benchmark_assets_allocation = pd.DataFrame()
        self.benchmark_sectors_allocation = pd.DataFrame()
        self.benchmark_regions_allocation = pd.DataFrame()
        self.benchmark_countries_allocation = pd.DataFrame()

        # Set and preprocess transactions
        if not transactions.empty:
            self.__set_transactions(transactions)

    def __set_transactions(self, transactions):
        self.__transactions = transactions
        self.__preprocess_transactions()
        self.empty = False

    def get_transactions(self):
        """Get formatted transactions

        Returns
        -------
            pd.DataFrame: formatted transactions
        """

        df = self.__transactions[
            [
                "Date",
                "Type",
                "Ticker",
                "Side",
                "Price",
                "Quantity",
                "Fees",
                "Investment",
                "Currency",
                "Sector",
                "Industry",
                "Country",
                "Region",
            ]
        ]
        df = df.replace(np.nan, "-")
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df.sort_values(by="Date", ascending=False, inplace=True)
        return df

    @staticmethod
    def read_transactions(path: str) -> pd.DataFrame:
        """Static method to read transactions from file.

        Parameters
        ----------
        path: str
            path to transactions file

        Returns
        -------
        pd.DataFrame
            DataFrame with transactions
        """
        # Load transactions from file
        if path.endswith(".xlsx"):
            transactions = pd.read_excel(path)
        elif path.endswith(".csv"):
            transactions = pd.read_csv(path)

        return transactions

    @log_start_end(log=logger)
    def __preprocess_transactions(self):
        """Method to preprocess, format and compute auxiliary fields.

        Preprocessing steps:
            0. If optional fields not in the transactions add missing
            1. Convert Date to datetime
            2. Sort transactions by date
            3. Capitalize Ticker and Type [of instrument...]
            4. Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            5. Convert quantity to signed integer
            6. Determining the investment/divestment value
            7. Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            8. Reformat STOCK/ETF tickers to yfinance format if ISIN provided
            9. Remove unsupported ISINs that came out empty
            10. Create tickers dictionary with structure {'Type': [Ticker]}
            11. Create list with tickers except cash
            12. Save transactions inception date
            13. Populate fields Sector, Industry and Country
        """

        p_bar = tqdm(range(14), desc="Preprocessing transactions")

        try:

            # 0. If optional fields not in the transactions add missing
            optional_fields = [
                "Sector",
                "Industry",
                "Country",
                "Region",
                "Fees",
                "Premium",
                "ISIN",
            ]
            if not set(optional_fields).issubset(set(self.__transactions.columns)):
                for field in optional_fields:
                    if field not in self.__transactions.columns:
                        self.__transactions[field] = np.nan

            p_bar.n += 1
            p_bar.refresh()

            # 1. Convert Date to datetime
            self.__transactions["Date"] = pd.to_datetime(self.__transactions["Date"])

            p_bar.n += 1
            p_bar.refresh()

            # 2. Sort transactions by date
            self.__transactions = self.__transactions.sort_values(by="Date")

            p_bar.n += 1
            p_bar.refresh()

            # 3. Capitalize Ticker and Type [of instrument...]
            self.__transactions["Ticker"] = self.__transactions["Ticker"].map(
                lambda x: x.upper()
            )
            self.__transactions["Type"] = self.__transactions["Type"].map(
                lambda x: x.upper()
            )

            p_bar.n += 1
            p_bar.refresh()

            # 4. Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            self.__transactions["Signal"] = self.__transactions["Side"].map(
                lambda x: 1
                if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )

            p_bar.n += 1
            p_bar.refresh()

            # 5. Convert quantity to signed integer
            self.__transactions["Quantity"] = (
                abs(self.__transactions["Quantity"]) * self.__transactions["Signal"]
            )

            p_bar.n += 1
            p_bar.refresh()

            # 6. Determining the investment/divestment value
            self.__transactions["Investment"] = (
                self.__transactions["Quantity"] * self.__transactions["Price"]
                + self.__transactions["Fees"]
            )

            p_bar.n += 1
            p_bar.refresh()

            # 7. Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.__transactions[self.__transactions.Type == "CRYPTO"]
            self.__transactions.loc[
                (self.__transactions.Type == "CRYPTO"), "Ticker"
            ] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(
                    crypto_trades.Ticker, crypto_trades.Currency
                )
            ]

            p_bar.n += 1
            p_bar.refresh()

            # 8. Reformat STOCK/ETF tickers to yfinance format if ISIN provided.

            # If isin not valid ticker is empty
            self.__transactions["yf_Ticker"] = self.__transactions["ISIN"].apply(
                lambda x: yf.utils.get_ticker_by_isin(x) if not pd.isna(x) else np.nan
            )

            empty_tickers = list(
                self.__transactions[
                    (self.__transactions["yf_Ticker"] == "")
                    | (self.__transactions["yf_Ticker"].isna())
                ]["Ticker"].unique()
            )

            # If ticker from isin is empty it is not valid in yfinance, so check if user provided ticker is supported
            removed_tickers = []
            for item in empty_tickers:
                with contextlib.redirect_stdout(None):
                    # Suppress yfinance failed download message if occurs
                    valid_ticker = not (
                        yf.download(
                            item,
                            start=datetime.datetime.now() + datetime.timedelta(days=-5),
                            progress=False,
                        ).empty
                    )
                    if valid_ticker:
                        # Invalid ISIN but valid ticker
                        self.__transactions.loc[
                            self.__transactions["Ticker"] == item, "yf_Ticker"
                        ] = np.nan
                    else:
                        self.__transactions.loc[
                            self.__transactions["Ticker"] == item, "yf_Ticker"
                        ] = ""
                        removed_tickers.append(item)

            # Merge reformated tickers into Ticker
            self.__transactions["Ticker"] = self.__transactions["yf_Ticker"].fillna(
                self.__transactions["Ticker"]
            )

            p_bar.n += 1
            p_bar.refresh()

            # 9. Remove unsupported ISINs that came out empty
            self.__transactions.drop(
                self.__transactions[self.__transactions["Ticker"] == ""].index,
                inplace=True,
            )

            p_bar.n += 1
            p_bar.refresh()

            # 10. Create tickers dictionary with structure {'Type': [Ticker]}
            for ticker_type in set(self.__transactions["Type"]):
                self.tickers[ticker_type] = list(
                    set(
                        self.__transactions[
                            self.__transactions["Type"].isin([ticker_type])
                        ]["Ticker"]
                    )
                )

            p_bar.n += 1
            p_bar.refresh()

            # 11. Create list with tickers except cash
            self.tickers_list = list(set(self.__transactions["Ticker"]))

            p_bar.n += 1
            p_bar.refresh()

            # 12. Save transactions inception date
            self.inception_date = self.__transactions["Date"][0]

            p_bar.n += 1
            p_bar.refresh()

            # 13. Populate fields Sector, Industry and Country
            if (
                self.__transactions.loc[
                    self.__transactions["Type"] == "STOCK",
                    optional_fields,
                ]
                .isnull()
                .values.any()
            ):
                # If any fields is empty for stocks (overwrites any info there)
                self.load_company_data()

            p_bar.n += 1
            p_bar.refresh()

            # Warn user of removed ISINs
            if removed_tickers:
                p_bar.disable = True
                console.print(
                    f"\n[red]The following tickers are not supported and were removed: {removed_tickers}."
                    f"\nManually edit the 'Ticker' field with the proper Yahoo Finance suffix or provide a valid ISIN."
                    f"\nSuffix info on 'Yahoo Finance market coverage':"
                    " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html"
                    f"\nE.g. IWDA -> IWDA.AS[/red]\n"
                )
        except Exception:
            console.print("\nCould not preprocess transactions.")

    @log_start_end(log=logger)
    def load_company_data(self):
        """Method to populate company data for stocks such as sector, industry and country"""

        for ticker_type, ticker_list in self.tickers.items():
            # yfinance only has sector, industry and country for stocks
            if ticker_type == "STOCK":
                for ticker in ticker_list:
                    # Only gets fields for tickers with missing data
                    # TODO: Should only get field missing for tickers with missing data
                    # now it's taking the 4 of them
                    if (
                        self.__transactions.loc[
                            self.__transactions["Ticker"] == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ]
                        .isnull()
                        .values.any()
                    ):
                        # Get ticker info in list ["Sector", "Industry", "Country", "Region"] from isin/ticker
                        info_list = portfolio_helper.get_info_from_ticker(ticker)

                        # Replace fields in transactions
                        self.__transactions.loc[
                            self.__transactions.Ticker == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ] = info_list

            elif ticker_type == "CRYPTO":
                for ticker in ticker_list:
                    if (
                        self.__transactions.loc[
                            self.__transactions["Ticker"] == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ]
                        .isnull()
                        .values.any()
                    ):
                        # Get ticker info in list ["Sector", "Industry", "Country", "Region"]
                        info_list = ["Crypto", "Crypto", "Crypto", "Crypto"]

                        # Replace fields in transactions
                        self.__transactions.loc[
                            self.__transactions.Ticker == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ] = info_list

            else:
                for ticker in ticker_list:
                    if (
                        self.__transactions.loc[
                            self.__transactions["Ticker"] == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ]
                        .isnull()
                        .values.any()
                    ):
                        # Get ticker info in list ["Sector", "Industry", "Country", "Region"]
                        info_list = ["-", "-", "-", "-"]

                        # Replace fields in transactions
                        self.__transactions.loc[
                            self.__transactions.Ticker == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ] = info_list

    @log_start_end(log=logger)
    def set_benchmark(self, symbol: str = "SPY", full_shares: bool = False):
        """Load benchmark into portfolio.

        Parameters
        ----------
        symbol: str
            Benchmark symbol to download data
        full_shares: bool
            Whether to mimic the portfolio trades exactly (partial shares) or round down the
            quantity to the nearest number
        """

        p_bar = tqdm(range(4), desc="         Loading benchmark")

        self.benchmark_ticker = symbol

        self.benchmark_historical_prices = yf.download(
            symbol,
            start=self.inception_date - datetime.timedelta(days=1),
            threads=False,
            progress=False,
        )["Adj Close"]

        p_bar.n += 1
        p_bar.refresh()

        self.mimic_trades_for_benchmark(full_shares)

        # Merge benchmark and portfolio dates to ensure same length
        self.benchmark_historical_prices = pd.merge(
            self.portfolio_historical_prices["Close"],
            self.benchmark_historical_prices,
            how="outer",
            left_index=True,
            right_index=True,
        )["Adj Close"]
        self.benchmark_historical_prices.fillna(method="ffill", inplace=True)

        p_bar.n += 1
        p_bar.refresh()

        self.benchmark_returns = self.benchmark_historical_prices.pct_change().dropna()
        self.benchmark_info = yf.Ticker(symbol).info

        p_bar.n += 1
        p_bar.refresh()

        (
            self.returns,
            self.benchmark_returns,
        ) = portfolio_helper.make_equal_length(self.returns, self.benchmark_returns)

        p_bar.n += 1
        p_bar.refresh()

    @log_start_end(log=logger)
    def mimic_trades_for_benchmark(self, full_shares: bool = False):
        """Mimic trades from the transactions based on chosen benchmark assuming partial shares

        Parameters
        ----------
        full_shares: bool
            whether to mimic the portfolio trades exactly (partial shares) or round down the
            quantity to the nearest number.
        """

        # Create dataframe to store benchmark trades
        self.benchmark_trades = self.__transactions[
            ["Date", "Type", "Investment"]
        ].copy()

        # Set current price of benchmark
        self.benchmark_trades["Last price"] = self.benchmark_historical_prices[-1]

        # Map historical prices into trades
        self.benchmark_trades[["Benchmark Quantity"]] = float(0)
        benchmark_historical_prices = pd.DataFrame(self.benchmark_historical_prices)
        benchmark_historical_prices.columns.values[0] = "Trade price"
        self.benchmark_trades = self.benchmark_trades.set_index("Date")
        self.benchmark_trades.index = pd.to_datetime(self.benchmark_trades.index)
        self.benchmark_trades = self.benchmark_trades.merge(
            benchmark_historical_prices, how="left", left_index=True, right_index=True
        )
        self.benchmark_trades = self.benchmark_trades.reset_index()
        self.benchmark_trades["Trade price"] = self.benchmark_trades[
            "Trade price"
        ].fillna(method="ffill")

        # Calculate benchmark investment quantity
        if full_shares:
            self.benchmark_trades["Benchmark Quantity"] = np.floor(
                self.benchmark_trades["Investment"]
                / self.benchmark_trades["Trade price"]
            )
        else:
            self.benchmark_trades["Benchmark Quantity"] = (
                self.benchmark_trades["Investment"]
                / self.benchmark_trades["Trade price"]
            )

        self.benchmark_trades["Benchmark Investment"] = (
            self.benchmark_trades["Trade price"]
            * self.benchmark_trades["Benchmark Quantity"]
        )
        self.benchmark_trades["Benchmark Value"] = (
            self.benchmark_trades["Last price"]
            * self.benchmark_trades["Benchmark Quantity"]
        )
        self.benchmark_trades["Benchmark % Return"] = (
            self.benchmark_trades["Benchmark Value"]
            / self.benchmark_trades["Benchmark Investment"]
            - 1
        )
        self.benchmark_trades["Benchmark Abs Return"] = (
            self.benchmark_trades["Benchmark Value"]
            - self.benchmark_trades["Benchmark Investment"]
        )
        # TODO: To add alpha here, we must pull prices from original trades and get last price
        # for each of those trades. Then just calculate returns and compare to benchmark
        self.benchmark_trades.fillna(0, inplace=True)

        if full_shares:
            console.print(
                "Note that with full shares (-s) enabled, there will be a mismatch between how much you invested in the"
                f" portfolio ({round(sum(self.portfolio_trades['Portfolio Investment']), 2)}) and how much you invested"
                f" in the benchmark ({round(sum(self.benchmark_trades['Benchmark Investment']), 2)})."
            )

    @log_start_end(log=logger)
    def generate_portfolio_data(self):
        """Generates portfolio data from transactions"""

        self.load_portfolio_historical_prices()
        self.populate_historical_trade_data()
        self.calculate_value()

        # Determine the returns, replace inf values with NaN and then drop any missing values
        for _, data in self.tickers.items():
            self.historical_trade_data[
                pd.MultiIndex.from_product([["Returns"], data])
            ] = (
                self.historical_trade_data["End Value"][data]
                / self.historical_trade_data["Initial Value"][data]
                - 1
            )

        self.historical_trade_data.loc[:, ("Returns", "Total")] = (
            self.historical_trade_data["End Value"]["Total"]
            / self.historical_trade_data["Initial Value"]["Total"]
            - 1
        )

        self.returns = self.historical_trade_data["Returns"]["Total"]
        self.returns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.returns = self.returns.dropna()

        # Determine invested amount, relative and absolute return based on last close
        last_price = self.historical_trade_data["Close"].iloc[-1]

        # Save portfolio trades to compute allocations later
        self.portfolio_trades = self.__transactions.copy()
        self.portfolio_trades[
            [
                "Portfolio Investment",
                "Close",
                "Portfolio Value",
                "Portfolio % Return",
                "Abs Portfolio Return",
            ]
        ] = float(0)

        for index, trade in self.__transactions.iterrows():
            self.portfolio_trades["Close"][index] = last_price[trade["Ticker"]]
            self.portfolio_trades["Portfolio Investment"][index] = trade["Investment"]
            self.portfolio_trades["Portfolio Value"][index] = (
                self.portfolio_trades["Close"][index] * trade["Quantity"]
            )
            self.portfolio_trades["Portfolio % Return"][index] = (
                self.portfolio_trades["Portfolio Value"][index]
                / self.portfolio_trades["Portfolio Investment"][index]
            ) - 1
            self.portfolio_trades["Abs Portfolio Return"].loc[index] = (
                self.portfolio_trades["Portfolio Value"][index]
                - self.portfolio_trades["Portfolio Investment"][index]
            )

    @log_start_end(log=logger)
    def load_portfolio_historical_prices(self, use_close: bool = False):
        """Loads historical adj close/close prices for tickers in list of trades

        Parameters
        ----------
        use_close: bool
            whether to use close or adjusted close prices
        """

        p_bar = tqdm(range(len(self.tickers)), desc="        Loading price data")

        for ticker_type, data in self.tickers.items():
            if ticker_type in ["STOCK", "ETF", "CRYPTO"]:
                # Download yfinance data
                price_data = yf.download(
                    data, start=self.inception_date, progress=False
                )["Close" if use_close or ticker_type == "CRYPTO" else "Adj Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(data) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = data

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [self.portfolio_historical_prices, price_data], axis=1
                )
            else:
                console.print(f"Type {ticker_type} not supported.")

            p_bar.n += 1
            p_bar.refresh()

            # Fill missing values with last known price
            self.portfolio_historical_prices.fillna(method="ffill", inplace=True)

    @log_start_end(log=logger)
    def populate_historical_trade_data(self):
        """Create a new dataframe to store historical prices by ticker"""

        trade_data = self.__transactions.pivot_table(
            index="Date",
            columns=["Ticker"],
            values=[
                "Quantity",
                "Investment",
            ],
            aggfunc={"Quantity": np.sum, "Investment": np.sum},
        )

        # Make historical prices columns a multi-index. This helps the merging.
        self.portfolio_historical_prices.columns = pd.MultiIndex.from_product(
            [["Close"], self.portfolio_historical_prices.columns]
        )

        # Merge with historical close prices (and fillna)
        trade_data = pd.merge(
            trade_data,
            self.portfolio_historical_prices,
            how="outer",
            left_index=True,
            right_index=True,
        )

        trade_data["Close"] = trade_data["Close"].fillna(method="ffill")
        trade_data.fillna(0, inplace=True)

        # Accumulate quantity held by trade date
        trade_data["Quantity"] = trade_data["Quantity"].cumsum()

        trade_data["Investment"] = trade_data["Investment"].cumsum()

        trade_data.loc[:, ("Investment", "Total")] = trade_data["Investment"][
            self.tickers_list
        ].sum(axis=1)

        self.historical_trade_data = trade_data

    @log_start_end(log=logger)
    def calculate_value(self):
        """Calculate end of day value from historical data"""

        p_bar = tqdm(range(1), desc="       Calculating returns")

        trade_data = self.historical_trade_data

        # For each type [STOCK, ETF, etc] calculate value value by trade date
        # and add it to historical_trade_data

        # End Value
        for ticker_type, data in self.tickers.items():
            trade_data[pd.MultiIndex.from_product([["End Value"], data])] = (
                trade_data["Quantity"][data] * trade_data["Close"][data]
            )

        trade_data.loc[:, ("End Value", "Total")] = trade_data["End Value"][
            self.tickers_list
        ].sum(axis=1)

        self.portfolio_value = trade_data["End Value"]["Total"]

        for ticker_type, data in self.tickers.items():
            self.itemized_value[ticker_type] = trade_data["End Value"][data].sum(axis=1)

        trade_data[
            pd.MultiIndex.from_product(
                [["Initial Value"], self.tickers_list + ["Total"]]
            )
        ] = 0

        # Initial Value = Previous End Value + Investment changes
        trade_data["Initial Value"] = trade_data["End Value"].shift(1) + trade_data[
            "Investment"
        ].diff(periods=1)

        # Set first day Initial Value as the Investment (NaNs break first period)
        for t in self.tickers_list + ["Total"]:
            trade_data.at[trade_data.index[0], ("Initial Value", t)] = trade_data.iloc[
                0
            ]["Investment"][t]

        p_bar.n += 1
        p_bar.refresh()

        self.historical_trade_data = trade_data

    @log_start_end(log=logger)
    def set_risk_free_rate(self, risk_free_rate: float):
        """Sets risk free rate

        Parameters
        ----------
        risk_free_rate : float
            Risk free rate in float format
        """

        self.risk_free_rate = risk_free_rate

    @log_start_end(log=logger)
    def calculate_reserves(self):
        """Takes dividends into account for returns calculation"""
        # TODO: Add back cash dividends and deduct exchange costs
        console.print("Still has to be build.")

    @log_start_end(log=logger)
    def calculate_allocation(self, category: str, recalculate: bool = False):
        """Determine allocation based on Asset, Sector, Country or Region

        Parameters
        ----------
        category: str
            Chosen allocation category from Asset, Sector, Country or Region
        recalculate: bool
            Flag to force recalculate allocation if already exists
        """

        if category == "Asset":
            if (
                self.benchmark_assets_allocation.empty
                or self.portfolio_assets_allocation.empty
                or recalculate
            ):
                (
                    self.benchmark_assets_allocation,
                    self.portfolio_assets_allocation,
                ) = get_allocation(category, self.benchmark_info, self.portfolio_trades)
        elif category == "Sector":
            if (
                self.benchmark_sectors_allocation.empty
                or self.portfolio_sectors_allocation.empty
                or recalculate
            ):
                (
                    self.benchmark_sectors_allocation,
                    self.portfolio_sectors_allocation,
                ) = get_allocation(category, self.benchmark_info, self.portfolio_trades)
        elif category == "Country":
            if (
                self.benchmark_countries_allocation.empty
                or self.portfolio_countries_allocation.empty
                or recalculate
            ):
                (
                    self.benchmark_countries_allocation,
                    self.portfolio_countries_allocation,
                ) = get_allocation(category, self.benchmark_info, self.portfolio_trades)
        elif category == "Region":
            if (
                self.benchmark_regions_allocation.empty
                or self.portfolio_regions_allocation.empty
                or recalculate
            ):
                (
                    self.benchmark_regions_allocation,
                    self.portfolio_regions_allocation,
                ) = get_allocation(category, self.benchmark_info, self.portfolio_trades)
        else:
            console.print(
                "Category not available. Choose from: Asset, Sector, Country or Region"
            )


# Metrics
@log_start_end(log=logger)
def get_r2_score(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Method that retrieves R2 Score for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with R2 Score between portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.rsquare(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            round(
                r2_score(
                    portfolio_helper.filter_df_by_period(
                        portfolio_engine.returns, period
                    ),
                    portfolio_helper.filter_df_by_period(
                        portfolio_engine.benchmark_returns, period
                    ),
                ),
                3,
            )
        )
    return pd.DataFrame(vals, index=portfolio_helper.PERIODS, columns=["R2 Score"])


@log_start_end(log=logger)
def get_skewness(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Method that retrieves skewness for portfolio and benchmark selected

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.skew(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.returns, period
                        )
                    ),
                    3,
                ),
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )


@log_start_end(log=logger)
def get_kurtosis(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Method that retrieves kurtosis for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with kurtosis for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.kurtosis(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    scipy.stats.kurtosis(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.returns, period
                        )
                    ),
                    3,
                ),
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )


@log_start_end(log=logger)
def get_stats(portfolio_engine: PortfolioEngine, window: str = "all") -> pd.DataFrame:
    """Method that retrieves stats for portfolio and benchmark selected based on a certain interval

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all

    Returns
    -------
    pd.DataFrame
        DataFrame with overall stats for portfolio and benchmark for a certain period

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.stats(P)
    """

    df = (
        portfolio_helper.filter_df_by_period(portfolio_engine.returns, window)
        .describe()
        .to_frame()
        .join(
            portfolio_helper.filter_df_by_period(
                portfolio_engine.benchmark_returns, window
            ).describe()
        )
    )
    df.columns = ["Portfolio", "Benchmark"]
    return df


@log_start_end(log=logger)
def get_volatility(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Method that retrieves volatility for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with volatility for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.volatility(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        port_rets = portfolio_helper.filter_df_by_period(
            portfolio_engine.returns, period
        )
        bench_rets = portfolio_helper.filter_df_by_period(
            portfolio_engine.benchmark_returns, period
        )
        vals.append(
            [
                round(
                    100 * port_rets.std() * (len(port_rets) ** 0.5),
                    3,
                ),
                round(
                    100 * bench_rets.std() * (len(bench_rets) ** 0.5),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals,
        index=portfolio_helper.PERIODS,
        columns=["Portfolio [%]", "Benchmark [%]"],
    )


@log_start_end(log=logger)
def get_sharpe_ratio(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0
) -> pd.DataFrame:
    """Method that retrieves sharpe ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value

    Returns
    -------
    pd.DataFrame
        DataFrame with sharpe ratio for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.sharpe(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    portfolio_helper.sharpe_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
                round(
                    portfolio_helper.sharpe_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )


@log_start_end(log=logger)
def get_sortino_ratio(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0
) -> pd.DataFrame:
    """Method that retrieves sortino ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value

    Returns
    -------
    pd.DataFrame
        DataFrame with sortino ratio for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.sortino(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    portfolio_helper.sortino_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
                round(
                    portfolio_helper.sortino_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )


@log_start_end(log=logger)
def get_maximum_drawdown_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Method that retrieves maximum drawdown ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with maximum drawdown for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.maxdrawdown(P)
    """

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    portfolio_helper.maximum_drawdown(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.returns, period
                        )
                    ),
                    3,
                ),
                round(
                    portfolio_helper.maximum_drawdown(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )


@log_start_end(log=logger)
def get_gaintopain_ratio(portfolio_engine: PortfolioEngine):
    """Get Pain-to-Gain ratio based on historical data

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's gain-to-pain ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.gaintopain(P)
    """

    gtp_period_df = portfolio_helper.get_gaintopain_ratio(
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return gtp_period_df


@log_start_end(log=logger)
def get_tracking_error(portfolio_engine: PortfolioEngine, window: int = 252):
    """Get tracking error

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of tracking errors during different time windows
    pd.Series
        Series of rolling tracking error

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.trackerr(P)
    """

    trackr_period_df, trackr_rolling = portfolio_helper.get_tracking_error(
        portfolio_engine.returns, portfolio_engine.benchmark_returns, window
    )

    return trackr_period_df, trackr_rolling


@log_start_end(log=logger)
def get_information_ratio(portfolio_engine: PortfolioEngine):
    """Get information ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the information ratio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.information(P)
    """

    ir_period_df = portfolio_helper.get_information_ratio(
        portfolio_engine.returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return ir_period_df


@log_start_end(log=logger)
def get_tail_ratio(portfolio_engine: PortfolioEngine, window: int = 252):
    """Get tail ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time windows
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.tail(P)
    """

    tailr_period_df, portfolio_tr, benchmark_tr = portfolio_helper.get_tail_ratio(
        portfolio_engine.returns, portfolio_engine.benchmark_returns, window
    )

    return tailr_period_df, portfolio_tr, benchmark_tr


@log_start_end(log=logger)
def get_common_sense_ratio(portfolio_engine: PortfolioEngine):
    """Get common sense ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks common sense ratio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.commonsense(P)
    """

    csr_period_df = portfolio_helper.get_common_sense_ratio(
        portfolio_engine.returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return csr_period_df


@log_start_end(log=logger)
def get_jensens_alpha(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0, window: str = "1y"
):
    """Get jensen's alpha

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: str
        Interval used for rolling values
    risk_free_rate: float
        Risk free rate

    Returns
    -------
    pd.DataFrame
        DataFrame of jensens's alpha during different time windows
    pd.Series
        Series of jensens's alpha data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.jensens(P)
    """

    ja_period_df, ja_rolling = portfolio_helper.jensens_alpha(
        portfolio_engine.returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
        risk_free_rate,
        window,
    )

    return ja_period_df, ja_rolling


@log_start_end(log=logger)
def get_calmar_ratio(portfolio_engine: PortfolioEngine, window: int = 756):
    """Get calmar ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.calmar(P)
    """

    cr_period_df, cr_rolling = portfolio_helper.get_calmar_ratio(
        portfolio_engine.returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
        window,
    )

    return cr_period_df, cr_rolling


@log_start_end(log=logger)
def get_kelly_criterion(portfolio_engine: PortfolioEngine):
    """Gets kelly criterion

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of kelly criterion of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.kelly(P)
    """

    kc_period_df = portfolio_helper.get_kelly_criterion(
        portfolio_engine.returns, portfolio_engine.portfolio_trades
    )

    return kc_period_df


@log_start_end(log=logger)
def get_payoff_ratio(portfolio_engine: PortfolioEngine):
    """Gets payoff ratio

    Returns
    -------
    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.payoff(P)
    """

    pr_period_ratio = portfolio_helper.get_payoff_ratio(
        portfolio_engine.portfolio_trades
    )

    return pr_period_ratio


@log_start_end(log=logger)
def get_profit_factor(portfolio_engine: PortfolioEngine):
    """Gets profit factor

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.profitfactor(P)
    """

    pf_period_df = portfolio_helper.get_profit_factor(portfolio_engine.portfolio_trades)

    return pf_period_df


def get_holdings_value(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get holdings of assets (absolute value)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of holdings

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.holdv(P)
    """

    all_holdings = portfolio_engine.historical_trade_data["End Value"][
        portfolio_engine.tickers_list
    ]

    all_holdings["Total Value"] = all_holdings.sum(axis=1)
    # No need to account for time since this is daily data
    all_holdings.index = all_holdings.index.date

    return all_holdings


def get_holdings_percentage(
    portfolio_engine: PortfolioEngine,
):
    """Get holdings of assets (in percentage)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.holdp(P)
    """

    all_holdings = portfolio_engine.historical_trade_data["End Value"][
        portfolio_engine.tickers_list
    ]

    all_holdings = all_holdings.divide(all_holdings.sum(axis=1), axis=0) * 100

    # order it a bit more in terms of magnitude
    all_holdings = all_holdings[all_holdings.sum().sort_values(ascending=False).index]

    return all_holdings


@log_start_end(log=logger)
def get_maximum_drawdown(
    portfolio_engine: PortfolioEngine, is_returns: bool = False
) -> pd.Series:
    """Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum

    Parameters
    ----------
    data: pd.Series
        Series of input values
    is_returns: bool
        Flag to indicate inputs are returns

    Returns
    -------
    pd.Series
        Holdings series
    pd.Series
        Drawdown series

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.maxdd(P)
    """

    holdings: pd.Series = portfolio_engine.portfolio_value
    if is_returns:
        holdings = (1 + holdings).cumprod()

    rolling_max = holdings.cummax()
    drawdown = (holdings - rolling_max) / rolling_max

    return holdings, drawdown


def get_distribution_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
):
    """Display daily returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.distr(P)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    df = pd.DataFrame(portfolio_returns).join(pd.DataFrame(benchmark_returns))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


def get_rolling_volatility(
    portfolio_engine: PortfolioEngine, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling volatility

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        Rolling window size to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rvol(P)
    """

    portfolio_rvol = portfolio_helper.rolling_volatility(
        portfolio_engine.returns, window
    )
    if portfolio_rvol.empty:
        return pd.DataFrame()

    benchmark_rvol = portfolio_helper.rolling_volatility(
        portfolio_engine.benchmark_returns, window
    )
    if benchmark_rvol.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rvol).join(pd.DataFrame(benchmark_rvol))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


def get_rolling_sharpe(
    portfolio_engine: pd.DataFrame, risk_free_rate: float = 0, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling sharpe ratio

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate : float
        Risk free rate
    window : str
        Rolling window to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    Returns
    -------
    pd.DataFrame
        Rolling sharpe ratio DataFrame

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rsharpe(P)
    """

    portfolio_rsharpe = portfolio_helper.rolling_sharpe(
        portfolio_engine.returns, risk_free_rate, window
    )
    if portfolio_rsharpe.empty:
        return pd.DataFrame()

    benchmark_rsharpe = portfolio_helper.rolling_sharpe(
        portfolio_engine.benchmark_returns, risk_free_rate, window
    )
    if benchmark_rsharpe.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rsharpe).join(pd.DataFrame(benchmark_rsharpe))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


def get_rolling_sortino(
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = "1y",
) -> pd.DataFrame:
    """Get rolling sortino

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations

    Returns
    -------
    pd.DataFrame
        Rolling sortino ratio DataFrame

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rsortino(P)
    """

    portfolio_rsortino = portfolio_helper.rolling_sortino(
        portfolio_engine.returns, risk_free_rate, window
    )
    if portfolio_rsortino.empty:
        return pd.DataFrame()

    benchmark_rsortino = portfolio_helper.rolling_sortino(
        portfolio_engine.benchmark_returns, risk_free_rate, window
    )
    if benchmark_rsortino.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rsortino).join(pd.DataFrame(benchmark_rsortino))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


@log_start_end(log=logger)
def get_rolling_beta(
    portfolio_engine: PortfolioEngine,
    window: str = "1y",
) -> pd.DataFrame:
    """Get rolling beta using portfolio and benchmark returns

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    window: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rbeta(P)
    """

    df = portfolio_helper.rolling_beta(
        portfolio_engine.returns, portfolio_engine.benchmark_returns, window
    )

    return df


@log_start_end(log=logger)
def get_performance_vs_benchmark(
    portfolio_engine: PortfolioEngine,
    show_all_trades: bool = False,
) -> pd.DataFrame:

    """Get portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio performance vs the benchmark

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.perf(P)
    """

    portfolio_trades = portfolio_engine.portfolio_trades
    benchmark_trades = portfolio_engine.benchmark_trades

    portfolio_trades.index = pd.to_datetime(portfolio_trades["Date"].values)
    benchmark_trades.index = pd.to_datetime(benchmark_trades["Date"].values)

    if show_all_trades:
        # Combine DataFrames
        combined = pd.concat(
            [
                portfolio_trades[
                    ["Date", "Ticker", "Portfolio Value", "Portfolio % Return"]
                ],
                benchmark_trades[["Benchmark Value", "Benchmark % Return"]],
            ],
            axis=1,
        )

        # Calculate alpha
        combined["Alpha"] = (
            combined["Portfolio % Return"] - combined["Benchmark % Return"]
        )

        combined["Date"] = pd.to_datetime(combined["Date"]).dt.date

        return combined

    # Calculate total value and return
    total_investment_difference = (
        portfolio_trades["Portfolio Investment"].sum()
        - benchmark_trades["Benchmark Investment"].sum()
    )
    total_value_difference = (
        portfolio_trades["Portfolio Value"].sum()
        - benchmark_trades["Benchmark Value"].sum()
    )
    total_portfolio_return = (
        portfolio_trades["Portfolio Value"].sum()
        / portfolio_trades["Portfolio Investment"].sum()
    ) - 1
    total_benchmark_return = (
        benchmark_trades["Benchmark Value"].sum()
        / benchmark_trades["Benchmark Investment"].sum()
    ) - 1
    total_abs_return_difference = (
        portfolio_trades["Portfolio Value"].sum()
        - portfolio_trades["Portfolio Investment"].sum()
    ) - (
        benchmark_trades["Benchmark Value"].sum()
        - benchmark_trades["Benchmark Investment"].sum()
    )

    totals = pd.DataFrame.from_dict(
        {
            "Total Investment": [
                portfolio_trades["Portfolio Investment"].sum(),
                benchmark_trades["Benchmark Investment"].sum(),
                total_investment_difference,
            ],
            "Total Value": [
                portfolio_trades["Portfolio Value"].sum(),
                benchmark_trades["Benchmark Value"].sum(),
                total_value_difference,
            ],
            "Total % Return": [
                f"{total_portfolio_return:.2%}",
                f"{total_benchmark_return:.2%}",
                f"{total_portfolio_return - total_benchmark_return:.2%}",
            ],
            "Total Abs Return": [
                portfolio_trades["Portfolio Value"].sum()
                - portfolio_trades["Portfolio Investment"].sum(),
                benchmark_trades["Benchmark Value"].sum()
                - benchmark_trades["Benchmark Investment"].sum(),
                total_abs_return_difference,
            ],
        },
        orient="index",
        columns=["Portfolio", "Benchmark", "Difference"],
    )

    return totals.replace(0, "-")


@log_start_end(log=logger)
def get_var(
    portfolio_engine: PortfolioEngine,
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
) -> pd.DataFrame:

    """Get portfolio VaR

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean: bool
        if one should use the data mean return
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: float
        var percentile (%)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio VaR

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.var(P)
    """

    return qa_model.get_var(
        data=portfolio_engine.returns,
        use_mean=use_mean,
        adjusted_var=adjusted_var,
        student_t=student_t,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def get_es(
    portfolio_engine: PortfolioEngine,
    use_mean: bool = False,
    distribution: str = "normal",
    percentile: float = 99.9,
) -> pd.DataFrame:
    """Get portfolio expected shortfall

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean:
        if one should use the data mean return
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: float
        es percentile (%)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio expected shortfall

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.es(P)
    """

    return qa_model.get_es(
        data=portfolio_engine.returns,
        use_mean=use_mean,
        distribution=distribution,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def get_omega(
    portfolio_engine: PortfolioEngine,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
) -> pd.DataFrame:
    """Get omega ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio omega ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.om(P)
    """

    return qa_model.get_omega(
        data=portfolio_engine.returns,
        threshold_start=threshold_start,
        threshold_end=threshold_end,
    )


def get_summary(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    risk_free_rate: float = 0,
) -> pd.DataFrame:
    """Get portfolio and benchmark returns summary

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio and benchmark returns summary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.summary(P)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    metrics = {
        "Volatility": [portfolio_returns.std(), benchmark_returns.std()],
        "Skew": [
            scipy.stats.skew(portfolio_returns),
            scipy.stats.skew(benchmark_returns),
        ],
        "Kurtosis": [
            scipy.stats.kurtosis(portfolio_returns),
            scipy.stats.kurtosis(benchmark_returns),
        ],
        "Maximum Drawdown": [
            portfolio_helper.maximum_drawdown(portfolio_returns),
            portfolio_helper.maximum_drawdown(benchmark_returns),
        ],
        "Sharpe ratio": [
            portfolio_helper.sharpe_ratio(portfolio_returns, risk_free_rate),
            portfolio_helper.sharpe_ratio(benchmark_returns, risk_free_rate),
        ],
        "Sortino ratio": [
            portfolio_helper.sortino_ratio(portfolio_returns, risk_free_rate),
            portfolio_helper.sortino_ratio(benchmark_returns, risk_free_rate),
        ],
        "R2 Score": [
            r2_score(portfolio_returns, benchmark_returns),
            r2_score(portfolio_returns, benchmark_returns),
        ],
    }

    summary = pd.DataFrame(
        metrics.values(), index=metrics.keys(), columns=["Portfolio", "Benchmark"]
    )
    summary["Difference"] = summary["Portfolio"] - summary["Benchmark"]
    summary.loc["Volatility"] = summary.loc["Volatility"].apply("{:.2%}".format)
    summary.loc["Maximum Drawdown"] = summary.loc["Maximum Drawdown"].apply(
        "{:.2%}".format
    )
    summary.loc["R2 Score"] = summary.loc["R2 Score"].apply("{:.2%}".format)

    return summary


@log_start_end(log=logger)
def get_yearly_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Get yearly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with yearly returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.yret(P)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    creturns_year_val = list()
    breturns_year_val = list()

    for year in sorted(set(portfolio_returns.index.year)):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        cumulative_returns = 100 * portfolio_helper.cumulative_returns(creturns_year)
        creturns_year_val.append(cumulative_returns.values[-1])

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        benchmark_c_returns = 100 * portfolio_helper.cumulative_returns(breturns_year)
        breturns_year_val.append(benchmark_c_returns.values[-1])

    df = pd.DataFrame(
        {
            "Portfolio": pd.Series(
                creturns_year_val, index=list(set(portfolio_returns.index.year))
            ),
            "Benchmark": pd.Series(
                breturns_year_val, index=list(set(portfolio_returns.index.year))
            ),
            "Difference": pd.Series(
                np.array(creturns_year_val) - np.array(breturns_year_val),
                index=list(set(portfolio_returns.index.year)),
            ),
        }
    )

    return df


@log_start_end(log=logger)
def get_monthly_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Get monthly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with monthly returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.mret(P)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    creturns_month_val = list()
    breturns_month_val = list()

    for year in sorted(list(set(portfolio_returns.index.year))):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        creturns_val = list()
        for i in range(1, 13):
            creturns_year_month = creturns_year[creturns_year.index.month == i]
            creturns_year_month_val = 100 * portfolio_helper.cumulative_returns(
                creturns_year_month
            )

            if creturns_year_month.empty:
                creturns_val.append(0)
            else:
                creturns_val.append(creturns_year_month_val.values[-1])
        creturns_month_val.append(creturns_val)

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        breturns_val = list()
        for i in range(1, 13):
            breturns_year_month = breturns_year[breturns_year.index.month == i]
            breturns_year_month_val = 100 * portfolio_helper.cumulative_returns(
                breturns_year_month
            )

            if breturns_year_month.empty:
                breturns_val.append(0)
            else:
                breturns_val.append(breturns_year_month_val.values[-1])
        breturns_month_val.append(breturns_val)

    monthly_returns = pd.DataFrame(
        creturns_month_val,
        index=sorted(list(set(portfolio_returns.index.year))),
        columns=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )
    bench_monthly_returns = pd.DataFrame(
        breturns_month_val,
        index=sorted(list(set(benchmark_returns.index.year))),
        columns=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )

    return monthly_returns, bench_monthly_returns


@log_start_end(log=logger)
def get_daily_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Get daily returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with daily returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.dret(P)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    df = portfolio_returns.to_frame()
    df = df.join(benchmark_returns)
    df.index = df.index.date
    df.columns = ["portfolio", "benchmark"]

    return df


@log_start_end(log=logger)
def generate_portfolio(
    transactions_file_path: str,
    benchmark_symbol: str = "SPY",
    full_shares: bool = False,
    risk_free_rate: float = 0,
) -> PortfolioEngine:
    """Get PortfolioEngine object

    Parameters
    ----------
    transactions_file_path : str
        Path to transactions file
    benchmark_symbol : str
        Benchmark ticker to download data
    full_shares : bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number
    risk_free_rate : float
        Risk free rate in float format

    Returns
    -------
    PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    """

    transactions = PortfolioEngine.read_transactions(transactions_file_path)
    portfolio_engine = PortfolioEngine(transactions)
    portfolio_engine.generate_portfolio_data()
    portfolio_engine.set_benchmark(symbol=benchmark_symbol, full_shares=full_shares)
    portfolio_engine.set_risk_free_rate(risk_free_rate)

    return portfolio_engine


@log_start_end(log=logger)
def get_transactions(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get portfolio transactions

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object

    Returns
    -------
    pd.DataFrame
        Portfolio transactions

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.show(P)
    """

    return portfolio_engine.get_transactions()


@log_start_end(log=logger)
def set_benchmark(
    portfolio_engine: PortfolioEngine, symbol: str, full_shares: bool = False
):
    """Load benchmark into portfolio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object
    symbol: str
        Benchmark symbol to download data
    full_shares: bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.bench(P, symbol="SPY")
    """

    portfolio_engine.set_benchmark(symbol=symbol, full_shares=full_shares)


@log_start_end(log=logger)
def set_risk_free_rate(portfolio_engine: PortfolioEngine, risk_free_rate: float):
    """Set risk-free rate

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object
    risk_free_rate: float
        Risk free rate in float format
    """

    portfolio_engine.set_risk_free_rate(risk_free_rate=risk_free_rate)


def join_allocation(
    portfolio: pd.DataFrame, benchmark: pd.DataFrame, column: str
) -> pd.DataFrame:
    """Helper method to join portfolio and benchmark allocation by column

    Parameters
    ----------
    portfolio: pd.DataFrame
        Portfolio allocation
    benchmark: pd.DataFrame
        Benchmark allocation
    column: str
        Column to join DataFrames

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio and benchmark allocations
    """
    combined = pd.merge(portfolio, benchmark, on=column, how="left")
    combined["Difference"] = combined["Portfolio"] - combined["Benchmark"]
    combined = combined.replace(np.nan, "-")
    combined = combined.replace(0, "-")

    return combined


@log_start_end(log=logger)
def get_assets_allocation(
    portfolio_engine: PortfolioEngine,
    tables: bool = False,
    limit: int = 10,
    recalculate: bool = False,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
    """Display portfolio asset allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.alloc.assets(P)
    """

    portfolio_engine.calculate_allocation(category="Asset", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_assets_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_assets_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Symbol")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_sectors_allocation(
    portfolio_engine=None,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio sector allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.alloc.sectors(P)
    """

    portfolio_engine.calculate_allocation(category="Sector", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_sectors_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_sectors_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Sector")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_countries_allocation(
    portfolio_engine=None,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio country allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.alloc.countries(P)
    """

    portfolio_engine.calculate_allocation(category="Country", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_countries_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_countries_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Country")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_regions_allocation(
    portfolio_engine=None,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio region allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.alloc.regions(P)
    """

    portfolio_engine.calculate_allocation(category="Region", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_regions_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_regions_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Region")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


# Old code
@log_start_end(log=logger)
def get_main_text(data: pd.DataFrame) -> str:
    """Get main performance summary from a dataframe with market returns

    Parameters
    ----------
    data : pd.DataFrame
        Stock holdings and returns with market returns

    Returns
    ----------
    text : str
        The main summary of performance
    """
    d_debt = np.where(data[("Cash", "Cash")] > 0, 0, 1)
    bcash = 0 if data[("Cash", "Cash")][0] > 0 else abs(data[("Cash", "Cash")][0])
    ecash = 0 if data[("Cash", "Cash")][-1] > 0 else abs(data[("Cash", "Cash")][-1])
    bdte = bcash / (data["holdings"][0] - bcash)
    edte = ecash / (data["holdings"][-1] - ecash)
    if sum(d_debt) > 0:
        t_debt = (
            f"Beginning debt to equity was {bdte:.2%} and ending debt to equity was"
            f" {edte:.2%}. Debt adds risk to a portfolio by amplifying the gains and losses when"
            " equities change in value."
        )
        if bdte > 1 or edte > 1:
            t_debt += " Debt to equity ratios above one represent a significant amount of risk."
    else:
        t_debt = (
            "Margin was not used this year. This reduces this risk of the portfolio."
        )
    text = (
        f"Your portfolio's performance for the period was {data['return'][-1]:.2%}. This was"
        f" {'greater' if data['return'][-1] > data[('Market', 'Return')][-1] else 'less'} than"
        f" the market return of {data[('Market', 'Return')][-1]:.2%}. The variance for the"
        f" portfolio is {np.var(data['return']):.2%}, while the variance for the market was"
        f" {np.var(data[('Market', 'Return')]):.2%}. {t_debt} The following report details"
        f" various analytics from the portfolio. Read below to see the moving beta for a"
        f" stock."
    )
    return text


@log_start_end(log=logger)
def get_beta_text(data: pd.DataFrame) -> str:
    """Get beta summary for a stock from a dataframe

    Parameters
    ----------
    data : pd.DataFrame
        The beta history of the stock

    Returns
    ----------
    text : str
        The beta history for a ticker
    """
    betas = data[list(filter(lambda score: "beta" in score, list(data.columns)))]
    high = betas.idxmax(axis=1)
    low = betas.idxmin(axis=1)
    text = (
        "Beta is how strongly a portfolio's movements correlate with the market's movements."
        " A stock with a high beta is considered to be riskier. The beginning beta for the period"
        f" was {portfolio_helper.beta_word(data['total'][0])} at {data['total'][0]:.2f}. This went"
        f" {'up' if data['total'][-1] > data['total'][0] else 'down'} to"
        f" {portfolio_helper.beta_word(data['total'][-1])} at {data['total'][-1]:.2f} by the end"
        f" of the period. The ending beta was pulled {'up' if data['total'][-1] > 1 else 'down'} by"
        f" {portfolio_helper.clean_name(high[-1] if data['total'][-1] > 1 else low[-1])}, which had"
        f" an ending beta of {data[high[-1]][-1] if data['total'][-1] > 1 else data[low[-1]][-1]:.2f}."
    )
    return text


performance_text = (
    "The Sharpe ratio is a measure of reward to total volatility. A Sharpe ratio above one is"
    " considered acceptable. The Treynor ratio is a measure of systematic risk to reward."
    " Alpha is the average return above what CAPM predicts. This measure should be above zero"
    ". The information ratio is the excess return on systematic risk. An information ratio of"
    " 0.4 to 0.6 is considered good."
)
