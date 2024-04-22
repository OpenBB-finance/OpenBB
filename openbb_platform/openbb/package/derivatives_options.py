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
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'intrinio' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        date : Optional[datetime.date]
            The end-of-day date for options chains data. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[OptionsChains]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        OptionsChains
        -------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data. Here, it is the underlying symbol for the option.
        contract_symbol : str
            Contract symbol for the option.
        eod_date : Optional[date]
            Date for which the options chains are returned.
        expiration : date
            Expiration date of the contract.
        strike : float
            Strike price of the contract.
        option_type : str
            Call or Put.
        open_interest : Optional[int]
            Open interest on the contract.
        volume : Optional[int]
            The trading volume.
        theoretical_price : Optional[float]
            Theoretical value of the option.
        last_trade_price : Optional[float]
            Last trade price of the option.
        tick : Optional[str]
            Whether the last tick was up or down in price.
        bid : Optional[float]
            Current bid price for the option.
        bid_size : Optional[int]
            Bid size for the option.
        ask : Optional[float]
            Current ask price for the option.
        ask_size : Optional[int]
            Ask size for the option.
        mark : Optional[float]
            The mid-price between the latest bid and ask.
        open : Optional[float]
            The open price.
        open_bid : Optional[float]
            The opening bid price for the option that day.
        open_ask : Optional[float]
            The opening ask price for the option that day.
        high : Optional[float]
            The high price.
        bid_high : Optional[float]
            The highest bid price for the option that day.
        ask_high : Optional[float]
            The highest ask price for the option that day.
        low : Optional[float]
            The low price.
        bid_low : Optional[float]
            The lowest bid price for the option that day.
        ask_low : Optional[float]
            The lowest ask price for the option that day.
        close : Optional[float]
            The close price.
        close_size : Optional[int]
            The closing trade size for the option that day.
        close_time : Optional[datetime]
            The time of the closing price for the option that day.
        close_bid : Optional[float]
            The closing bid price for the option that day.
        close_bid_size : Optional[int]
            The closing bid size for the option that day.
        close_bid_time : Optional[datetime]
            The time of the bid closing price for the option that day.
        close_ask : Optional[float]
            The closing ask price for the option that day.
        close_ask_size : Optional[int]
            The closing ask size for the option that day.
        close_ask_time : Optional[datetime]
            The time of the ask closing price for the option that day.
        prev_close : Optional[float]
            The previous close price.
        change : Optional[float]
            The change in the price of the option.
        change_percent : Optional[float]
            Change, in normalizezd percentage points, of the option.
        implied_volatility : Optional[float]
            Implied volatility of the option.
        delta : Optional[float]
            Delta of the option.
        gamma : Optional[float]
            Gamma of the option.
        theta : Optional[float]
            Theta of the option.
        vega : Optional[float]
            Vega of the option.
        rho : Optional[float]
            Rho of the option.
        exercise_style : Optional[str]
            The exercise style of the option, American or European. (provider: intrinio)

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
                        "/derivatives/options/chains",
                        ("intrinio",),
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
    def unusual(
        self,
        symbol: Annotated[
            Optional[str],
            OpenBBField(description="Symbol to get data for. (the underlying symbol)"),
        ] = None,
        provider: Annotated[
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'intrinio' if there is\n    no default."
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
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
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
        >>> obb.derivatives.options.unusual(provider='intrinio')
        >>> # Use the 'symbol' parameter to get the most recent activity for a specific symbol.
        >>> obb.derivatives.options.unusual(symbol='TSLA', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/derivatives/options/unusual",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/derivatives/options/unusual",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
