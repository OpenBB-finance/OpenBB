import pandas as pd
from pydantic import BaseModel

from openbb_terminal.helper_funcs import request


class FMP(BaseModel):
    # key: str = cfg.API_KEY_FINANCIALMODELINGPREP
    # base_url: str = "https://financialmodelingprep.com/api/v3/"
    # v4_url: str = "https://financialmodelingprep.com/api/v4/"

    @classmethod
    def _BASE_URL(cls) -> str:
        return "https://financialmodelingprep.com/api/v3/"

    @classmethod
    def _V4_URL(cls) -> str:
        return "https://financialmodelingprep.com/api/v4/"

    @classmethod
    def _KEY(cls) -> str:
        # return cfg.API_KEY_FINANCIALMODELINGPREP
        return "THIS_ISNT_OUR_KEY"

    @classmethod
    def income(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        """Get historical income statement data

        Parameters
        ----------
        quarter : bool, optional
            Flag to get quarterly data, by default False
        limit : int, optional
            Number of statements to get, by default 200

        Returns
        -------
        pd.DataFrame
            Income statement dataframe with columns as the reported dates
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
        if quarter:
            url = f"{cls._BASE_URL()}balance-sheet-statement-as-reported/{symbol}?period=quarter"
        else:
            url = f"{cls._BASE_URL()}balance-sheet-statement-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json()).T

    @classmethod
    def cash_flow(cls, symbol: str, quarter: bool = False, limit=200) -> pd.DataFrame:
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
        if quarter:
            url = f"{cls._BASE_URL()}financial-statement-full-as-reported/{symbol}?period=quarter"
        else:
            url = f"{cls._BASE_URL()}financial-statement-full-as-reported/{symbol}?"
        r = request(url + "&limit=" + str(limit) + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json()).T

    @classmethod
    def revseg(cls, symbol: str, quarter=False) -> dict:
        # TODO: make dataframe since this is not a fixed shape
        if quarter:
            url = f"{cls._V4_URL()}revenue-product-segmentation/?symbol={symbol}&period=quarter"
        else:
            url = f"{cls._V4_URL()}revenue-product-segmentation/?symbol={symbol}"
        r = request(url + "&structure=flat&apikey={cls._KEY()}")
        return r.json()

    @classmethod
    def revgeo(cls, symbol: str, quarter=False) -> dict:
        # TODO same as above
        if quarter:
            url = f"{cls._V4_URL()}revenue-geographic-segmentation/?symbol={symbol}&period=quarter"
        else:
            url = f"{cls._V4_URL()}revenue-geographic-segmentation/?symbol={symbol}"
        r = request(url + "&structure=flat&apikey={cls._KEY()}")
        return r.json()

    @classmethod
    def key_execs(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}key-executives/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def insider(cls, symbol: str) -> pd.DataFrame:
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
        url = (
            f"{cls._V4_URL()}institutional-ownership/symbol-ownership/?symbol={symbol}"
        )
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def price_target(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._V4_URL()}price-target/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def price_target_summary(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._V4_URL()}price-target-summary/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json()).T

    @classmethod
    def upgrade_downgrade(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._V4_URL()}upgrades-downgrades/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def news(cls, symbol: str, limit: int = 100) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}stock_news/?tickers={symbol}&limit={limit}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def divcal(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}historical-price-full/stock_dividend/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(r.json()["historical"])

    @classmethod
    def earnings(cls, symbol: str, limit: int = 100) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}historical/earning_calendar/{symbol}?limit={limit}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def key_metrics(
        cls, symbol: str, quarter: bool = False, limit: int = 200
    ) -> pd.DataFrame:
        if quarter:
            url = f"{cls._BASE_URL()}key-metrics/{symbol}?period=quarter&"
        else:
            url = f"{cls._BASE_URL()}key-metrics/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(r.json()).T

    @classmethod
    def ratios(cls, symbol: str, quarter=True, limit: int = 200) -> pd.DataFrame:
        url = (
            f"{cls._BASE_URL()}ratios/{symbol}?period=quarter&"
            if quarter
            else f"{cls._BASE_URL()}ratios/{symbol}?"
        )
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(r.json()).T

    @classmethod
    def income_growth(cls, symbol: str, limit: int = 00) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}income-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(r.json()).T

    @classmethod
    def balance_growth(cls, symbol: str, limit: int = 00) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}balance-sheet-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(r.json()).T

    @classmethod
    def cash_flow_growth(cls, symbol: str, limit: int = 00) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}cash-flow-statement-growth/{symbol}?"
        r = request(url + f"apikey={cls._KEY()}&limit={limit}")
        return pd.DataFrame(r.json()).T

    @classmethod
    def ftd(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._V4_URL()}/fail_to_deliver/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def senate_trading(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._V4_URL()}/senate-trading/?symbol={symbol}"
        r = request(url + "&apikey=" + cls._KEY())
        return pd.DataFrame(r.json())

    @classmethod
    def splits(cls, symbol: str) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}historical-price-full/stock_split/{symbol}"
        r = request(url + "?apikey=" + cls._KEY())
        return pd.DataFrame(r.json()["historical"])

    @classmethod
    def eod_prices(cls, symbol: str, start, end) -> pd.DataFrame:
        url = f"{cls._BASE_URL()}historical-price-full/{symbol}?from={start}&to={end}"
        r = request(url + f"&apikey={cls._KEY()}")
        return pd.DataFrame(r.json()["historical"])
