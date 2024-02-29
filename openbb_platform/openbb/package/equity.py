### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
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
    profile
    screener
    search
    /shorts
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def calendar(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_calendar

        return equity_calendar.ROUTER_equity_calendar(
            command_runner=self._command_runner
        )

    @property
    def compare(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_compare

        return equity_compare.ROUTER_equity_compare(command_runner=self._command_runner)

    @property
    def discovery(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_discovery

        return equity_discovery.ROUTER_equity_discovery(
            command_runner=self._command_runner
        )

    @property
    def estimates(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_estimates

        return equity_estimates.ROUTER_equity_estimates(
            command_runner=self._command_runner
        )

    @property
    def fundamental(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_fundamental

        return equity_fundamental.ROUTER_equity_fundamental(
            command_runner=self._command_runner
        )

    @exception_handler
    @validate
    def market_snapshots(
        self, provider: Optional[Literal["fmp", "polygon"]] = None, **kwargs
    ) -> OBBject:
        """Get an updated equity market snapshot. This includes price data for thousands of stocks.

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
            extra : Dict[str, Any]
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
            The previous close price.
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
        timestamp : Optional[Union[float, int]]
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

        return self._run(
            "/equity/market_snapshots",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/market_snapshots",
                        ("fmp", "polygon"),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @property
    def ownership(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_ownership

        return equity_ownership.ROUTER_equity_ownership(
            command_runner=self._command_runner
        )

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_price

        return equity_price.ROUTER_equity_price(command_runner=self._command_runner)

    @exception_handler
    @validate
    def profile(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): fmp, intrinio, yfinance."
            ),
        ],
        provider: Optional[Literal["fmp", "intrinio", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get general information about a company. This includes company name, industry, sector and price data.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): fmp, intrinio, yfinance.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EquityInfo]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityInfo
        ----------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Common name of the company.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        cusip : Optional[str]
            CUSIP identifier for the company.
        isin : Optional[str]
            International Securities Identification Number.
        lei : Optional[str]
            Legal Entity Identifier assigned to the company.
        legal_name : Optional[str]
            Official legal name of the company.
        stock_exchange : Optional[str]
            Stock exchange where the company is traded.
        sic : Optional[int]
            Standard Industrial Classification code for the company.
        short_description : Optional[str]
            Short description of the company.
        long_description : Optional[str]
            Long description of the company.
        ceo : Optional[str]
            Chief Executive Officer of the company.
        company_url : Optional[str]
            URL of the company's website.
        business_address : Optional[str]
            Address of the company's headquarters.
        mailing_address : Optional[str]
            Mailing address of the company.
        business_phone_no : Optional[str]
            Phone number of the company's headquarters.
        hq_address1 : Optional[str]
            Address of the company's headquarters.
        hq_address2 : Optional[str]
            Address of the company's headquarters.
        hq_address_city : Optional[str]
            City of the company's headquarters.
        hq_address_postal_code : Optional[str]
            Zip code of the company's headquarters.
        hq_state : Optional[str]
            State of the company's headquarters.
        hq_country : Optional[str]
            Country of the company's headquarters.
        inc_state : Optional[str]
            State in which the company is incorporated.
        inc_country : Optional[str]
            Country in which the company is incorporated.
        employees : Optional[int]
            Number of employees working for the company.
        entity_legal_form : Optional[str]
            Legal form of the company.
        entity_status : Optional[str]
            Status of the company.
        latest_filing_date : Optional[date]
            Date of the company's latest filing.
        irs_number : Optional[str]
            IRS number assigned to the company.
        sector : Optional[str]
            Sector in which the company operates.
        industry_category : Optional[str]
            Category of industry in which the company operates.
        industry_group : Optional[str]
            Group of industry in which the company operates.
        template : Optional[str]
            Template used to standardize the company's financial statements.
        standardized_active : Optional[bool]
            Whether the company is active or not.
        first_fundamental_date : Optional[date]
            Date of the company's first fundamental.
        last_fundamental_date : Optional[date]
            Date of the company's last fundamental.
        first_stock_price_date : Optional[date]
            Date of the company's first stock price.
        last_stock_price_date : Optional[date]
            Date of the company's last stock price.
        is_etf : Optional[bool]
            If the symbol is an ETF. (provider: fmp)
        is_actively_trading : Optional[bool]
            If the company is actively trading. (provider: fmp)
        is_adr : Optional[bool]
            If the stock is an ADR. (provider: fmp)
        is_fund : Optional[bool]
            If the company is a fund. (provider: fmp)
        image : Optional[str]
            Image of the company. (provider: fmp)
        currency : Optional[str]
            Currency in which the stock is traded. (provider: fmp, yfinance)
        market_cap : Optional[int]
            Market capitalization of the company. (provider: fmp);
            The market capitalization of the asset. (provider: yfinance)
        last_price : Optional[float]
            The last traded price. (provider: fmp)
        year_high : Optional[float]
            The one-year high of the price. (provider: fmp)
        year_low : Optional[float]
            The one-year low of the price. (provider: fmp)
        volume_avg : Optional[int]
            Average daily trading volume. (provider: fmp)
        annualized_dividend_amount : Optional[float]
            The annualized dividend payment based on the most recent regular dividend payment. (provider: fmp)
        beta : Optional[float]
            Beta of the stock relative to the market. (provider: fmp, yfinance)
        id : Optional[str]
            Intrinio ID for the company. (provider: intrinio)
        thea_enabled : Optional[bool]
            Whether the company has been enabled for Thea. (provider: intrinio)
        exchange_timezone : Optional[str]
            The timezone of the exchange. (provider: yfinance)
        issue_type : Optional[str]
            The issuance type of the asset. (provider: yfinance)
        shares_outstanding : Optional[int]
            The number of listed shares outstanding. (provider: yfinance)
        shares_float : Optional[int]
            The number of shares in the public float. (provider: yfinance)
        shares_implied_outstanding : Optional[int]
            Implied shares outstanding of common equityassuming the conversion of all convertible subsidiary equity into common. (provider: yfinance)
        shares_short : Optional[int]
            The reported number of shares short. (provider: yfinance)
        dividend_yield : Optional[float]
            The dividend yield of the asset, as a normalized percent. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.profile(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/profile",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/profile",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {
                        "multiple_items_allowed": ["fmp", "intrinio", "yfinance"]
                    }
                },
            )
        )

    @exception_handler
    @validate
    def screener(self, provider: Optional[Literal["fmp"]] = None, **kwargs) -> OBBject:
        """Screen for companies meeting various criteria. These criteria include
        market cap, price, beta, volume, and dividend yield.

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
            extra : Dict[str, Any]
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

        return self._run(
            "/equity/screener",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/screener",
                        ("fmp",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        is_symbol: Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        use_cache: Annotated[
            Optional[bool],
            OpenBBCustomParameter(description="Whether to use the cache or not."),
        ] = True,
        provider: Optional[Literal["intrinio", "sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Search for stock symbol, CIK, LEI, or company name.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        use_cache : Optional[bool]
            Whether to use the cache or not.
        provider : Optional[Literal['intrinio', 'sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        active : Optional[bool]
            When true, return companies that are actively traded (having stock prices within the past 14 days). When false, return companies that are not actively traded or never have been traded. (provider: intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)
        is_fund : bool
            Whether to direct the search to the list of mutual funds and ETFs. (provider: sec)

        Returns
        -------
        OBBject
            results : List[EquitySearch]
                Serializable results.
            provider : Optional[Literal['intrinio', 'sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquitySearch
        ------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        name : str
            Name of the company.
        cik : Optional[str]
            ;
            Central Index Key (provider: sec)
        lei : Optional[str]
            The Legal Entity Identifier (LEI) of the company. (provider: intrinio)
        intrinio_id : Optional[str]
            The Intrinio ID of the company. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.search(query="AAPL", is_symbol=False, use_cache=True)
        """  # noqa: E501

        return self._run(
            "/equity/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/search",
                        ("intrinio", "sec"),
                    )
                },
                standard_params={
                    "query": query,
                    "is_symbol": is_symbol,
                    "use_cache": use_cache,
                },
                extra_params=kwargs,
            )
        )

    @property
    def shorts(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_shorts

        return equity_shorts.ROUTER_equity_shorts(command_runner=self._command_runner)
