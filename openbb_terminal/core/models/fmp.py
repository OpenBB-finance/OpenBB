import pandas as pd
from pydantic import BaseModel

from openbb_terminal.helper_funcs import request

#pylint: disable=too-many-lines

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
        # return cfg.API_KEY_FINANCIALMODELINGPREP
        return "THIS_ISNT_OUR_KEY"

    # TODO: add request validation method

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
        return pd.DataFrame(r.json()).T

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
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
            Historical ker ratios

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
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
        return pd.DataFrame(r.json()).T

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
        r = request(url + "&structure=flat&apikey={cls._KEY()}")
        return r.json()

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
        r = request(url + "&structure=flat&apikey={cls._KEY()}")
        return r.json()

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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json())

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
        >>> esg = openbb.stocks.fa.esg("AAPL")
        >>> esg_scores = esg[["date", "environmentScore", "socialScore", "governanceScore"]]
        """
        url = (
            f"{cls._V4_URL()}esg-environmental-social-governance-data/?symbol={symbol}"
        )
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json())

    @classmethod
    def price_target(cls, symbol: str) -> pd.DataFrame:
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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json()).T

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
        >>> up_down = openbb.fmp.updowngrade("AAPL")
        """
        url = f"{cls._V4_URL()}upgrades-downgrades/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json()["historical"])

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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json())

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
        return pd.DataFrame(r.json()["historical"])

    @classmethod
    def eod_prices(cls, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Get end of day prices for company

        Parameters
        ----------
        symbol : str
            Symbol to get data for
        start : str
            Start date in YYYY-MM-DD format
        end : str
            End date in YYYY-MM-DD format

        Returns
        -------
        pd.DataFrame
            DataFrame of eod prices

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> price_df = openbb.fmp.prices("AAPL")
        """
        url = f"{cls._BASE_URL()}historical-price-full/{symbol}?from={start}&to={end}"
        r = request(url + f"&apikey={cls._KEY()}")
        return pd.DataFrame(r.json()["historical"])
