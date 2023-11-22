### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_equity(Container):
    """/equity
    /calendar
    /compare
    /discovery
    /estimates
    /fundamental
    market_snapshots
    /ownership
    /price
    screener
    search
    /shorts
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def calendar(self):  # route = "/equity/calendar"
        from . import equity_calendar

        return equity_calendar.ROUTER_equity_calendar(
            command_runner=self._command_runner
        )

    @property
    def compare(self):  # route = "/equity/compare"
        from . import equity_compare

        return equity_compare.ROUTER_equity_compare(command_runner=self._command_runner)

    @property
    def discovery(self):  # route = "/equity/discovery"
        from . import equity_discovery

        return equity_discovery.ROUTER_equity_discovery(
            command_runner=self._command_runner
        )

    @property
    def estimates(self):  # route = "/equity/estimates"
        from . import equity_estimates

        return equity_estimates.ROUTER_equity_estimates(
            command_runner=self._command_runner
        )

    @property
    def fundamental(self):  # route = "/equity/fundamental"
        from . import equity_fundamental

        return equity_fundamental.ROUTER_equity_fundamental(
            command_runner=self._command_runner
        )

    @validate
    def market_snapshots(
        self, provider: Optional[Literal["fmp", "polygon"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Get a current, complete, market snapshot.

        Parameters
        ----------
        provider : Optional[Literal['fmp', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        market : Literal['AMEX', 'AMS', 'ASE', 'ASX', 'ATH', 'BME', 'BRU', 'BUD', 'BUE', 'CAI', 'CNQ', 'CPH', 'DFM', 'DOH', 'DUS', 'ETF', 'EURONEXT', 'HEL', 'HKSE', 'ICE', 'IOB', 'IST', 'JKT', 'JNB', 'JPX', 'KLS', 'KOE', 'KSC', 'KUW', 'LSE', 'MEX', 'MIL', 'NASDAQ', 'NEO', 'NSE', 'NYSE', 'NZE', 'OSL', 'OTC', 'PNK', 'PRA', 'RIS', 'SAO', 'SAU', 'SES', 'SET', 'SGO', 'SHH', 'SHZ', 'SIX', 'STO', 'TAI', 'TLV', 'TSX', 'TWO', 'VIE', 'WSE', 'XETRA']
            The market to fetch data for. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[MarketSnapshots]
                Serializable results.
            provider : Optional[Literal['fmp', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MarketSnapshots
        ---------------
        symbol : str
            Symbol representing the entity requested in the data.
        open : Optional[float]
            The open price.
        high : Optional[float]
            The high price.
        low : Optional[float]
            The low price.
        close : Optional[float]
            The close price.
        prev_close : Optional[float]
            The previous closing price of the stock.
        change : Optional[float]
            The change in price.
        change_percent : Optional[float]
            The change, as a percent.
        volume : Optional[int]
            The trading volume.
        price : Optional[float]
            The last price of the stock. (provider: fmp)
        avg_volume : Optional[int]
            Average volume of the stock. (provider: fmp)
        ma50 : Optional[float]
            The 50-day moving average. (provider: fmp)
        ma200 : Optional[float]
            The 200-day moving average. (provider: fmp)
        year_high : Optional[float]
            The 52-week high. (provider: fmp)
        year_low : Optional[float]
            The 52-week low. (provider: fmp)
        market_cap : Optional[float]
            Market cap of the stock. (provider: fmp)
        shares_outstanding : Optional[float]
            Number of shares outstanding. (provider: fmp)
        eps : Optional[float]
            Earnings per share. (provider: fmp)
        pe : Optional[float]
            Price to earnings ratio. (provider: fmp)
        exchange : Optional[str]
            The exchange of the stock. (provider: fmp)
        timestamp : Optional[Union[int, float]]
            The timestamp of the data. (provider: fmp)
        earnings_announcement : Optional[str]
            The earnings announcement of the stock. (provider: fmp)
        name : Optional[str]
            The name associated with the stock symbol. (provider: fmp)
        vwap : Optional[float]
            The volume weighted average price of the stock on the current trading day. (provider: polygon)
        prev_open : Optional[float]
            The previous trading session opening price. (provider: polygon)
        prev_high : Optional[float]
            The previous trading session high price. (provider: polygon)
        prev_low : Optional[float]
            The previous trading session low price. (provider: polygon)
        prev_volume : Optional[float]
            The previous trading session volume. (provider: polygon)
        prev_vwap : Optional[float]
            The previous trading session VWAP. (provider: polygon)
        last_updated : Optional[datetime]
            The last time the data was updated. (provider: polygon)
        bid : Optional[float]
            The current bid price. (provider: polygon)
        bid_size : Optional[int]
            The current bid size. (provider: polygon)
        ask_size : Optional[int]
            The current ask size. (provider: polygon)
        ask : Optional[float]
            The current ask price. (provider: polygon)
        quote_timestamp : Optional[datetime]
            The timestamp of the last quote. (provider: polygon)
        last_trade_price : Optional[float]
            The last trade price. (provider: polygon)
        last_trade_size : Optional[int]
            The last trade size. (provider: polygon)
        last_trade_conditions : Optional[List[int]]
            The last trade condition codes. (provider: polygon)
        last_trade_exchange : Optional[int]
            The last trade exchange ID code. (provider: polygon)
        last_trade_timestamp : Optional[datetime]
            The last trade timestamp. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.market_snapshots()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/equity/market_snapshots",
            **inputs,
        )

    @property
    def ownership(self):  # route = "/equity/ownership"
        from . import equity_ownership

        return equity_ownership.ROUTER_equity_ownership(
            command_runner=self._command_runner
        )

    @property
    def price(self):  # route = "/equity/price"
        from . import equity_price

        return equity_price.ROUTER_equity_price(command_runner=self._command_runner)

    @validate
    def screener(
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Equity Screen. Screen for companies meeting various criteria.

        Parameters
        ----------
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        mktcap_min : Optional[int]
            Filter by market cap greater than this value. (provider: fmp)
        mktcap_max : Optional[int]
            Filter by market cap less than this value. (provider: fmp)
        price_min : Optional[float]
            Filter by price greater than this value. (provider: fmp)
        price_max : Optional[float]
            Filter by price less than this value. (provider: fmp)
        beta_min : Optional[float]
            Filter by a beta greater than this value. (provider: fmp)
        beta_max : Optional[float]
            Filter by a beta less than this value. (provider: fmp)
        volume_min : Optional[int]
            Filter by volume greater than this value. (provider: fmp)
        volume_max : Optional[int]
            Filter by volume less than this value. (provider: fmp)
        dividend_min : Optional[float]
            Filter by dividend amount greater than this value. (provider: fmp)
        dividend_max : Optional[float]
            Filter by dividend amount less than this value. (provider: fmp)
        is_etf : Optional[bool]
            If true, returns only ETFs. (provider: fmp)
        is_active : Optional[bool]
            If false, returns only inactive tickers. (provider: fmp)
        sector : Optional[Literal['Consumer Cyclical', 'Energy', 'Technology', 'Industrials', 'Financial Services', 'Basic Materials', 'Communication Services', 'Consumer Defensive', 'Healthcare', 'Real Estate', 'Utilities', 'Industrial Goods', 'Financial', 'Services', 'Conglomerates']]
            Filter by sector. (provider: fmp)
        industry : Optional[str]
            Filter by industry. (provider: fmp)
        country : Optional[str]
            Filter by country, as a two-letter country code. (provider: fmp)
        exchange : Optional[Literal['amex', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra']]
            Filter by exchange. (provider: fmp)
        limit : Optional[int]
            Limit the number of results to return. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[EquityScreener]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EquityScreener
        --------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the company.
        market_cap : Optional[int]
            The market cap of ticker. (provider: fmp)
        sector : Optional[str]
            The sector the ticker belongs to. (provider: fmp)
        industry : Optional[str]
            The industry ticker belongs to. (provider: fmp)
        beta : Optional[float]
            The beta of the ETF. (provider: fmp)
        price : Optional[float]
            The current price. (provider: fmp)
        last_annual_dividend : Optional[float]
            The last annual amount dividend paid. (provider: fmp)
        volume : Optional[int]
            The current trading volume. (provider: fmp)
        exchange : Optional[str]
            The exchange code the asset trades on. (provider: fmp)
        exchange_name : Optional[str]
            The full name of the primary exchange. (provider: fmp)
        country : Optional[str]
            The two-letter country abbreviation where the head office is located. (provider: fmp)
        is_etf : Optional[Literal[True, False]]
            Whether the ticker is an ETF. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.screener()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/equity/screener",
            **inputs,
        )

    @validate
    def search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        is_symbol: Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Equity Search. Search for a company or stock ticker.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.
        is_fund : bool
            Whether to direct the search to the list of mutual funds and ETFs. (provider: sec)
        use_cache : bool
            Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. (provider: sec)

        Returns
        -------
        OBBject
            results : List[EquitySearch]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EquitySearch
        ------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the company.
        cik : Optional[str]
            Central Index Key (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "is_symbol": is_symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/search",
            **inputs,
        )

    @property
    def shorts(self):  # route = "/equity/shorts"
        from . import equity_shorts

        return equity_shorts.ROUTER_equity_shorts(command_runner=self._command_runner)
