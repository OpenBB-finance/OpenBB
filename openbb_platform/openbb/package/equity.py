### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
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
    historical_market_cap
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
    def historical_market_cap(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio."
            ),
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the historical market cap of a ticker symbol.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio.
        interval : Literal['day', 'week', 'month', 'quarter', 'year']
            None

        Returns
        -------
        OBBject
            results : List[HistoricalMarketCap]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalMarketCap
        -------------------
        date : date
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        market_cap : Union[int, float]
            Market capitalization of the security.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.historical_market_cap(provider='fmp', symbol='AAPL')
        """  # noqa: E501

        return self._run(
            "/equity/historical_market_cap",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.historical_market_cap",
                        ("fmp", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                    },
                    "interval": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["day", "week", "month", "quarter", "year"],
                        }
                    },
                },
            )
        )

    @exception_handler
    @validate
    def market_snapshots(
        self,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "polygon"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get an updated equity market snapshot. This includes price data for thousands of stocks.

        Parameters
        ----------
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon.
        market : Literal['amex', 'ams', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'mutual_fund', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra']
            The market to fetch data for. (provider: fmp)
        date : Optional[Union[datetime.date, datetime.datetime, str]]
            The date of the data. Can be a datetime or an ISO datetime string. Historical data appears to go back to mid-June 2022. Example: '2024-03-08T12:15:00+0400' (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[MarketSnapshots]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
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
        volume : Optional[int]
            The trading volume.
        prev_close : Optional[float]
            The previous close price.
        change : Optional[float]
            The change in price from the previous close.
        change_percent : Optional[float]
            The change in price from the previous close, as a normalized percent.
        last_price : Optional[float]
            The last price of the stock. (provider: fmp);
            The last trade price. (provider: intrinio)
        last_price_timestamp : Optional[Union[date, datetime]]
            The timestamp of the last price. (provider: fmp)
        ma50 : Optional[float]
            The 50-day moving average. (provider: fmp)
        ma200 : Optional[float]
            The 200-day moving average. (provider: fmp)
        year_high : Optional[float]
            The 52-week high. (provider: fmp)
        year_low : Optional[float]
            The 52-week low. (provider: fmp)
        volume_avg : Optional[int]
            Average daily trading volume. (provider: fmp)
        market_cap : Optional[int]
            Market cap of the stock. (provider: fmp)
        eps : Optional[float]
            Earnings per share. (provider: fmp)
        pe : Optional[float]
            Price to earnings ratio. (provider: fmp)
        shares_outstanding : Optional[int]
            Number of shares outstanding. (provider: fmp)
        name : Optional[str]
            The company name associated with the symbol. (provider: fmp)
        exchange : Optional[str]
            The exchange of the stock. (provider: fmp)
        earnings_date : Optional[Union[date, datetime]]
            The upcoming earnings announcement date. (provider: fmp)
        last_size : Optional[int]
            The last trade size. (provider: intrinio)
        last_volume : Optional[int]
            The last trade volume. (provider: intrinio)
        last_trade_timestamp : Optional[datetime]
            The timestamp of the last trade. (provider: intrinio);
            The last trade timestamp. (provider: polygon)
        bid_size : Optional[int]
            The size of the last bid price. Bid price and size is not always available. (provider: intrinio);
            The current bid size. (provider: polygon)
        bid_price : Optional[float]
            The last bid price. Bid price and size is not always available. (provider: intrinio)
        ask_price : Optional[float]
            The last ask price. Ask price and size is not always available. (provider: intrinio)
        ask_size : Optional[int]
            The size of the last ask price. Ask price and size is not always available. (provider: intrinio);
            The current ask size. (provider: polygon)
        last_bid_timestamp : Optional[datetime]
            The timestamp of the last bid price. Bid price and size is not always available. (provider: intrinio)
        last_ask_timestamp : Optional[datetime]
            The timestamp of the last ask price. Ask price and size is not always available. (provider: intrinio)
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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.market_snapshots(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/market_snapshots",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.market_snapshots",
                        ("fmp", "intrinio", "polygon"),
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
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get general information about a company. This includes company name, industry, sector and price data.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, yfinance.

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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.profile(symbol='AAPL', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/profile",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.profile",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                        "yfinance": {"multiple_items_allowed": True, "choices": None},
                    }
                },
            )
        )

    @exception_handler
    @validate
    def screener(
        self,
        provider: Annotated[
            Optional[Literal["fmp", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Screen for companies meeting various criteria.

        These criteria include market cap, price, beta, volume, and dividend yield.


        Parameters
        ----------
        provider : Optional[Literal['fmp', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, yfinance.
        mktcap_min : Optional[int]
            Filter by market cap greater than this value. (provider: fmp, yfinance)
        mktcap_max : Optional[int]
            Filter by market cap less than this value. (provider: fmp, yfinance)
        price_min : Optional[float]
            Filter by price greater than this value. (provider: fmp, yfinance)
        price_max : Optional[float]
            Filter by price less than this value. (provider: fmp, yfinance)
        beta_min : Optional[float]
            Filter by a beta greater than this value. (provider: fmp, yfinance)
        beta_max : Optional[float]
            Filter by a beta less than this value. (provider: fmp, yfinance)
        volume_min : Optional[int]
            Filter by volume greater than this value. (provider: fmp, yfinance)
        volume_max : Optional[int]
            Filter by volume less than this value. (provider: fmp, yfinance)
        dividend_min : Optional[float]
            Filter by dividend amount greater than this value. (provider: fmp)
        dividend_max : Optional[float]
            Filter by dividend amount less than this value. (provider: fmp)
        is_etf : Optional[bool]
            If true, returns only ETFs. (provider: fmp)
        is_active : Optional[bool]
            If false, returns only inactive tickers. (provider: fmp)
        sector : Optional[Union[Literal['consumer_cyclical', 'energy', 'technology', 'industrials', 'financial_services', 'basic_materials', 'communication_services', 'consumer_defensive', 'healthcare', 'real_estate', 'utilities', 'industrial_goods', 'financial', 'services', 'conglomerates'], Literal['basic_materials', 'communication_services', 'consumer_cyclical', 'consumer_defensive', 'energy', 'financial_services', 'healthcare', 'industrials', 'real_estate', 'technology', 'utilities']]]
            Filter by sector. (provider: fmp, yfinance)
        industry : Optional[str]
            Filter by industry. (provider: fmp, yfinance)
        country : Optional[str]
            Filter by country, as a two-letter country code. (provider: fmp);
            Filter by country, as a two-letter country code. Default is, 'us'. Use, 'all', for all countries. (provider: yfinance)
        exchange : Optional[Union[Literal['amex', 'ams', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'mutual_fund', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra'], Literal['ams', 'aqs', 'ase', 'asx', 'ath', 'ber', 'bru', 'bse', 'bts', 'bud', 'bue', 'bvb', 'bvc', 'ccs', 'cnq', 'cph', 'cxe', 'dfm', 'doh', 'dus', 'ebs', 'fka', 'fra', 'ger', 'ham', 'han', 'hel', 'hkg', 'ice', 'iob', 'ise', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'kuw', 'lis', 'lit', 'lse', 'mce', 'mex', 'mil', 'mun', 'ncm', 'neo', 'ngm', 'nms', 'nsi', 'nyq', 'nze', 'oem', 'oqb', 'oqx', 'osl', 'par', 'pnk', 'pra', 'ris', 'sau', 'ses', 'set', 'sgo', 'shh', 'shz', 'sto', 'stu', 'tai', 'tal', 'tlv', 'tor', 'two', 'van', 'vie', 'vse', 'wse']]]
            Filter by exchange. (provider: fmp, yfinance)
        limit : Optional[int]
            Limit the number of results to return. (provider: fmp);
            Limit the number of results returned. Default is, 200. Set to, 0, for all results. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityScreener]
                Serializable results.
            provider : Optional[Literal['fmp', 'yfinance']]
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
        name : Optional[str]
            Name of the company.
        market_cap : Optional[Union[int, float]]
            The market cap of ticker. (provider: fmp);
            Market Cap. (provider: yfinance)
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
            The exchange code the asset trades on. (provider: fmp);
            Exchange where the stock is listed. (provider: yfinance)
        exchange_name : Optional[str]
            The full name of the primary exchange. (provider: fmp)
        country : Optional[str]
            The two-letter country abbreviation where the head office is located. (provider: fmp)
        is_etf : Optional[Literal[True, False]]
            Whether the ticker is an ETF. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        open : Optional[float]
            Open price for the day. (provider: yfinance)
        high : Optional[float]
            High price for the day. (provider: yfinance)
        low : Optional[float]
            Low price for the day. (provider: yfinance)
        previous_close : Optional[float]
            Previous close price. (provider: yfinance)
        ma50 : Optional[float]
            50-day moving average. (provider: yfinance)
        ma200 : Optional[float]
            200-day moving average. (provider: yfinance)
        year_high : Optional[float]
            52-week high. (provider: yfinance)
        year_low : Optional[float]
            52-week low. (provider: yfinance)
        shares_outstanding : Optional[float]
            Shares outstanding. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price to book ratio. (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share over the trailing twelve months. (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        pe_forward : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        dividend_yield : Optional[float]
            Trailing twelve month dividend yield. (provider: yfinance)
        exchange_timezone : Optional[str]
            Timezone of the exchange. (provider: yfinance)
        earnings_date : Optional[datetime]
            Most recent earnings date. (provider: yfinance)
        currency : Optional[str]
            Currency of the price data. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.screener(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/screener",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.screener",
                        ("fmp", "yfinance"),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "sector": {
                        "yfinance": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "basic_materials",
                                "communication_services",
                                "consumer_cyclical",
                                "consumer_defensive",
                                "energy",
                                "financial_services",
                                "healthcare",
                                "industrials",
                                "real_estate",
                                "technology",
                                "utilities",
                            ],
                        }
                    },
                    "industry": {
                        "yfinance": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "advertising_agencies",
                                "aerospace_defense",
                                "agricultural_inputs",
                                "airlines",
                                "airports_air_services",
                                "aluminum",
                                "apparel_manufacturing",
                                "apparel_retail",
                                "asset_management",
                                "auto_components",
                                "auto_manufacturers",
                                "auto_parts",
                                "auto_truck_dealerships",
                                "automobiles",
                                "banks",
                                "biotechnology",
                                "broadcasting",
                                "building_materials",
                                "building_products",
                                "building_products_equipment",
                                "business_equipment_supplies",
                                "capital_markets",
                                "chemicals",
                                "coking_coal",
                                "commercial_services",
                                "communication_equipment",
                                "computer_hardware",
                                "confectioners",
                                "construction_engineering",
                                "construction_materials",
                                "consulting_services",
                                "consumer_durables",
                                "consumer_electronics",
                                "consumer_services",
                                "copper",
                                "credit_services",
                                "department_stores",
                                "diagnostics_research",
                                "discount_stores",
                                "diversified_financials",
                                "education_training_services",
                                "electrical_equipment",
                                "electrical_equipment_parts",
                                "electronic_components",
                                "electronic_gaming_multimedia",
                                "electronics_computer_distribution",
                                "energy_services",
                                "engineering_construction",
                                "entertainment",
                                "farm_heavy_construction_machinery",
                                "farm_products",
                                "financial_conglomerates",
                                "financial_data_stock_exchanges",
                                "food_distribution",
                                "footwear_accessories",
                                "furnishings_fixtures_appliances",
                                "gambling",
                                "gold",
                                "grocery_stores",
                                "health_information_services",
                                "healthcare_plans",
                                "home_builders",
                                "home_improvement_retail",
                                "household_products",
                                "household_personal_products",
                                "industrial_conglomerates",
                                "industrial_distribution",
                                "information_technology_services",
                                "infrastructure_operations",
                                "insurance",
                                "integrated_freight_logistics",
                                "internet_content_information",
                                "internet_retail",
                                "leisure",
                                "lodging",
                                "lumber_wood_production",
                                "luxury_goods",
                                "machinery",
                                "marine_shipping",
                                "media",
                                "medical_care_facilities",
                                "medical_devices",
                                "medical_distribution",
                                "medical_instruments_supplies",
                                "metal_fabrication",
                                "mortgage_finance",
                                "oil_gas_drilling",
                                "oil_gas_e_p",
                                "oil_gas_equipment_services",
                                "oil_gas_integrated",
                                "oil_gas_midstream",
                                "oil_gas_producers",
                                "oil_gas_refining_marketing",
                                "other_industrial_metals_mining",
                                "other_precious_metals_mining",
                                "packaged_foods",
                                "packaging_containers",
                                "paper_forestry",
                                "paper_paper_products",
                                "personal_services",
                                "pharmaceuticals",
                                "pharmaceutical_retailers",
                                "pollution_treatment_controls",
                                "precious_metals",
                                "publishing",
                                "railroads",
                                "real_estate",
                                "recreational_vehicles",
                                "refiners_pipelines",
                                "rental_leasing_services",
                                "residential_construction",
                                "resorts_casinos",
                                "restaurants",
                                "retailing",
                                "scientific_technical_instruments",
                                "security_protection_services",
                                "semiconductor_equipment_materials",
                                "semiconductors",
                                "shell_companies",
                                "silver",
                                "software_and_services",
                                "solar",
                                "specialty_business_services",
                                "specialty_chemicals",
                                "specialty_industrial_machinery",
                                "specialty_retail",
                                "staffing_employment_services",
                                "steel",
                                "technology_hardware",
                                "telecom_services",
                                "textiles_apparel",
                                "textile_manufacturing",
                                "thermal_coal",
                                "tobacco",
                                "tools_accessories",
                                "traders_distributors",
                                "transportation",
                                "transportation_infrastructure",
                                "travel_services",
                                "trucking",
                                "uranium",
                                "utilities",
                                "waste_management",
                            ],
                        }
                    },
                    "country": {
                        "yfinance": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "all",
                                "ar",
                                "at",
                                "au",
                                "be",
                                "br",
                                "ca",
                                "ch",
                                "cl",
                                "cn",
                                "cz",
                                "de",
                                "dk",
                                "ee",
                                "eg",
                                "es",
                                "fi",
                                "fr",
                                "gb",
                                "gr",
                                "hk",
                                "hu",
                                "id",
                                "ie",
                                "il",
                                "in",
                                "is",
                                "it",
                                "jp",
                                "kr",
                                "kw",
                                "lk",
                                "lt",
                                "lv",
                                "mx",
                                "my",
                                "nl",
                                "no",
                                "nz",
                                "pe",
                                "ph",
                                "pk",
                                "pl",
                                "pt",
                                "qa",
                                "ro",
                                "ru",
                                "sa",
                                "se",
                                "sg",
                                "sr",
                                "th",
                                "tr",
                                "tw",
                                "us",
                                "ve",
                                "vn",
                                "za",
                            ],
                        }
                    },
                    "exchange": {
                        "yfinance": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "ams",
                                "aqs",
                                "ase",
                                "asx",
                                "ath",
                                "ber",
                                "bru",
                                "bse",
                                "bts",
                                "bud",
                                "bue",
                                "bvb",
                                "bvc",
                                "ccs",
                                "cnq",
                                "cph",
                                "cxe",
                                "dfm",
                                "doh",
                                "dus",
                                "ebs",
                                "fka",
                                "fra",
                                "ger",
                                "ham",
                                "han",
                                "hel",
                                "hkg",
                                "ice",
                                "iob",
                                "ise",
                                "ist",
                                "jkt",
                                "jnb",
                                "jpx",
                                "kls",
                                "kuw",
                                "lis",
                                "lit",
                                "lse",
                                "mce",
                                "mex",
                                "mil",
                                "mun",
                                "ncm",
                                "neo",
                                "ngm",
                                "nms",
                                "nsi",
                                "nyq",
                                "nze",
                                "oem",
                                "oqb",
                                "oqx",
                                "osl",
                                "par",
                                "pnk",
                                "pra",
                                "ris",
                                "sau",
                                "ses",
                                "set",
                                "sgo",
                                "shh",
                                "shz",
                                "sto",
                                "stu",
                                "tai",
                                "tal",
                                "tlv",
                                "tor",
                                "two",
                                "van",
                                "vie",
                                "vse",
                                "wse",
                            ],
                        }
                    },
                },
            )
        )

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[str, OpenBBField(description="Search query.")] = "",
        is_symbol: Annotated[
            bool, OpenBBField(description="Whether to search by ticker symbol.")
        ] = False,
        provider: Annotated[
            Optional[Literal["intrinio", "sec"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio, sec."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Search for stock symbol, CIK, LEI, or company name.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        provider : Optional[Literal['intrinio', 'sec']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio, sec.
        active : bool
            When true, return companies that are actively traded (having stock prices within the past 14 days). When false, return companies that are not actively traded or never have been traded. (provider: intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)
        use_cache : bool
            Whether to use the cache or not. (provider: sec)
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
        name : Optional[str]
            Name of the company.
        cik : Optional[str]
            ;
            Central Index Key (provider: sec)
        lei : Optional[str]
            The Legal Entity Identifier (LEI) of the company. (provider: intrinio)
        intrinio_id : Optional[str]
            The Intrinio ID of the company. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.search(provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/equity/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.search",
                        ("intrinio", "sec"),
                    )
                },
                standard_params={
                    "query": query,
                    "is_symbol": is_symbol,
                },
                extra_params=kwargs,
            )
        )

    @property
    def shorts(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_shorts

        return equity_shorts.ROUTER_equity_shorts(command_runner=self._command_runner)
