from typing import Dict, List

import pandas as pd
import requests
from pydantic import BaseModel

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import request

# pylint: disable=too-many-public-methods


class FMP(BaseModel):
    """OpenBB Integration for Financial Modeling Prep"""

    def __repr__(self):
        return "OpenBB Integration for FMP"

    @classmethod
    def _BASE_URL(cls) -> str:
        """Returns the v3 url"""
        return "https://financialmodelingprep.com/api/v3/"

    @classmethod
    def _V4_URL(cls) -> str:
        """Returns the v4 url"""
        return "https://financialmodelingprep.com/api/v4/"

    @classmethod
    def _KEY(cls) -> str:
        """Returns the api key"""
        return get_current_user().credentials.API_KEY_FINANCIALMODELINGPREP

    @classmethod
    def _QUARTERS(cls) -> Dict[str, str]:
        quarters = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31"}
        return quarters

    @classmethod
    def validate_request(cls, response: requests.models.Response) -> dict:
        """Validate request

        Parameters
        ----------
        request : requests.models.Response
            Request to validate

        Returns
        -------
        dict
            JSON response of request
        """
        if response.status_code != 200:
            print("Error: ", response.status_code)
            return {}
        response_json = response.json()
        if "Error Message" in response_json:
            print("Error: ", response_json["Error Message"])
            return {}
        if not response_json:
            print("Error: No data returned")
            return {}
        return response_json

    @classmethod
    def income(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        """Get historical income statement data

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Income statement dataframe with columns as the reported dates

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> quarterly_income_statement = openbb.fmp.income("AAPL", quarter=True)
        """
        if quarter:
            url = (
                f"{cls._BASE_URL()}income-statement-as-reported/{symbol}?period=quarter"
            )
        else:
            url = f"{cls._BASE_URL()}income-statement-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def balance(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        """Get historical balance sheet data

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Balance sheet dataframe with columns as the reported dates

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> quarterly_balance_sheet = openbb.fmp.balance("AAPL", quarter=True)
        """
        if quarter:
            url = f"{cls._BASE_URL()}balance-sheet-statement-as-reported/{symbol}?period=quarter"
        else:
            url = f"{cls._BASE_URL()}balance-sheet-statement-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + f"&apikey={cls._KEY()}")
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def cash_flow(cls, symbol: str, quarter: bool = False, limit=200) -> pd.DataFrame:
        """Get historical cash flow data

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Cash Flow dataframe with columns as the reported dates

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> annual_cash_flow = openbb.fmp.cash("AAPL", quarter=False)
        """
        if quarter:
            url = f"{cls._BASE_URL()}cash-flow-statement-as-reported/{symbol}?period=quarter"
        else:
            url = f"{cls._BASE_URL()}cash-flow-statement-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def full_statement(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        """Get historical full financial statement as reported

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Historical statement dataframe with columns as the reported dates

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> statements = openbb.fmp.statements("AAPL")
        """
        if quarter:
            url = f"{cls._BASE_URL()}financial-statement-full-as-reported/{symbol}?period=quarter"
        else:
            url = f"{cls._BASE_URL()}financial-statement-full-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def key_metrics(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        """Get historical key metrics

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Historical key ratios

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> key_ratios = openbb.fmp.key("AAPL")
        """
        if quarter:
            url = f"{cls._BASE_URL()}key-metrics/{symbol}?period=quarter&"
        else:
            url = f"{cls._BASE_URL()}key-metrics/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def ratios(cls, symbol: str, quarter=True, limit: int = 200) -> pd.DataFrame:
        """Get historical ratios

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Historical ratios

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> ratios = openbb.fmp.ratios("AAPL")
        """
        url = (
            f"{cls._BASE_URL()}ratios/{symbol}?period=quarter&"
            if quarter
            else f"{cls._BASE_URL()}ratios/{symbol}?"
        )
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def income_growth(cls, symbol: str, limit: int = 200) -> pd.DataFrame:
        """Get historical income statement growth

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Historical income statement growth

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> income_growth = openbb.fmp.income_growth("AAPL")
        """
        url = f"{cls._BASE_URL()}income-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        df = (
            pd.DataFrame(cls.validate_request(r))
            .drop(columns=["symbol", "period"])
            .set_index("date")
        )
        return df.T

    @classmethod
    def balance_growth(cls, symbol: str, limit: int = 200) -> pd.DataFrame:
        """Get historical balance sheet growth

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Dataframe of historical balance sheet growth

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> balance_growth = openbb.fmp.balance_growth("AAPL")
        """
        url = f"{cls._BASE_URL()}balance-sheet-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def cash_flow_growth(cls, symbol: str, limit: int = 00) -> pd.DataFrame:
        """Get historical cash flow growth

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Dataframe of historical cash flow growth

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> cash_growth = openbb.fmp.cash_growth("AAPL")
        """
        url = f"{cls._BASE_URL()}cash-flow-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def revseg(cls, symbol: str, quarter=False) -> dict:
        """Get sales revenue by segment

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False

        Returns
        -------
        dict
            Dictionary containing the revenue by segment

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> revseg = openbb.fmp.revseg("AAPL")
        """
        # TODO: make dataframe since this is not a fixed shape
        if quarter:
            url = f"{cls._V4_URL()}revenue-product-segmentation/?symbol={symbol}&period=quarter"
        else:
            url = f"{cls._V4_URL()}revenue-product-segmentation/?symbol={symbol}"
        r = request(url + f"&structure=flat&apikey={cls._KEY()}")
        return cls.validate_request(r)

    @classmethod
    def revgeo(cls, symbol: str, quarter=False) -> dict:
        """Get sales revenue by geography

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        quarter : bool, optional
            Flag to get quarterly data, by default False

        Returns
        -------
        dict
            Dictionary containing the revenue by geography

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> revseg = openbb.fmp.revseg("AAPL")
        """
        # TODO same as above
        if quarter:
            url = f"{cls._V4_URL()}revenue-geographic-segmentation/?symbol={symbol}&period=quarter"
        else:
            url = f"{cls._V4_URL()}revenue-geographic-segmentation/?symbol={symbol}"
        r = request(url + f"&structure=flat&apikey={cls._KEY()}")
        return cls.validate_request(r)

    @classmethod
    def key_execs(cls, symbol: str) -> pd.DataFrame:
        """Get key executives from company

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of key executives

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> execs = openbb.fmp.key_execs("AAPL")
        """
        url = f"{cls._BASE_URL()}key-executives/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def insider(cls, symbol: str) -> pd.DataFrame:
        """Get insider trading data

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of insider trading data

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> insider = openbb.fmp.insider("AAPL")
        """
        url = f"{cls._V4_URL()}insider-trading/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def esg(cls, symbol: str) -> pd.DataFrame:
        """Get ESG data from symbol

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            Dataframe of ESG data.

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> esg = openbb.fmp.esg("AAPL")
        >>> esg_scores = esg[["date", "environmentalScore", "socialScore", "governanceScore","ESGScore"]]
        """
        url = (
            f"{cls._V4_URL()}esg-environmental-social-governance-data/?symbol={symbol}"
        )
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def institutional(cls, symbol: str) -> pd.DataFrame:
        """Get institutional ownership data

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of institutional ownership data

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> ownership = openbb.fmp.institutional("AAPL")
        """

        url = (
            f"{cls._V4_URL()}institutional-ownership/symbol-ownership/?symbol={symbol}"
        )
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def institutional_holders(
        cls, symbol: str, quarter: str = "Q4", year: int = 2022
    ) -> pd.DataFrame:
        """Get institutional ownership data at a given quarter

        Parameters
        ----------
        symbol : str
            Symbol to get data for


        Returns
        -------
        pd.DataFrame
            DataFrame of institutional ownership data

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> holders = openbb.fmp.institutional_holders("AAPL")
        """
        date = f"{year}-{cls._QUARTERS()[quarter]}"
        url = f"{cls._V4_URL()}institutional-ownership/institutional-holders/symbol-ownership-percent?date={date}&symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def price_targets(cls, symbol: str) -> pd.DataFrame:
        """Get price targets for a company

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of price targets

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> pt = openbb.fmp.price_targets("AAPL")
        """
        url = f"{cls._V4_URL()}price-target/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def price_target_summary(cls, symbol: str) -> pd.DataFrame:
        """Get price target summary for a company

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of price target summary

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> summary_pt = openbb.fmp.pt_summary("AAPL")
        """
        url = f"{cls._V4_URL()}price-target-summary/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)).T

    @classmethod
    def upgrade_downgrade(cls, symbol: str) -> pd.DataFrame:
        """Get upgrades and downgrades for a company

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of upgrades and downgrades

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> up_down = openbb.fmp.upgradedowngrade("AAPL")
        """
        url = f"{cls._V4_URL()}upgrades-downgrades/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def news(cls, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Get news for a company

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        limit : int, optional
            Number of articles to get, by default 100

        Returns
        -------
        pd.DataFrame
            DataFrame of news

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> news = openbb.fmp.news("AAPL")
        """
        url = f"{cls._BASE_URL()}stock_news/?tickers={symbol}&limit={limit}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def divcal(cls, symbol: str) -> pd.DataFrame:
        """Get company dividend calendar

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of dividend calendar

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> divs = openbb.fmp.divcal("AAPL")
        """
        url = f"{cls._BASE_URL()}historical-price-full/stock_dividend/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)["historical"])

    @classmethod
    def earnings(cls, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Get upgrades and downgrades for a company

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        limit : int, optional
            Number of previous earnings to get by default 100

        Returns
        -------
        pd.DataFrame
            DataFrame of earnings

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> earnings = openbb.fmp.earnings("AAPL")
        """
        url = f"{cls._BASE_URL()}historical/earning_calendar/{symbol}?limit={limit}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def ftd(cls, symbol: str) -> pd.DataFrame:
        """Get company ftds

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of ftds

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> ftds = openbb.fmp.ftd("AAPL")
        """
        url = f"{cls._V4_URL()}/fail_to_deliver/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def senate_trading(cls, symbol: str) -> pd.DataFrame:
        """Get company senate trading

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of senate trading

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> senate = openbb.fmp.senate("AAPL")
        """
        url = f"{cls._V4_URL()}/senate-trading/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def splits(cls, symbol: str) -> pd.DataFrame:
        """Get company splits

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of historical splits

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> splits = openbb.fmp.splits("AAPL")
        """
        url = f"{cls._BASE_URL()}historical-price-full/stock_split/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r)["historical"])

    @classmethod
    def eod_prices(cls, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get end of day prices for company

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        start_date : str
            Start date in YYYY-MM-DD format
        end_date : str
            End date in YYYY-MM-DD format

        Returns
        -------
        pd.DataFrame
            DataFrame of eod prices

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> price_df = openbb.fmp.prices("AAPL", start_date="2022-01-01", end_date="2023-01-31")
        """
        url = f"{cls._BASE_URL()}historical-price-full/{symbol}?from={start_date}&to={end_date}"
        r = request(url + f"&apikey={cls._KEY()}")
        response = cls.validate_request(r)
        if response:
            return pd.DataFrame(response.get("historical", {}))
        return pd.DataFrame()

    @classmethod
    def marketcap(cls, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical marketcap

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        start_date : str
            Start date in YYYY-MM-DD format
        end_date : str
            End date in YYYY-MM-DD format

        Returns
        -------
        pd.DataFrame
            DataFrame of historical marketcap

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> mktcap = openbb.fmp.marketcap("AAPL", start_date="2022-01-01", end_date="2023-01-31")
        """
        url = f"{cls._BASE_URL()}historical-market-capitalization/{symbol}"
        r = request(url + f"?apikey={cls._KEY()}")
        df = pd.DataFrame(cls.validate_request(r))
        df = df[(df.date >= start_date) & (df.date <= end_date)].reset_index(drop=True)
        return df

    @classmethod
    def peers(cls, symbol: str) -> List[str]:
        """Get company peers

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        List[str]
            List of company peers

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> peers_list = openbb.fmp.peers("AAPL")
        """
        url = f"{cls._V4_URL()}stock_peers?symbol={symbol}"
        r = request(url + f"&apikey={cls._KEY()}")
        peers = cls.validate_request(r)
        if peers:
            return peers[0].get("peersList", [])
        return []

    @classmethod
    def market_risk_premium(cls) -> pd.DataFrame:
        """Get market risk premium

        Returns
        -------
        pd.DataFrame
            DataFrame of market risk premium

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> premiums = openbb.fmp.market_risk_premium()
        """
        url = f"{cls._V4_URL()}/market_risk_premium"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def executive_compensation(cls, symbol: str) -> pd.DataFrame:
        """Get executive compensation

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of executive compensation

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> executive_compensation = openbb.fmp.exec_comp("AAPL")
        """
        url = f"{cls._V4_URL()}governance/executive_compensation?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def company_notes(cls, symbol: str) -> pd.DataFrame:
        """Get company notes

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of company notes

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> notes = openbb.fmp.notes("AAPL")
        """
        url = f"{cls._V4_URL()}company-notes?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def sp500_companies(cls) -> pd.DataFrame:
        """Get S&P 500 companies

        Returns
        -------
        pd.DataFrame
            DataFrame of S&P 500 companies

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> sp500 = openbb.fmp.sp500_companies()
        """
        url = f"{cls._BASE_URL()}sp500_constituent"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def dow_companies(cls) -> pd.DataFrame:
        """Get Dow Jones companies

        Returns
        -------
        pd.DataFrame
            DataFrame of Dow Jones companies

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> dow = openbb.fmp.dow_companies()
        """
        url = f"{cls._BASE_URL()}dowjones_constituent"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def all_symbols(cls) -> pd.DataFrame:
        """Get all symbols

        Returns
        -------
        pd.DataFrame
            DataFrame of all symbols

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> symbols = openbb.fmp.all_symbols()
        """
        url = f"{cls._BASE_URL()}stock/list"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def sectors_pe_ratios(cls, date: str) -> pd.DataFrame:
        """Get sectors PE ratios

        Parameters
        ----------
        date: str
            Date to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of sectors PE ratios

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> sectors = openbb.fmp.sectors_pe(date="2023-03-03")
        """
        url = f"{cls._V4_URL()}sector_price_earning_ratio?date={date}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def industry_pe_ratios(cls, date: str) -> pd.DataFrame:
        """Get industry PE ratios

        Parameters
        ----------
        date: str
            Date to get data for

        Returns
        -------
        pd.DataFrame
            DataFrame of sectors PE ratios

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> sectors = openbb.fmp.industry_pe(date="2023-03-03")
        """
        url = f"{cls._V4_URL()}industry_price_earning_ratio?date={date}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def sector_performance(cls) -> pd.DataFrame:
        """Get sector performance

        Returns
        -------
        pd.DataFrame
            DataFrame of sector performance

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> sectors = openbb.fmp.sector_performance()
        """
        url = f"{cls._BASE_URL()}sector-performance"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def most_active(cls) -> pd.DataFrame:
        """Get most active stocks

        Returns
        -------
        pd.DataFrame
            DataFrame of most active stocks

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> most_active = openbb.fmp.active()
        """
        url = f"{cls._BASE_URL()}stock_market/actives"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def gainers(cls) -> pd.DataFrame:
        """Get top gainers

        Returns
        -------
        pd.DataFrame
            DataFrame of top gainers

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> top_gainers = openbb.fmp.gainers()
        """
        url = f"{cls._BASE_URL()}gainers"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def losers(cls) -> pd.DataFrame:
        """Get top losers

        Returns
        -------
        pd.DataFrame
            DataFrame of top losers

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> top_losers = openbb.fmp.losers()
        """
        url = f"{cls._BASE_URL()}losers"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))

    @classmethod
    def scores(cls, symbol: str) -> pd.DataFrame:
        """Get stock financial scores

        Parameters
        ----------
        symbol : str
            Symbol to get data for

        Returns
        -------
        pd.DataFrame
            Dataframe of financial scores

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> top_losers = openbb.fmp.scores("AAPL")
        """
        url = f"{cls._V4_URL()}score?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(cls.validate_request(r))
