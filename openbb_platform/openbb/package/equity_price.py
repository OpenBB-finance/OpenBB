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
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: fmp, polygon, tiingo, yfinance."
            ),
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
        provider: Optional[
            Literal["fmp", "intrinio", "polygon", "tiingo", "yfinance"]
        ] = None,
        **kwargs
    ) -> OBBject:
        """Equity Historical price. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: fmp, polygon, tiingo, yfinance.
        interval : Optional[str]
            Time interval of the data to return.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'tiingo', 'yfinanc...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
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
        adjusted : bool
            Output time series is adjusted by historical split and dividend events. (provider: polygon);
            Adjust all OHLC data automatically. (provider: yfinance)
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
            provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']]
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
        volume : Optional[Union[float, int]]
            The trading volume.
        vwap : Optional[float]
            Volume Weighted Average Price over the period.
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        adj_close : Optional[float]
            The adjusted close price. (provider: fmp);
            Adjusted closing price during the period. (provider: intrinio);
            Adjusted closing price during the period. (provider: tiingo)
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
                    "provider": self._get_provider(
                        provider,
                        "/equity/price/historical",
                        ("fmp", "intrinio", "polygon", "tiingo", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "interval": interval,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {
                        "multiple_items_allowed": [
                            "fmp",
                            "polygon",
                            "tiingo",
                            "yfinance",
                        ]
                    }
                },
            )
        )

    @validate
    def nbbo(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
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
                    "provider": self._get_provider(
                        provider,
                        "/equity/price/nbbo",
                        ("polygon",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def performance(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
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
                    "provider": self._get_provider(
                        provider,
                        "/equity/price/performance",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
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
                description="Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed: fmp, intrinio, yfinance."
            ),
        ],
        provider: Optional[Literal["fmp", "intrinio", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Equity Quote. Load stock data for a specific ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. This endpoint will accept multiple symbols separated by commas. Multiple items allowed: fmp, intrinio, yfinance.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        source : Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip']
            Source of the data. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[EquityQuote]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
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
        asset_type : Optional[str]
            Type of asset - i.e, stock, ETF, etc.
        name : Optional[str]
            Name of the company or asset.
        exchange : Optional[str]
            The name or symbol of the venue where the data is from.
        bid : Optional[float]
            Price of the top bid order.
        bid_size : Optional[int]
            This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price.
        bid_exchange : Optional[str]
            The specific trading venue where the purchase order was placed.
        ask : Optional[float]
            Price of the top ask order.
        ask_size : Optional[int]
            This represents the number of round lot orders at the given price. The normal round lot size is 100 shares. A size of 2 means there are 200 shares available at the given price.
        ask_exchange : Optional[str]
            The specific trading venue where the sale order was placed.
        quote_conditions : Optional[Union[str, int, List[str], List[int]]]
            Conditions or condition codes applicable to the quote.
        quote_indicators : Optional[Union[str, int, List[str], List[int]]]
            Indicators or indicator codes applicable to the participant quote related to the price bands for the issue, or the affect the quote has on the NBBO.
        sales_conditions : Optional[Union[str, int, List[str], List[int]]]
            Conditions or condition codes applicable to the sale.
        sequence_number : Optional[int]
            The sequence number represents the sequence in which message events happened. These are increasing and unique per ticker symbol, but will not always be sequential (e.g., 1, 2, 6, 9, 10, 11).
        market_center : Optional[str]
            The ID of the UTP participant that originated the message.
        participant_timestamp : Optional[datetime]
            Timestamp for when the quote was generated by the exchange.
        trf_timestamp : Optional[datetime]
            Timestamp for when the TRF (Trade Reporting Facility) received the message.
        sip_timestamp : Optional[datetime]
            Timestamp for when the SIP (Security Information Processor) received the message from the exchange.
        last_price : Optional[float]
            Price of the last trade.
        last_tick : Optional[str]
            Whether the last sale was an up or down tick.
        last_size : Optional[int]
            Size of the last trade.
        last_timestamp : Optional[datetime]
            Date and Time when the last price was recorded.
        open : Optional[float]
            The open price.
        high : Optional[float]
            The high price.
        low : Optional[float]
            The low price.
        close : Optional[float]
            The close price.
        volume : Optional[Union[float, int]]
            The trading volume.
        exchange_volume : Optional[Union[float, int]]
            Volume of shares exchanged during the trading day on the specific exchange.
        prev_close : Optional[float]

        change : Optional[float]
            Change in price from previous close.
        change_percent : Optional[float]
            Change in price as a normalized percentage.
        year_high : Optional[float]
            The one year high (52W High).
        year_low : Optional[float]
            The one year low (52W Low).
        price_avg50 : Optional[float]
            50 day moving average price. (provider: fmp)
        price_avg200 : Optional[float]
            200 day moving average price. (provider: fmp)
        avg_volume : Optional[int]
            Average volume over the last 10 trading days. (provider: fmp)
        market_cap : Optional[float]
            Market cap of the company. (provider: fmp)
        shares_outstanding : Optional[int]
            Number of shares outstanding. (provider: fmp)
        eps : Optional[float]
            Earnings per share. (provider: fmp)
        pe : Optional[float]
            Price earnings ratio. (provider: fmp)
        earnings_announcement : Optional[Union[datetime, str]]
            Upcoming earnings announcement date. (provider: fmp)
        is_darkpool : Optional[bool]
            Whether or not the current trade is from a darkpool. (provider: intrinio)
        source : Optional[str]
            Source of the Intrinio data. (provider: intrinio)
        updated_on : Optional[datetime]
            Date and Time when the data was last updated. (provider: intrinio)
        security : Optional[openbb_intrinio.utils.references.IntrinioSecurity]
            Security details related to the quote. (provider: intrinio)
        ma_50d : Optional[float]
            50-day moving average price. (provider: yfinance)
        ma_200d : Optional[float]
            200-day moving average price. (provider: yfinance)
        volume_average : Optional[float]
            Average daily trading volume. (provider: yfinance)
        volume_average_10d : Optional[float]
            Average daily trading volume in the last 10 days. (provider: yfinance)
        currency : Optional[str]
            Currency of the price. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.price.quote(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/price/quote",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/price/quote",
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
