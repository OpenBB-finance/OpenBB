### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Literal, Optional

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_derivatives_options(Container):
    """/derivatives/options
    chains
    snapshots
    unusual
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def chains(
        self,
        symbol: Annotated[str, OpenBBField(description="Symbol to get data for.")],
        provider: Annotated[
            Optional[Literal["cboe", "intrinio", "tmx", "tradier", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, intrinio, tmx, tradier, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['cboe', 'intrinio', 'tmx', 'tradier', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, intrinio, tmx, tradier, yfinance.
        use_cache : bool
            When True, the company directories will be cached for24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe);
            Caching is used to validate the supplied ticker symbol, or if a historical EOD chain is requested. To bypass, set to False. (provider: tmx)
        date : Optional[datetime.date]
            The end-of-day date for options chains data. (provider: intrinio);
            A specific date to get data for. (provider: tmx)
        option_type : Optional[Literal['call', 'put']]
            The option type, call or put, 'None' is both (default). (provider: intrinio)
        moneyness : Literal['otm', 'itm', 'all']
            Return only contracts that are in or out of the money, default is 'all'. Parameter is ignored when a date is supplied. (provider: intrinio)
        strike_gt : Optional[int]
            Return options with a strike price greater than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        strike_lt : Optional[int]
            Return options with a strike price less than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        volume_gt : Optional[int]
            Return options with a volume greater than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        volume_lt : Optional[int]
            Return options with a volume less than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        oi_gt : Optional[int]
            Return options with an open interest greater than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        oi_lt : Optional[int]
            Return options with an open interest less than the given value. Parameter is ignored when a date is supplied. (provider: intrinio)
        model : Literal['black_scholes', 'bjerk']
            The pricing model to use for options chains data, default is 'black_scholes'. Parameter is ignored when a date is supplied. (provider: intrinio)
        show_extended_price : bool
            Whether to include OHLC type fields, default is True. Parameter is ignored when a date is supplied. (provider: intrinio)
        include_related_symbols : bool
            Include related symbols that end in a 1 or 2 because of a corporate action, default is False. (provider: intrinio)

        Returns
        -------
        OBBject
            results : OptionsChains
                Serializable results.
            provider : Optional[Literal['cboe', 'intrinio', 'tmx', 'tradier', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsChains
        -------------
        underlying_symbol : List[Optional[str]]
            Underlying symbol for the option.
        underlying_price : List[Optional[float]]
            Price of the underlying stock.
        contract_symbol : List[str]
            Contract symbol for the option.
        eod_date : List[Optional[date]]
            Date for which the options chains are returned.
        expiration : List[date]
            Expiration date of the contract.
        dte : List[Optional[int]]
            Days to expiration of the contract.
        strike : List[float]
            Strike price of the contract.
        option_type : List[str]
            Call or Put.
        open_interest : List[Optional[int]]
            Open interest on the contract.
        volume : List[Optional[int]]
            The trading volume.
        theoretical_price : List[Optional[float]]
            Theoretical value of the option.
        last_trade_price : List[Optional[float]]
            Last trade price of the option.
        last_trade_size : List[Optional[int]]
            Last trade size of the option.
        last_trade_time : List[Optional[datetime]]
            The timestamp of the last trade.
        tick : List[Optional[str]]
            Whether the last tick was up or down in price.
        bid : List[Optional[float]]
            Current bid price for the option.
        bid_size : List[Optional[int]]
            Bid size for the option.
        bid_time : List[Optional[datetime]]
            The timestamp of the bid price.
        bid_exchange : List[Optional[str]]
            The exchange of the bid price.
        ask : List[Optional[float]]
            Current ask price for the option.
        ask_size : List[Optional[int]]
            Ask size for the option.
        ask_time : List[Optional[datetime]]
            The timestamp of the ask price.
        ask_exchange : List[Optional[str]]
            The exchange of the ask price.
        mark : List[Optional[float]]
            The mid-price between the latest bid and ask.
        open : List[Optional[float]]
            The open price.
        open_bid : List[Optional[float]]
            The opening bid price for the option that day.
        open_ask : List[Optional[float]]
            The opening ask price for the option that day.
        high : List[Optional[float]]
            The high price.
        bid_high : List[Optional[float]]
            The highest bid price for the option that day.
        ask_high : List[Optional[float]]
            The highest ask price for the option that day.
        low : List[Optional[float]]
            The low price.
        bid_low : List[Optional[float]]
            The lowest bid price for the option that day.
        ask_low : List[Optional[float]]
            The lowest ask price for the option that day.
        close : List[Optional[float]]
            The close price.
        close_size : List[Optional[int]]
            The closing trade size for the option that day.
        close_time : List[Optional[datetime]]
            The time of the closing price for the option that day.
        close_bid : List[Optional[float]]
            The closing bid price for the option that day.
        close_bid_size : List[Optional[int]]
            The closing bid size for the option that day.
        close_bid_time : List[Optional[datetime]]
            The time of the bid closing price for the option that day.
        close_ask : List[Optional[float]]
            The closing ask price for the option that day.
        close_ask_size : List[Optional[int]]
            The closing ask size for the option that day.
        close_ask_time : List[Optional[datetime]]
            The time of the ask closing price for the option that day.
        prev_close : List[Optional[float]]
            The previous close price.
        change : List[Optional[float]]
            The change in the price of the option.
        change_percent : List[Optional[float]]
            Change, in normalized percentage points, of the option.
        implied_volatility : List[Optional[float]]
            Implied volatility of the option.
        delta : List[Optional[float]]
            Delta of the option.
        gamma : List[Optional[float]]
            Gamma of the option.
        theta : List[Optional[float]]
            Theta of the option.
        vega : List[Optional[float]]
            Vega of the option.
        rho : List[Optional[float]]
            Rho of the option.
        transactions : List[Optional[int]]
            Number of transactions for the contract. (provider: tmx)
        total_value : List[Optional[float]]
            Total value of the transactions. (provider: tmx)
        settlement_price : List[Optional[float]]
            Settlement price on that date. (provider: tmx)
        phi : List[Optional[float]]
            Phi of the option. The sensitivity of the option relative to dividend yield. (provider: tradier)
        bid_iv : List[Optional[float]]
            Implied volatility of the bid price. (provider: tradier)
        ask_iv : List[Optional[float]]
            Implied volatility of the ask price. (provider: tradier)
        orats_final_iv : List[Optional[float]]
            ORATS final implied volatility of the option, updated once per hour. (provider: tradier)
        year_high : List[Optional[float]]
            52-week high price of the option. (provider: tradier)
        year_low : List[Optional[float]]
            52-week low price of the option. (provider: tradier)
        contract_size : List[Optional[int]]
            Size of the contract. (provider: tradier)
        greeks_time : List[Optional[datetime]]
            Timestamp of the last greeks update. Greeks/IV data is updated once per hour. (provider: tradier)
        in_the_money : List[Optional[bool]]
            Whether the option is in the money. (provider: yfinance)
        currency : List[Optional[str]]
            Currency of the option. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.derivatives.options.chains(symbol='AAPL', provider='intrinio')
        >>> # Use the "date" parameter to get the end-of-day-data for a specific date, where supported.
        >>> obb.derivatives.options.chains(symbol='AAPL', date='2023-01-25', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/derivatives/options/chains",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "derivatives.options.chains",
                        ("cboe", "intrinio", "tmx", "tradier", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def snapshots(
        self,
        provider: Annotated[
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get a snapshot of the options market universe.

        Parameters
        ----------
        provider : Optional[Literal['intrinio']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio.
        date : Optional[Union[datetime.date, datetime.datetime, str]]
            The date of the data. Can be a datetime or an ISO datetime string. Data appears to go back to around 2022-06-01 Example: '2024-03-08T12:15:00+0400' (provider: intrinio)
        only_traded : bool
            Only include options that have been traded during the session, default is True. Setting to false will dramatically increase the size of the response - use with caution. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[OptionsSnapshots]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsSnapshots
        ----------------
        underlying_symbol : List[str]
            Ticker symbol of the underlying asset.
        contract_symbol : List[str]
            Symbol of the options contract.
        expiration : List[date]
            Expiration date of the options contract.
        dte : List[Optional[int]]
            Number of days to expiration of the options contract.
        strike : List[float]
            Strike price of the options contract.
        option_type : List[str]
            The type of option.
        volume : List[Optional[int]]
            The trading volume.
        open_interest : List[Optional[int]]
            Open interest at the time.
        last_price : List[Optional[float]]
            Last trade price at the time.
        last_size : List[Optional[int]]
            Lot size of the last trade.
        last_timestamp : List[Optional[datetime]]
            Timestamp of the last price.
        open : List[Optional[float]]
            The open price.
        high : List[Optional[float]]
            The high price.
        low : List[Optional[float]]
            The low price.
        close : List[Optional[float]]
            The close price.
        bid : List[Optional[float]]
            The last bid price at the time. (provider: intrinio)
        bid_size : List[Optional[int]]
            The size of the last bid price. (provider: intrinio)
        bid_timestamp : List[Optional[datetime]]
            The timestamp of the last bid price. (provider: intrinio)
        ask : List[Optional[float]]
            The last ask price at the time. (provider: intrinio)
        ask_size : List[Optional[int]]
            The size of the last ask price. (provider: intrinio)
        ask_timestamp : List[Optional[datetime]]
            The timestamp of the last ask price. (provider: intrinio)
        total_bid_volume : List[Optional[int]]
            Total volume of bids. (provider: intrinio)
        bid_high : List[Optional[float]]
            The highest bid price. (provider: intrinio)
        bid_low : List[Optional[float]]
            The lowest bid price. (provider: intrinio)
        total_ask_volume : List[Optional[int]]
            Total volume of asks. (provider: intrinio)
        ask_high : List[Optional[float]]
            The highest ask price. (provider: intrinio)
        ask_low : List[Optional[float]]
            The lowest ask price. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.derivatives.options.snapshots(provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/derivatives/options/snapshots",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "derivatives.options.snapshots",
                        ("intrinio",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def unusual(
        self,
        symbol: Annotated[
            Optional[str],
            OpenBBField(description="Symbol to get data for. (the underlying symbol)"),
        ] = None,
        provider: Annotated[
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for. (the underlying symbol)
        provider : Optional[Literal['intrinio']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format. If no symbol is supplied, requests are only allowed for a single date. Use the start_date for the target date. Intrinio appears to have data beginning Feb/2022, but is unclear when it actually began. (provider: intrinio)
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format. If a symbol is not supplied, do not include an end date. (provider: intrinio)
        trade_type : Optional[Literal['block', 'sweep', 'large']]
            The type of unusual activity to query for. (provider: intrinio)
        sentiment : Optional[Literal['bullish', 'bearish', 'neutral']]
            The sentiment type to query for. (provider: intrinio)
        min_value : Optional[Union[float, int]]
            The inclusive minimum total value for the unusual activity. (provider: intrinio)
        max_value : Optional[Union[float, int]]
            The inclusive maximum total value for the unusual activity. (provider: intrinio)
        limit : int
            The number of data entries to return. A typical day for all symbols will yield 50-80K records. The API will paginate at 1000 records. The high default limit (100K) is to be able to reliably capture the most days. The high absolute limit (1.25M) is to allow for outlier days. Queries at the absolute limit will take a long time, and might be unreliable. Apply filters to improve performance. (provider: intrinio)
        source : Literal['delayed', 'realtime']
            The source of the data. Either realtime or delayed. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[OptionsUnusual]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsUnusual
        --------------
        underlying_symbol : Optional[str]
            Symbol representing the entity requested in the data. (the underlying symbol)
        contract_symbol : str
            Contract symbol for the option.
        trade_timestamp : Optional[datetime]
            The datetime of order placement. (provider: intrinio)
        trade_type : Optional[Literal['block', 'sweep', 'large']]
            The type of unusual trade. (provider: intrinio)
        sentiment : Optional[Literal['bullish', 'bearish', 'neutral']]
            Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. (provider: intrinio)
        bid_at_execution : Optional[float]
            Bid price at execution. (provider: intrinio)
        ask_at_execution : Optional[float]
            Ask price at execution. (provider: intrinio)
        average_price : Optional[float]
            The average premium paid per option contract. (provider: intrinio)
        underlying_price_at_execution : Optional[float]
            Price of the underlying security at execution of trade. (provider: intrinio)
        total_size : Optional[int]
            The total number of contracts involved in a single transaction. (provider: intrinio)
        total_value : Optional[Union[int, float]]
            The aggregated value of all option contract premiums included in the trade. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.derivatives.options.unusual(symbol='TSLA', provider='intrinio')
        >>> # Use the 'symbol' parameter to get the most recent activity for a specific symbol.
        >>> obb.derivatives.options.unusual(symbol='TSLA', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/derivatives/options/unusual",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "derivatives.options.unusual",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
