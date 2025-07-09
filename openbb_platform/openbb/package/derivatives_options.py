### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Any, Literal, Optional, Union

from numpy import ndarray
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from pandas import DataFrame, Series
from typing_extensions import Annotated


class ROUTER_derivatives_options(Container):
    """/derivatives/options
    chains
    snapshots
    surface
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
            Optional[Literal["intrinio", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio, yfinance.
        symbol : str
            Symbol to get data for.
        delay : Literal['eod', 'realtime', 'delayed']
            Whether to return delayed, realtime, or eod data. (provider: intrinio)
        date : Optional[date]
            The end-of-day date for options chains data. (provider: intrinio)
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
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsChains
        -------------
        underlying_symbol : list[Optional[str]]
            Underlying symbol for the option.
        underlying_price : list[Optional[float]]
            Price of the underlying stock.
        contract_symbol : list[str]
            Contract symbol for the option.
        eod_date : list[Optional[date]]
            Date for which the options chains are returned.
        expiration : list[date]
            Expiration date of the contract.
        dte : list[Optional[int]]
            Days to expiration of the contract.
        strike : list[float]
            Strike price of the contract.
        option_type : list[str]
            Call or Put.
        contract_size : list[Union[int, float]]
            Number of underlying units per contract.
        open_interest : list[Union[int, float]]
            Open interest on the contract.
        volume : list[Union[int, float]]
            The trading volume.
        theoretical_price : list[Optional[float]]
            Theoretical value of the option.
        last_trade_price : list[Optional[float]]
            Last trade price of the option.
        last_trade_size : list[Union[int, float]]
            Last trade size of the option.
        last_trade_time : list[Optional[datetime]]
            The timestamp of the last trade.
        tick : list[Optional[str]]
            Whether the last tick was up or down in price.
        bid : list[Optional[float]]
            Current bid price for the option.
        bid_size : list[Union[int, float]]
            Bid size for the option.
        bid_time : list[Optional[datetime]]
            The timestamp of the bid price.
        bid_exchange : list[Optional[str]]
            The exchange of the bid price.
        ask : list[Optional[float]]
            Current ask price for the option.
        ask_size : list[Union[int, float]]
            Ask size for the option.
        ask_time : list[Optional[datetime]]
            The timestamp of the ask price.
        ask_exchange : list[Optional[str]]
            The exchange of the ask price.
        mark : list[Optional[float]]
            The mid-price between the latest bid and ask.
        open : list[Optional[float]]
            The open price.
        open_bid : list[Optional[float]]
            The opening bid price for the option that day.
        open_ask : list[Optional[float]]
            The opening ask price for the option that day.
        high : list[Optional[float]]
            The high price.
        bid_high : list[Optional[float]]
            The highest bid price for the option that day.
        ask_high : list[Optional[float]]
            The highest ask price for the option that day.
        low : list[Optional[float]]
            The low price.
        bid_low : list[Optional[float]]
            The lowest bid price for the option that day.
        ask_low : list[Optional[float]]
            The lowest ask price for the option that day.
        close : list[Optional[float]]
            The close price.
        close_size : list[Union[int, float]]
            The closing trade size for the option that day.
        close_time : list[Optional[datetime]]
            The time of the closing price for the option that day.
        close_bid : list[Optional[float]]
            The closing bid price for the option that day.
        close_bid_size : list[Union[int, float]]
            The closing bid size for the option that day.
        close_bid_time : list[Optional[datetime]]
            The time of the bid closing price for the option that day.
        close_ask : list[Optional[float]]
            The closing ask price for the option that day.
        close_ask_size : list[Union[int, float]]
            The closing ask size for the option that day.
        close_ask_time : list[Optional[datetime]]
            The time of the ask closing price for the option that day.
        prev_close : list[Optional[float]]
            The previous close price.
        change : list[Optional[float]]
            The change in the price of the option.
        change_percent : list[Optional[float]]
            Change, in normalized percentage points, of the option.
        implied_volatility : list[Optional[float]]
            Implied volatility of the option.
        delta : list[Optional[float]]
            Delta of the option.
        gamma : list[Optional[float]]
            Gamma of the option.
        theta : list[Optional[float]]
            Theta of the option.
        vega : list[Optional[float]]
            Vega of the option.
        rho : list[Optional[float]]
            Rho of the option.
        in_the_money : list[Optional[bool]]
            Whether the option is in the money. (provider: yfinance)
        currency : list[Optional[str]]
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
                        ("intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={
                    "delay": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["eod", "realtime", "delayed"],
                        }
                    },
                    "option_type": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["call", "put"],
                        }
                    },
                    "moneyness": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["otm", "itm", "all"],
                        }
                    },
                    "model": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["black_scholes", "bjerk"],
                        }
                    },
                },
            ),
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
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio.
        date : Union[date, datetime, str, None]
            The date of the data. Can be a datetime or an ISO datetime string. Data appears to go back to around 2022-06-01 Example: '2024-03-08T12:15:00+0400' (provider: intrinio)
        only_traded : bool
            Only include options that have been traded during the session, default is True. Setting to false will dramatically increase the size of the response - use with caution. (provider: intrinio)

        Returns
        -------
        OBBject
            results : list[OptionsSnapshots]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsSnapshots
        ----------------
        underlying_symbol : list[str]
            Ticker symbol of the underlying asset.
        contract_symbol : list[str]
            Symbol of the options contract.
        expiration : list[date]
            Expiration date of the options contract.
        dte : list[Optional[int]]
            Number of days to expiration of the options contract.
        strike : list[float]
            Strike price of the options contract.
        option_type : list[str]
            The type of option.
        volume : list[Optional[int]]
            The trading volume.
        open_interest : list[Optional[int]]
            Open interest at the time.
        last_price : list[Optional[float]]
            Last trade price at the time.
        last_size : list[Optional[int]]
            Lot size of the last trade.
        last_timestamp : list[Optional[datetime]]
            Timestamp of the last price.
        open : list[Optional[float]]
            The open price.
        high : list[Optional[float]]
            The high price.
        low : list[Optional[float]]
            The low price.
        close : list[Optional[float]]
            The close price.
        bid : list[Optional[float]]
            The last bid price at the time. (provider: intrinio)
        bid_size : list[Optional[int]]
            The size of the last bid price. (provider: intrinio)
        bid_timestamp : list[Optional[datetime]]
            The timestamp of the last bid price. (provider: intrinio)
        ask : list[Optional[float]]
            The last ask price at the time. (provider: intrinio)
        ask_size : list[Optional[int]]
            The size of the last ask price. (provider: intrinio)
        ask_timestamp : list[Optional[datetime]]
            The timestamp of the last ask price. (provider: intrinio)
        total_bid_volume : list[Optional[int]]
            Total volume of bids. (provider: intrinio)
        bid_high : list[Optional[float]]
            The highest bid price. (provider: intrinio)
        bid_low : list[Optional[float]]
            The lowest bid price. (provider: intrinio)
        total_ask_volume : list[Optional[int]]
            Total volume of asks. (provider: intrinio)
        ask_high : list[Optional[float]]
            The highest ask price. (provider: intrinio)
        ask_low : list[Optional[float]]
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
            ),
        )

    @exception_handler
    @validate(config=dict(arbitrary_types_allowed=True))
    def surface(
        self,
        data: Annotated[
            Union[
                list,
                dict,
                DataFrame,
                list["DataFrame"],
                Series,
                list["Series"],
                ndarray,
                Data,
                list[Data],
                Data,
            ],
            OpenBBField(description=""),
        ],
        target: Annotated[str, OpenBBField(description="")] = "implied_volatility",
        underlying_price: Annotated[
            Optional[float], OpenBBField(description="")
        ] = None,
        option_type: Annotated[
            Optional[Literal["otm", "itm", "calls", "puts"]],
            OpenBBField(description=""),
        ] = "otm",
        dte_min: Annotated[Optional[int], OpenBBField(description="")] = None,
        dte_max: Annotated[Optional[int], OpenBBField(description="")] = None,
        moneyness: Annotated[Optional[float], OpenBBField(description="")] = None,
        strike_min: Annotated[Optional[float], OpenBBField(description="")] = None,
        strike_max: Annotated[Optional[float], OpenBBField(description="")] = None,
        oi: Annotated[bool, OpenBBField(description="")] = False,
        volume: Annotated[bool, OpenBBField(description="")] = False,
        theme: Annotated[
            Literal["dark", "light"], OpenBBField(description="")
        ] = "dark",
        chart_params: Annotated[Optional[dict], OpenBBField(description="")] = None,
        **kwargs: Any
    ) -> OBBject:
        """Filter and process the options chains data for volatility.

        Data posted can be an instance of OptionsChainsData,
        a pandas DataFrame, or a list of dictionaries.
        Data should contain the fields:

        - `expiration`: The expiration date of the option.
        - `strike`: The strike price of the option.
        - `option_type`: The type of the option (call or put).
        - `implied_volatility`: The implied volatility of the option. Or 'target' field.
        - `open_interest`: The open interest of the option.
        - `volume`: The trading volume of the option.
        - `dte` : Optional, days to expiration (DTE) of the option.
        - `underlying_price`: Optional, the price of the underlying asset.

        Results from the `/derivatives/options/chains` endpoint are the preferred input.

        If `underlying_price` is not supplied in the data as a field, it must be provided as a parameter.

        Parameters
        -----------
        data: Union[list[Data], Data]
        target: str
            The field to use as the z-axis. Default is "implied_volatility".
        underlying_price: Optional[float]
            The price of the underlying asset.
        option_type: Optional[str] = "otm"
            The type of df to display. Default is "otm".
            Choices are: ["otm", "itm", "puts", "calls"]
        dte_min: Optional[int] = None
            Minimum days to expiration (DTE) to filter options.
        dte_max: Optional[int] = None
            Maximum days to expiration (DTE) to filter options.
        moneyness: Optional[float] = None
            Specify a % moneyness to target for display,
            entered as a value between 0 and 100.
        strike_min: Optional[float] = None
            Minimum strike price to filter options.
        strike_max: Optional[float] = None
            Maximum strike price to filter options.
        oi: bool = False
            Filter for only options that have open interest. Default is False.
        volume: bool = False
            Filter for only options that have trading volume. Default is False.
        chart: bool = False
            Whether to return a chart or not. Default is False.
            Only valid if `openbb-charting` is installed.
        theme: Literal["dark", "light"] = "dark"
            The theme to use for the chart. Default is "dark".
            Only valid if `openbb-charting` is installed.
        chart_params: Optional[dict] = None
            Additional parameters to pass to the charting library.
            Only valid if `openbb-charting` is installed.
            Valid keys are:
            - `title`: The title of the chart.
            - `xtitle`: Title for the x-axis.
            - `ytitle`: Title for the y-axis.
            - `ztitle`: Title for the z-axis.
            - `colorscale`: The colorscale to use for the chart.
            - `layout_kwargs`: Additional dictionary to be passed to `fig.update_layout` before output.

        Returns
        -------
        OBBject[list]
            An OBBject containing the processed options data.
            Results are a list of dictionaries.
        """  # noqa: E501

        return self._run(
            "/derivatives/options/surface",
            **filter_inputs(
                data=data,
                target=target,
                underlying_price=underlying_price,
                option_type=option_type,
                dte_min=dte_min,
                dte_max=dte_max,
                moneyness=moneyness,
                strike_min=strike_min,
                strike_max=strike_max,
                oi=oi,
                volume=volume,
                theme=theme,
                chart_params=chart_params,
                data_processing=True,
                **kwargs,
            ),
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
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: intrinio.
        symbol : Optional[str]
            Symbol to get data for. (the underlying symbol)
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format. If no symbol is supplied, requests are only allowed for a single date. Use the start_date for the target date. Intrinio appears to have data beginning Feb/2022, but is unclear when it actually began. (provider: intrinio)
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format. If a symbol is not supplied, do not include an end date. (provider: intrinio)
        trade_type : Optional[Literal['block', 'sweep', 'large']]
            The type of unusual activity to query for. (provider: intrinio)
        sentiment : Optional[Literal['bullish', 'bearish', 'neutral']]
            The sentiment type to query for. (provider: intrinio)
        min_value : Union[int, float, None]
            The inclusive minimum total value for the unusual activity. (provider: intrinio)
        max_value : Union[int, float, None]
            The inclusive maximum total value for the unusual activity. (provider: intrinio)
        limit : int
            The number of data entries to return. A typical day for all symbols will yield 50-80K records. The API will paginate at 1000 records. The high default limit (100K) is to be able to reliably capture the most days. The high absolute limit (1.25M) is to allow for outlier days. Queries at the absolute limit will take a long time, and might be unreliable. Apply filters to improve performance. (provider: intrinio)
        source : Literal['delayed', 'realtime']
            The source of the data. Either realtime or delayed. (provider: intrinio)

        Returns
        -------
        OBBject
            results : list[OptionsUnusual]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
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
            ),
        )
