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
    /darkpool
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
    def darkpool(self):
        # pylint: disable=import-outside-toplevel
        from . import equity_darkpool

        return equity_darkpool.ROUTER_equity_darkpool(
            command_runner=self._command_runner
        )

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
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp."
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
        chart: Annotated[
            bool,
            OpenBBField(
                description="Whether to create a chart or not, by default False."
            ),
        ] = False,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the historical market cap of a ticker symbol.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.

        Returns
        -------
        OBBject
            results : List[HistoricalMarketCap]
                Serializable results.
            provider : Optional[Literal['fmp']]
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
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                chart=chart,
                info={
                    "symbol": {"fmp": {"multiple_items_allowed": True, "choices": None}}
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
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance."
            ),
        ],
        provider: Annotated[
            Optional[Literal["finviz", "fmp", "intrinio", "tmx", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz, fmp, intrinio, tmx, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get general information about a company. This includes company name, industry, sector and price data.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance.
        provider : Optional[Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz, fmp, intrinio, tmx, yfinance.

        Returns
        -------
        OBBject
            results : List[EquityInfo]
                Serializable results.
            provider : Optional[Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance']]
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
        index : Optional[str]
            Included in indices - i.e., Dow, Nasdaq, or S&P. (provider: finviz)
        optionable : Optional[str]
            Whether options trade against the ticker. (provider: finviz)
        shortable : Optional[str]
            If the asset is shortable. (provider: finviz)
        shares_outstanding : Optional[Union[str, int]]
            The number of shares outstanding, as an abbreviated string. (provider: finviz);
            The number of listed shares outstanding. (provider: tmx);
            The number of listed shares outstanding. (provider: yfinance)
        shares_float : Optional[Union[str, int]]
            The number of shares in the public float, as an abbreviated string. (provider: finviz);
            The number of shares in the public float. (provider: yfinance)
        short_interest : Optional[str]
            The last reported number of shares sold short, as an abbreviated string. (provider: finviz)
        institutional_ownership : Optional[float]
            The institutional ownership of the stock, as a normalized percent. (provider: finviz)
        market_cap : Optional[int]
            The market capitalization of the stock, as an abbreviated string. (provider: finviz);
            Market capitalization of the company. (provider: fmp);
            The market capitalization of the asset. (provider: yfinance)
        dividend_yield : Optional[float]
            The dividend yield of the stock, as a normalized percent. (provider: finviz, yfinance)
        earnings_date : Optional[str]
            The last, or next confirmed, earnings date and announcement time, as a string. The format is Nov 02 AMC - for after market close. (provider: finviz)
        beta : Optional[float]
            The beta of the stock relative to the broad market. (provider: finviz, fmp, yfinance)
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
        id : Optional[str]
            Intrinio ID for the company. (provider: intrinio)
        thea_enabled : Optional[bool]
            Whether the company has been enabled for Thea. (provider: intrinio)
        email : Optional[str]
            The email of the company. (provider: tmx)
        issue_type : Optional[str]
            The issuance type of the asset. (provider: tmx, yfinance)
        shares_escrow : Optional[int]
            The number of shares held in escrow. (provider: tmx)
        shares_total : Optional[int]
            The total number of shares outstanding from all classes. (provider: tmx)
        dividend_frequency : Optional[str]
            The dividend frequency. (provider: tmx)
        exchange_timezone : Optional[str]
            The timezone of the exchange. (provider: yfinance)
        shares_implied_outstanding : Optional[int]
            Implied shares outstanding of common equityassuming the conversion of all convertible subsidiary equity into common. (provider: yfinance)
        shares_short : Optional[int]
            The reported number of shares short. (provider: yfinance)

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
                        ("finviz", "fmp", "intrinio", "tmx", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "finviz": {"multiple_items_allowed": True, "choices": None},
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                        "tmx": {"multiple_items_allowed": True, "choices": None},
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
            Optional[Literal["finviz", "fmp", "nasdaq"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz, fmp, nasdaq."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Screen for companies meeting various criteria.

        These criteria include market cap, price, beta, volume, and dividend yield.


        Parameters
        ----------
        provider : Optional[Literal['finviz', 'fmp', 'nasdaq']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz, fmp, nasdaq.
        metric : Literal['overview', 'valuation', 'financial', 'ownership', 'performance', 'technical']
            The data group to return, default is 'overview'. (provider: finviz)
        exchange : Optional[Union[Literal['all', 'amex', 'nasdaq', 'nyse'], Literal['amex', 'ams', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'mutual_fund', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra'], str]]
            Filter by exchange. (provider: finviz, fmp);
            Filter by exchange. Multiple comma separated items allowed. (provider: nasdaq)
        index : Literal['all', 'dow', 'nasdaq', 'sp500', 'russell']
            Filter by index. (provider: finviz)
        sector : Optional[Union[Literal['all', 'energy', 'materials', 'industrials', 'consumer_cyclical', 'consumer_defensive', 'financial', 'healthcare', 'technology', 'communication_services', 'utilities', 'real_estate'], Literal['consumer_cyclical', 'energy', 'technology', 'industrials', 'financial_services', 'basic_materials', 'communication_services', 'consumer_defensive', 'healthcare', 'real_estate', 'utilities', 'industrial_goods', 'financial', 'services', 'conglomerates'], Literal['all', 'energy', 'basic_materials', 'industrials', 'consumer_staples', 'consumer_discretionary', 'health_care', 'financial_services', 'technology', 'communication_services', 'utilities', 'real_estate'], str]]
            Filter by sector. (provider: finviz, fmp);
            Filter by sector. Multiple comma separated items allowed. (provider: nasdaq)
        industry : Optional[str]
            Filter by industry. (provider: finviz, fmp)
        mktcap : Union[Literal['all', 'mega', 'large', 'large_over', 'large_under', 'mid', 'mid_over', 'mid_under', 'small', 'small_over', 'small_under', 'micro', 'micro_over', 'micro_under', 'nano'], Literal['all', 'mega', 'large', 'mid', 'small', 'micro'], str]
            Filter by market cap.
            Mega - > 200B
            Large - 10B - 200B
            Mid - 2B - 10B
            Small - 300M - 2B
            Micro - 50M - 300M
            Nano - < 50M (provider: finviz, nasdaq)
        recommendation : Union[Literal['all', 'strong_buy', 'buy+', 'buy', 'hold+', 'hold', 'hold-', 'sell', 'sell-', 'strong_sell'], Literal['all', 'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'], str]
            Filter by analyst recommendation. (provider: finviz);
            Filter by consensus analyst action. Multiple comma separated items allowed. (provider: nasdaq)
        signal : Optional[str]
            The Finviz screener signal to use. When no parameters are provided, the screener defaults to 'top_gainers'. Available signals are:
                channel: both support and resistance trendlines are horizontal
                channel_down: both support and resistance trendlines slope downward
                channel_up: both support and resistance trendlines slope upward
                double_bottom: stock with 'W' shape that indicates a bullish reversal in trend
                double_top: stock with 'M' shape that indicates a bearish reversal in trend
                downgrades: stocks downgraded by analysts today
                earnings_after: companies reporting earnings today, after market close
                earnings_before: companies reporting earnings today, before market open
                head_shoulders: chart formation that predicts a bullish-to-bearish trend reversal
                head_shoulders_inverse: chart formation that predicts a bearish-to-bullish trend reversal
                horizontal_sr: horizontal channel of price range between support and resistance trendlines
                major_news: stocks with the highest news coverage today
                most_active: stocks with the highest trading volume today
                most_volatile: stocks with the highest widest high/low trading range today
                multiple_bottom: same as double_bottom hitting more lows
                multiple_top: same as double_top hitting more highs
                new_high: stocks making 52-week high today
                new_low: stocks making 52-week low today
                overbought: stock is becoming overvalued and may experience a pullback.
                oversold: oversold stocks may represent a buying opportunity for investors
                recent_insider_buying: stocks with recent insider buying activity
                recent_insider_selling: stocks with recent insider selling activity
                tl_resistance: once a rising trendline is broken
                tl_support: once a falling trendline is broken
                top_gainers: stocks with the highest price gain percent today
                top_losers: stocks with the highest price percent loss today
                triangle_ascending: upward trendline support and horizontal trendline resistance
                triangle_descending: horizontal trendline support and downward trendline resistance
                unusual_volume: stocks with unusually high volume today - the highest relative volume ratio
                upgrades: stocks upgraded by analysts today
                wedge: upward trendline support, downward trendline resistance (contiunation)
                wedge_down: downward trendline support and downward trendline resistance (reversal)
                wedge_up: upward trendline support and upward trendline resistance (reversal) (provider: finviz)
        preset : Optional[str]
            A configured preset file to use for the query. This overrides all other query parameters except 'metric', and 'limit'. Presets (.ini text files) can be created and modified in the '~/OpenBBUserData/finviz/presets' directory. If the path does not exist, it will be created and populated with the default presets on the first run. Refer to the file, 'screener_template.ini', for the format and options.

        Note: Syntax of parameters in preset files must follow the template file exactly  - i.e, Analyst Recom. = Strong Buy (1) (provider: finviz)
        filters_dict : Optional[Union[Dict, str]]
            A formatted dictionary, or serialized JSON string, of additional filters to apply to the query. This parameter can be used as an alternative to preset files, and is ignored when a preset is supplied. Invalid entries will raise an error. Syntax should follow the 'screener_template.ini' file. (provider: finviz)
        limit : Optional[int]
            The number of data entries to return. (provider: finviz);
            Limit the number of results to return. (provider: fmp);
            Limit the number of results to return. (provider: nasdaq)
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
        country : Optional[Union[str, Literal['all', 'argentina', 'armenia', 'australia', 'austria', 'belgium', 'bermuda', 'brazil', 'canada', 'cayman_islands', 'chile', 'colombia', 'costa_rica', 'curacao', 'cyprus', 'denmark', 'finland', 'france', 'germany', 'greece', 'guernsey', 'hong_kong', 'india', 'indonesia', 'ireland', 'isle_of_man', 'israel', 'italy', 'japan', 'jersey', 'luxembourg', 'macau', 'mexico', 'monaco', 'netherlands', 'norway', 'panama', 'peru', 'philippines', 'puerto_rico', 'russia', 'singapore', 'south_africa', 'south_korea', 'spain', 'sweden', 'switzerland', 'taiwan', 'turkey', 'united_kingdom', 'united_states', 'usa']]]
            Filter by country, as a two-letter country code. (provider: fmp);
            Filter by country. Multiple comma separated items allowed. (provider: nasdaq)
        exsubcategory : Union[Literal['all', 'ngs', 'ngm', 'ncm', 'adr'], str]
            Filter by exchange subcategory.
            NGS - Nasdaq Global Select Market
            NGM - Nasdaq Global Market
            NCM - Nasdaq Capital Market
            ADR - American Depository Receipt
         Multiple comma separated items allowed. (provider: nasdaq)
        region : Union[Literal['all', 'africa', 'asia', 'australia_and_south_pacific', 'caribbean', 'europe', 'middle_east', 'north_america', 'south_america'], str]
            Filter by region. Multiple comma separated items allowed. (provider: nasdaq)

        Returns
        -------
        OBBject
            results : List[EquityScreener]
                Serializable results.
            provider : Optional[Literal['finviz', 'fmp', 'nasdaq']]
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
        earnings_date : Optional[str]
            Earnings date, where 'a' and 'b' mean after and before market close, respectively. (provider: finviz)
        country : Optional[str]
            Country of the company. (provider: finviz);
            The two-letter country abbreviation where the head office is located. (provider: fmp)
        sector : Optional[str]
            Sector of the company. (provider: finviz);
            The sector the ticker belongs to. (provider: fmp)
        industry : Optional[str]
            Industry of the company. (provider: finviz);
            The industry ticker belongs to. (provider: fmp)
        beta : Optional[float]
            Beta of the stock. (provider: finviz);
            The beta of the ETF. (provider: fmp)
        analyst_recommendation : Optional[float]
            Analyst's mean recommendation. (1=Buy 5=Sell). (provider: finviz)
        market_cap : Optional[Union[float, int]]
            Market capitalization of the company. (provider: finviz);
            The market cap of ticker. (provider: fmp);
            Market cap. (provider: nasdaq)
        price : Optional[float]
            Price of a share. (provider: finviz);
            The current price. (provider: fmp)
        change_percent : Optional[float]
            Price change percentage. (provider: finviz);
            1-day percent change in price. (provider: nasdaq)
        change_from_open : Optional[float]
            Price change percentage, from the opening price. (provider: finviz)
        gap : Optional[float]
            Price gap percentage, from the previous close. (provider: finviz)
        volume : Optional[Union[float, int]]
            The trading volume. (provider: finviz, fmp)
        volume_avg : Optional[Union[float, int]]
            3-month average daily volume. (provider: finviz)
        volume_relative : Optional[float]
            Current volume relative to the average. (provider: finviz)
        average_true_range : Optional[float]
            Average true range (14). (provider: finviz)
        price_change_1w : Optional[float]
            One-week price return. (provider: finviz)
        price_change_1m : Optional[float]
            One-month price return. (provider: finviz)
        price_change_3m : Optional[float]
            Three-month price return. (provider: finviz)
        price_change_6m : Optional[float]
            Six-month price return. (provider: finviz)
        price_change_1y : Optional[float]
            One-year price return. (provider: finviz)
        price_change_ytd : Optional[float]
            Year-to-date price return. (provider: finviz)
        volatility_1w : Optional[float]
            One-week volatility. (provider: finviz)
        volatility_1m : Optional[float]
            One-month volatility. (provider: finviz)
        year_high_percent : Optional[float]
            Percent difference from current price to the 52-week high. (provider: finviz)
        year_low_percent : Optional[float]
            Percent difference from current price to the 52-week low. (provider: finviz)
        sma20_percent : Optional[float]
            Percent difference from current price to the 20-day simple moving average. (provider: finviz)
        sma50_percent : Optional[float]
            Percent difference from current price to the 50-day simple moving average. (provider: finviz)
        sma200_percent : Optional[float]
            Percent difference from current price to the 200-day simple moving average. (provider: finviz)
        rsi : Optional[float]
            Relative strength index (14). (provider: finviz)
        shares_outstanding : Optional[Union[float, int]]
            Number of shares outstanding. (provider: finviz)
        shares_float : Optional[Union[float, int]]
            Number of shares available to trade. (provider: finviz)
        short_interest : Optional[float]
            Percent of float reported as short. (provider: finviz)
        short_ratio : Optional[float]
            Short interest ratio (provider: finviz)
        insider_ownership : Optional[float]
            Insider ownership as a percentage. (provider: finviz)
        insider_ownership_change : Optional[float]
            6-month change in insider ownership percentage. (provider: finviz)
        institutional_ownership : Optional[float]
            Institutional ownership as a percentage. (provider: finviz)
        institutional_ownership_change : Optional[float]
            3-month change in institutional ownership percentage. (provider: finviz)
        price_to_earnings : Optional[float]
            Price to earnings ratio. (provider: finviz)
        forward_pe : Optional[float]
            Forward price to earnings ratio. (provider: finviz)
        peg_ratio : Optional[float]
            Price/Earnings-To-Growth (PEG) ratio. (provider: finviz)
        price_to_sales : Optional[float]
            Price to sales ratio. (provider: finviz)
        price_to_book : Optional[float]
            Price to book ratio. (provider: finviz)
        price_to_cash : Optional[float]
            Price to cash ratio. (provider: finviz)
        price_to_fcf : Optional[float]
            Price to free cash flow ratio. (provider: finviz)
        eps_growth_past_1y : Optional[float]
            EPS growth for this year. (provider: finviz)
        eps_growth_next_1y : Optional[float]
            EPS growth next year. (provider: finviz)
        eps_growth_past_5y : Optional[float]
            EPS growth for the previous 5 years. (provider: finviz)
        eps_growth_next_5y : Optional[float]
            EPS growth for the next 5 years. (provider: finviz)
        sales_growth_past_5y : Optional[float]
            Sales growth for the previous 5 years. (provider: finviz)
        dividend_yield : Optional[float]
            Annualized dividend yield. (provider: finviz)
        return_on_assets : Optional[float]
            Return on assets. (provider: finviz)
        return_on_equity : Optional[float]
            Return on equity. (provider: finviz)
        return_on_investment : Optional[float]
            Return on investment. (provider: finviz)
        current_ratio : Optional[float]
            Current ratio. (provider: finviz)
        quick_ratio : Optional[float]
            Quick ratio. (provider: finviz)
        long_term_debt_to_equity : Optional[float]
            Long term debt to equity ratio. (provider: finviz)
        debt_to_equity : Optional[float]
            Total debt to equity ratio. (provider: finviz)
        gross_margin : Optional[float]
            Gross margin. (provider: finviz)
        operating_margin : Optional[float]
            Operating margin. (provider: finviz)
        profit_margin : Optional[float]
            Profit margin. (provider: finviz)
        last_annual_dividend : Optional[float]
            The last annual amount dividend paid. (provider: fmp)
        exchange : Optional[str]
            The exchange code the asset trades on. (provider: fmp)
        exchange_name : Optional[str]
            The full name of the primary exchange. (provider: fmp)
        is_etf : Optional[Literal[True, False]]
            Whether the ticker is an ETF. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        last_price : Optional[float]
            Last sale price. (provider: nasdaq)
        change : Optional[float]
            1-day change in price. (provider: nasdaq)

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
                        ("finviz", "fmp", "nasdaq"),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "metric": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "overview",
                                "valuation",
                                "financial",
                                "ownership",
                                "performance",
                                "technical",
                            ],
                        }
                    },
                    "exchange": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": ["all", "amex", "nasdaq", "nyse"],
                        },
                        "nasdaq": {"multiple_items_allowed": True, "choices": None},
                    },
                    "index": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": ["all", "dow", "sp500", "nasdaq", "russell"],
                        }
                    },
                    "sector": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "all",
                                "energy",
                                "materials",
                                "industrials",
                                "consumer_cyclical",
                                "consumer_defensive",
                                "financial",
                                "healthcare",
                                "technology",
                                "communication_services",
                                "utilities",
                                "real_estate",
                            ],
                        },
                        "nasdaq": {"multiple_items_allowed": True, "choices": None},
                    },
                    "industry": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "all",
                                "stocks_only",
                                "etf",
                                "advertising_agencies",
                                "aerospace_defense",
                                "agricultural_inputs",
                                "airlines",
                                "airports_airservices",
                                "aluminum",
                                "apparel_manufacturing",
                                "apparel_retail",
                                "asset_management",
                                "auto_manufacturers",
                                "auto_parts",
                                "auto_dealerships",
                                "banks_diversified",
                                "banks_regional",
                                "beverages_brewers",
                                "beverages_nonalcoholic",
                                "beverages_wineries_distilleries",
                                "biotechnology",
                                "broadcasting",
                                "building_materials",
                                "building_products_equipment",
                                "business_equipment_supplies",
                                "capital_markets",
                                "chemicals",
                                "closed_end_fund_debt",
                                "closed_end_fund_equity",
                                "closed_end_fund_foreign",
                                "coking_coal",
                                "communication_equipment",
                                "computer_hardware",
                                "confectioners",
                                "conglomerates",
                                "consulting_services",
                                "consumer_electronics",
                                "copper",
                                "credit_services",
                                "department_stores",
                                "diagnostics_research",
                                "discount_stores",
                                "drug_manufacturers_general",
                                "drug_manufacturers_specialty_generic",
                                "education_training_services",
                                "electrical_equipment_parts",
                                "electronic_components",
                                "electronic_gaming_multimedia",
                                "electronics_computer_distribution",
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
                                "health_care_plans",
                                "health_information_services",
                                "home_improvement_retail",
                                "household_personal_products",
                                "industrial_distribution",
                                "information_technology_services",
                                "infrastructure_operations",
                                "insurance_brokers",
                                "insurance_diversified",
                                "insurance_life",
                                "insurance_property_casualty",
                                "insurance_reinsurance",
                                "insurance_specialty",
                                "integrated_freight_logistics",
                                "internet_content_information",
                                "internet_retail",
                                "leisure",
                                "lodging",
                                "lumber_wood_production",
                                "luxury_goods",
                                "marine_shipping",
                                "medical_care_facilities",
                                "medical_devices",
                                "medical_distribution",
                                "medical_instruments_supplies",
                                "metal_fabrication",
                                "mortgage_finance",
                                "oil_gas_drilling",
                                "oil_gas_ep",
                                "oil_gas_equipment_services",
                                "oil_gas_integrated",
                                "oil_gas_midstream",
                                "oil_gas_refining_marketing",
                                "other_industrial_metals_mining",
                                "other_precious_metals_mining",
                                "packaged_foods",
                                "packaging_containers",
                                "paper_paper_products",
                                "personal_services",
                                "pharmaceutical_retailers",
                                "pollution_treatment_controls",
                                "publishing",
                                "railroads",
                                "real_estate_development",
                                "real_estate_diversified",
                                "real_estate_services",
                                "recreational_vehicles",
                                "reit_diversified",
                                "reit_health_care_facilities",
                                "reit_hotel_motel",
                                "reit_industrial",
                                "reit_mortgage",
                                "reit_office",
                                "reit_residential",
                                "reit_retail",
                                "reit_specialty",
                                "rental_leasing_services",
                                "residential_construction",
                                "resorts_casinos",
                                "restaurants",
                                "scientific_technical_instruments",
                                "security_protection_services",
                                "semiconductor_equipment_materials",
                                "semiconductors",
                                "shell_companies",
                                "silver",
                                "software_application",
                                "software_infrastructure",
                                "solar",
                                "specialty_business_services",
                                "specialty_chemicals",
                                "specialty_industrial_machinery",
                                "specialty_retail",
                                "staffing_employment_services",
                                "steel",
                                "telecom_services",
                                "textile_manufacturing",
                                "thermal_coal",
                                "tobacco",
                                "tools_accessories",
                                "travel_services",
                                "trucking",
                                "uranium",
                                "utilities_diversified",
                                "utilities_independent_power_producers",
                                "utilities_regulated_electric",
                                "utilities_regulated_gas",
                                "utilities_regulated_water",
                                "utilities_renewable",
                                "waste_management",
                            ],
                        }
                    },
                    "mktcap": {
                        "nasdaq": {"multiple_items_allowed": True, "choices": None}
                    },
                    "recommendation": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "all",
                                "strong_buy",
                                "buy+",
                                "buy",
                                "hold+",
                                "hold",
                                "hold-",
                                "sell",
                                "sell-",
                                "strong_sell",
                            ],
                        },
                        "nasdaq": {"multiple_items_allowed": True, "choices": None},
                    },
                    "signal": {
                        "finviz": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "channel",
                                "channel_down",
                                "channel_up",
                                "double_bottom",
                                "double_top",
                                "downgrades",
                                "earnings_after",
                                "earnings_before",
                                "head_shoulders",
                                "head_shoulders_inverse",
                                "horizontal_sr",
                                "major_news",
                                "most_active",
                                "most_volatile",
                                "multiple_bottom",
                                "multiple_top",
                                "new_high",
                                "new_low",
                                "overbought",
                                "oversold",
                                "recent_insider_buying",
                                "recent_insider_selling",
                                "tl_resistance",
                                "tl_support",
                                "top_gainers",
                                "top_losers",
                                "triangle_ascending",
                                "triangle_descending",
                                "unusual_volume",
                                "upgrades",
                                "wedge",
                                "wedge_down",
                                "wedge_up",
                            ],
                        }
                    },
                    "country": {
                        "nasdaq": {"multiple_items_allowed": True, "choices": None}
                    },
                    "exsubcategory": {
                        "nasdaq": {"multiple_items_allowed": True, "choices": None}
                    },
                    "region": {
                        "nasdaq": {"multiple_items_allowed": True, "choices": None}
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
            Optional[Literal["cboe", "intrinio", "nasdaq", "sec", "tmx", "tradier"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, intrinio, nasdaq, sec, tmx, tradier."
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
        provider : Optional[Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, intrinio, nasdaq, sec, tmx, tradier.
        use_cache : bool
            Whether to use the cache or not. (provider: cboe, sec);
            Whether to use a cached request. The list of companies is cached for two days. (provider: tmx)
        active : bool
            When true, return companies that are actively traded (having stock prices within the past 14 days). When false, return companies that are not actively traded or never have been traded. (provider: intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)
        is_etf : Optional[bool]
            If True, returns ETFs. (provider: nasdaq)
        is_fund : bool
            Whether to direct the search to the list of mutual funds and ETFs. (provider: sec)

        Returns
        -------
        OBBject
            results : List[EquitySearch]
                Serializable results.
            provider : Optional[Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier']]
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
        dpm_name : Optional[str]
            Name of the primary market maker. (provider: cboe)
        post_station : Optional[str]
            Post and station location on the CBOE trading floor. (provider: cboe)
        cik : Optional[str]
            ;
            Central Index Key (provider: sec)
        lei : Optional[str]
            The Legal Entity Identifier (LEI) of the company. (provider: intrinio)
        intrinio_id : Optional[str]
            The Intrinio ID of the company. (provider: intrinio)
        nasdaq_traded : Optional[str]
            Is Nasdaq traded? (provider: nasdaq)
        exchange : Optional[str]
            Primary Exchange (provider: nasdaq);
            Exchange where the security is listed. (provider: tradier)
        market_category : Optional[str]
            Market Category (provider: nasdaq)
        etf : Optional[str]
            Is ETF? (provider: nasdaq)
        round_lot_size : Optional[float]
            Round Lot Size (provider: nasdaq)
        test_issue : Optional[str]
            Is test Issue? (provider: nasdaq)
        financial_status : Optional[str]
            Financial Status (provider: nasdaq)
        cqs_symbol : Optional[str]
            CQS Symbol (provider: nasdaq)
        nasdaq_symbol : Optional[str]
            NASDAQ Symbol (provider: nasdaq)
        next_shares : Optional[str]
            Is NextShares? (provider: nasdaq)
        security_type : Optional[Literal['stock', 'option', 'etf', 'index', 'mutual_fund']]
            Type of security. (provider: tradier)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.search(provider='intrinio')
        >>> obb.equity.search(query='AAPL', is_symbol=False, use_cache=True, provider='nasdaq')
        """  # noqa: E501

        return self._run(
            "/equity/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.search",
                        ("cboe", "intrinio", "nasdaq", "sec", "tmx", "tradier"),
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
