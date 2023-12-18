### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_price(Container):
    """/equity/price
    historical
    nbbo
    performance
    quote
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        interval: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Time interval of the data to return."),
        ] = "1d",
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        chart: bool = False,
        provider: Optional[
            Literal[
                "alpha_vantage",
                "cboe",
                "fmp",
                "intrinio",
                "polygon",
                "tiingo",
                "yfinance",
            ]
        ] = None,
        **kwargs
    ) -> OBBject:
        """Equity Historical price. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        interval : Optional[str]
            Time interval of the data to return.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'pol...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'alpha_vantage' if there is
            no default.
        adjusted : Optional[bool]
            Output time series is adjusted by historical split and dividend events. (provider: alpha_vantage, polygon);
            Adjust all OHLC data automatically. (provider: yfinance)
        extended_hours : Optional[bool]
            Extended trading hours during pre-market and after-hours.Only available for intraday data. (provider: alpha_vantage)
        month : Optional[str]
            Query a specific month in history (in YYYY-MM format). (provider: alpha_vantage)
        output_size : Optional[Literal['compact', 'full']]
            Compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter is not specified, or the full intraday data for aspecific month in history if the month parameter is specified. (provider: alpha_vantage)
        use_cache : bool
            When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe)
        limit : Optional[Union[Annotated[int, Ge(ge=0)], int]]
            Number of days to look back (Only for interval 1d). (provider: fmp);
            The number of data entries to return. (provider: polygon)
        start_time : Optional[datetime.time]
            Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        end_time : Optional[datetime.time]
            Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio)
        timezone : str
            Timezone of the data, in the IANA format (Continent/City). (provider: intrinio)
        source : Literal['realtime', 'delayed', 'nasdaq_basic']
            The source of the data. (provider: intrinio)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        include : bool
            Include Dividends and Stock Splits in results. (provider: yfinance)
        ignore_tz : bool
            When combining from different timezones, ignore that part of datetime. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[EquityHistorical]
                Serializable results.
            provider : Optional[Literal['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EquityHistorical
        ----------------
        date : Union[date, datetime]
            The date of the data.
        open : float
            The open price.
        high : float
            The high price.
        low : float
            The low price.
        close : float
            The close price.
        volume : Union[float, int]
            The trading volume.
        vwap : Optional[float]
            Volume Weighted Average Price over the period.
        adj_close : Optional[Union[Annotated[float, Gt(gt=0)], float]]
            The adjusted close price. (provider: alpha_vantage, fmp);
            Adjusted closing price during the period. (provider: intrinio);
            Adjusted closing price during the period. (provider: tiingo)
        dividend_amount : Optional[Annotated[float, Ge(ge=0)]]
            Dividend amount paid for the corresponding date. (provider: alpha_vantage)
        split_coefficient : Optional[Annotated[float, Ge(ge=0)]]
            Split coefficient for the corresponding date. (provider: alpha_vantage)
        calls_volume : Optional[int]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[int]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[int]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp, intrinio)
        change_percent : Optional[float]
            Change % in the price of the symbol. (provider: fmp)
        change_over_time : Optional[float]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        close_time : Optional[datetime]
            The timestamp that represents the end of the interval span. (provider: intrinio)
        interval : Optional[str]
            The data time frequency. (provider: intrinio)
        average : Optional[float]
            Average trade price of an individual equity during the interval. (provider: intrinio)
        intra_period : Optional[bool]
            If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period (provider: intrinio)
        adj_open : Optional[float]
            Adjusted open price during the period. (provider: intrinio, tiingo)
        adj_high : Optional[float]
            Adjusted high price during the period. (provider: intrinio, tiingo)
        adj_low : Optional[float]
            Adjusted low price during the period. (provider: intrinio, tiingo)
        adj_volume : Optional[float]
            Adjusted volume during the period. (provider: intrinio, tiingo)
        factor : Optional[float]
            factor by which to multiply equity prices before this date, in order to calculate historically-adjusted equity prices. (provider: intrinio)
        split_ratio : Optional[float]
            Ratio of the equity split, if a equity split occurred. (provider: intrinio, tiingo)
        dividend : Optional[float]
            Dividend amount, if a dividend was paid. (provider: intrinio, tiingo)
        percent_change : Optional[float]
            Percent change in the price of the symbol from the previous day. (provider: intrinio)
        fifty_two_week_high : Optional[float]
            52 week high price for the symbol. (provider: intrinio)
        fifty_two_week_low : Optional[float]
            52 week low price for the symbol. (provider: intrinio)
        transactions : Optional[Annotated[int, Gt(gt=0)]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.historical(symbol="AAPL", interval="1d")
        """  # noqa: E501

        return self._run(
            "/equity/price/historical",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                    "interval": interval,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                chart=chart,
            )
        )

    @validate
    def nbbo(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["polygon"]] = None,
        **kwargs
    ) -> OBBject:
        """Equity NBBO. Load National Best Bid and Offer for a specific equity.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'polygon' if there is
            no default.
        limit : int
            The number of data entries to return. Up to ten million records will be returned. Pagination occurs in groups of 50,000. Remaining limit values will always return 50,000 more records unless it is the last page. High volume tickers will require multiple max requests for a single day's NBBO records. Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV. Splitting large requests into chunks is recommended for full-day requests of high-volume symbols. (provider: polygon)
        date : Optional[datetime.date]
            A specific date to get data for. Use bracketed the timestamp parameters to specify exact time ranges. (provider: polygon)
        timestamp_lt : Optional[Union[datetime.datetime, str]]

                    Query by datetime, less than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_gt : Optional[Union[datetime.datetime, str]]

                    Query by datetime, greater than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_lte : Optional[Union[datetime.datetime, str]]

                    Query by datetime, less than or equal to.
                    Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)
        timestamp_gte : Optional[Union[datetime.datetime, str]]

                    Query by datetime, greater than or equal to.
                    Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
                    YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
                 (provider: polygon)

        Returns
        -------
        OBBject
            results : List[EquityNBBO]
                Serializable results.
            provider : Optional[Literal['polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EquityNBBO
        ----------
        ask_exchange : str
            The exchange ID for the ask.
        ask : float
            The last ask price.
        ask_size : int

                The ask size. This represents the number of round lot orders at the given ask price.
                The normal round lot size is 100 shares.
                An ask size of 2 means there are 200 shares available to purchase at the given ask price.

        bid_size : int
            The bid size in round lots.
        bid : float
            The last bid price.
        bid_exchange : str
            The exchange ID for the bid.
        tape : Optional[str]
            The exchange tape. (provider: polygon)
        conditions : Optional[Union[str, List[int], List[str]]]
            A list of condition codes. (provider: polygon)
        indicators : Optional[List]
            A list of indicator codes. (provider: polygon)
        sequence_num : Optional[int]

                    The sequence number represents the sequence in which message events happened.
                    These are increasing and unique per ticker symbol, but will not always be sequential
                    (e.g., 1, 2, 6, 9, 10, 11)
                 (provider: polygon)
        participant_timestamp : Optional[datetime]

                    The nanosecond accuracy Participant/Exchange Unix Timestamp.
                    This is the timestamp of when the quote was actually generated at the exchange.
                 (provider: polygon)
        sip_timestamp : Optional[datetime]

                    The nanosecond accuracy SIP Unix Timestamp.
                    This is the timestamp of when the SIP received this quote from the exchange which produced it.
                 (provider: polygon)
        trf_timestamp : Optional[datetime]

                    The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp.
                    This is the timestamp of when the trade reporting facility received this quote.
                 (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.nbbo(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/price/nbbo",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def performance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Price performance as a return, over different periods.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[PricePerformance]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PricePerformance
        ----------------
        one_day : Optional[float]
            One-day return.
        wtd : Optional[float]
            Week to date return.
        one_week : Optional[float]
            One-week return.
        mtd : Optional[float]
            Month to date return.
        one_month : Optional[float]
            One-month return.
        qtd : Optional[float]
            Quarter to date return.
        three_month : Optional[float]
            Three-month return.
        six_month : Optional[float]
            Six-month return.
        ytd : Optional[float]
            Year to date return.
        one_year : Optional[float]
            One-year return.
        three_year : Optional[float]
            Three-year return.
        five_year : Optional[float]
            Five-year return.
        ten_year : Optional[float]
            Ten-year return.
        max : Optional[float]
            Return from the beginning of the time series.
        symbol : Optional[str]
            The ticker symbol. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.performance(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/price/performance",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def quote(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. In this case, the comma separated list of symbols."
            ),
        ],
        provider: Optional[Literal["cboe", "fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Equity Quote. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. In this case, the comma separated list of symbols.
        provider : Optional[Literal['cboe', 'fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        use_cache : bool
            When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe)
        source : Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip']
            Source of the data. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[EquityQuote]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EquityQuote
        -----------
        symbol : str
            Symbol representing the entity requested in the data.
        type : Optional[str]
            Type of asset. (provider: cboe)
        name : Optional[str]
            Name of the company or asset. (provider: cboe, fmp)
        bid : Optional[float]
            Current bid price. (provider: cboe);
            Price of the top bid order. (provider: intrinio)
        bid_size : Optional[Union[float, int]]
            Bid lot size. (provider: cboe);
            Size of the top bid order. (provider: intrinio)
        ask : Optional[float]
            Current ask price. (provider: cboe);
            Price of the top ask order. (provider: intrinio)
        ask_size : Optional[Union[float, int]]
            Ask lot size. (provider: cboe);
            Size of the top ask order. (provider: intrinio)
        last_price : Optional[float]
            Price of the last trade. (provider: cboe, intrinio)
        tick : Optional[str]
            Whether the last sale was an up or down tick. (provider: cboe)
        last_time : Optional[datetime]
            Time of the last trade. (provider: cboe);
            Date and Time when the last trade occurred. (provider: intrinio)
        open : Optional[float]
            Opening price. (provider: cboe);
            Opening price of the equity in the current trading day. (provider: fmp);
            Open price for the trading day. (provider: intrinio)
        high : Optional[float]
            High price. (provider: cboe);
            High price for the trading day. (provider: intrinio)
        low : Optional[float]
            Low price. (provider: cboe);
            Low price for the trading day. (provider: intrinio)
        close : Optional[float]
            Closing price. (provider: cboe);
            Closing price for the trading day (IEX source only). (provider: intrinio)
        prev_close : Optional[float]
            Previous closing price. (provider: cboe)
        price_change : Optional[float]
            Change in price. (provider: cboe)
        price_change_percent : Optional[float]
            Change in price as a normalized percentage value. (provider: cboe)
        price_annual_high : Optional[float]
            The annual high price of the stock. (provider: cboe)
        price_annual_low : Optional[float]
            The annual low price of the stock. (provider: cboe)
        volume : Optional[int]
            Stock volume for the current trading day. (provider: cboe);
            Volume of the equity in the current trading day. (provider: fmp)
        iv30 : Optional[float]
            The 30-day implied volatility of the stock. (provider: cboe)
        iv30_change : Optional[float]
            Change in 30-day implied volatility of the stock. (provider: cboe)
        iv30_change_percent : Optional[float]
            Change in 30-day implied volatility of the stock as a normalized percentage value. (provider: cboe)
        iv30_annual_high : Optional[float]
            The 1-year high of implied volatility. (provider: cboe)
        hv30_annual_high : Optional[float]
            The 1-year high of realized volatility. (provider: cboe)
        iv30_annual_low : Optional[float]
            The 1-year low of implied volatility. (provider: cboe)
        hv30_annual_low : Optional[float]
            The 1-year low of realized volatility. (provider: cboe)
        iv60_annual_high : Optional[float]
            The 60-day high of implied volatility. (provider: cboe)
        hv60_annual_high : Optional[float]
            The 60-day high of realized volatility. (provider: cboe)
        iv60_annual_low : Optional[float]
            The 60-day low of implied volatility. (provider: cboe)
        hv60_annual_low : Optional[float]
            The 60-day low of realized volatility. (provider: cboe)
        iv90_annual_high : Optional[float]
            The 90-day high of implied volatility. (provider: cboe)
        hv90_annual_high : Optional[float]
            The 90-day high of realized volatility. (provider: cboe)
        price : Optional[float]
            Current trading price of the equity. (provider: fmp)
        changes_percentage : Optional[float]
            Change percentage of the equity price. (provider: fmp)
        change : Optional[float]
            Change in the equity price. (provider: fmp)
        year_high : Optional[float]
            Highest price of the equity in the last 52 weeks. (provider: fmp)
        year_low : Optional[float]
            Lowest price of the equity in the last 52 weeks. (provider: fmp)
        market_cap : Optional[float]
            Market cap of the company. (provider: fmp)
        price_avg50 : Optional[float]
            50 days average price of the equity. (provider: fmp)
        price_avg200 : Optional[float]
            200 days average price of the equity. (provider: fmp)
        avg_volume : Optional[int]
            Average volume of the equity in the last 10 trading days. (provider: fmp)
        exchange : Optional[str]
            Exchange the equity is traded on. (provider: fmp)
        previous_close : Optional[float]
            Previous closing price of the equity. (provider: fmp)
        eps : Optional[float]
            Earnings per share of the equity. (provider: fmp)
        pe : Optional[float]
            Price earnings ratio of the equity. (provider: fmp)
        earnings_announcement : Optional[str]
            Earnings announcement date of the equity. (provider: fmp)
        shares_outstanding : Optional[int]
            Number of shares outstanding of the equity. (provider: fmp)
        last_size : Optional[int]
            Size of the last trade. (provider: intrinio)
        exchange_volume : Optional[int]
            Number of shares exchanged during the trading day on the exchange. (provider: intrinio)
        market_volume : Optional[int]
            Number of shares exchanged during the trading day for the whole market. (provider: intrinio)
        source : Optional[str]
            Source of the data. (provider: intrinio)
        is_darkpool : Optional[bool]
            Whether or not the current trade is from a darkpool. (provider: intrinio)
        listing_venue : Optional[str]
            Listing venue where the trade took place (SIP source only). (provider: intrinio)
        sales_conditions : Optional[str]
            Indicates any sales condition modifiers associated with the trade. (provider: intrinio)
        quote_conditions : Optional[str]
            Indicates any quote condition modifiers associated with the trade. (provider: intrinio)
        market_center_code : Optional[str]
            Market center character code. (provider: intrinio)
        messages : Optional[List[str]]
            Messages associated with the current quote. (provider: intrinio)
        updated_on : Optional[datetime]
            Date and Time when the data was last updated. (provider: intrinio)
        security : Optional[Dict[str, Any]]
            Reference and Intrinio codes for the security. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.quote(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/price/quote",
            **filter_inputs(
                provider_choices={
                    "provider": provider,
                },
                standard_params={
                    "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                },
                extra_params=kwargs,
            )
        )
