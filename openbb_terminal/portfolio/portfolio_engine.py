"""Portfolio Engine"""
__docformat__ = "numpy"

import contextlib
import logging
from typing import Dict, Any
import datetime

import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.portfolio.portfolio_helper import (
    make_equal_length,
    get_info_from_ticker,
)
from openbb_terminal.portfolio.allocation_model import get_allocation

# pylint: disable=E1136,W0201,R0902,C0302
# pylint: disable=unsupported-assignment-operation,redefined-outer-name,too-many-public-methods, consider-using-f-string

logger = logging.getLogger(__name__)

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
        pd.DataFrame
            Formatted transactions
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
        """Read static method to read transactions from file.

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
        """Preprocess, format and compute auxiliary fields.

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
        """Load populate company data for stocks such as sector, industry and country"""

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
                        info_list = get_info_from_ticker(ticker)

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
        ) = make_equal_length(self.returns, self.benchmark_returns)

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
        """Generate portfolio data from transactions"""

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
        """Load historical adj close/close prices for tickers in list of trades

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
        """Set risk free rate

        Parameters
        ----------
        risk_free_rate : float
            Risk free rate in float format
        """

        self.risk_free_rate = risk_free_rate

    @log_start_end(log=logger)
    def calculate_reserves(self):
        """Take dividends into account for returns calculation"""
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
