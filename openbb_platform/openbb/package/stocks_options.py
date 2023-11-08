### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_stocks_options(Container):
    """/stocks/options
    chains
    unusual
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def chains(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["cboe", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['cboe', 'intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        date : Optional[Union[datetime.date]]
            Date for which the options chains are returned. (provider: intrinio)

        Returns
        -------
        OBBject
            results : Union[List[OptionsChains]]
                Serializable results.
            provider : Union[Literal['cboe', 'intrinio'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        OptionsChains
        -------------
        contract_symbol : str
            Contract symbol for the option.
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data. Here its the underlying symbol for the option.
        expiration : date
            Expiration date of the contract.
        strike : float
            Strike price of the contract.
        option_type : str
            Call or Put.
        eod_date : Optional[Union[date]]
            Date for which the options chains are returned.
        close : Optional[Union[float]]
            The close price of the symbol.
        close_bid : Optional[Union[float]]
            The closing bid price for the option that day.
        close_ask : Optional[Union[float]]
            The closing ask price for the option that day.
        volume : Optional[Union[float]]
            The volume of the symbol.
        open : Optional[Union[float]]
            The open price of the symbol.
        open_bid : Optional[Union[float]]
            The opening bid price for the option that day.
        open_ask : Optional[Union[float]]
            The opening ask price for the option that day.
        open_interest : Optional[Union[float]]
            Open interest on the contract.
        high : Optional[Union[float]]
            The high price of the symbol.
        low : Optional[Union[float]]
            The low price of the symbol.
        mark : Optional[Union[float]]
            The mid-price between the latest bid-ask spread.
        ask_high : Optional[Union[float]]
            The highest ask price for the option that day.
        ask_low : Optional[Union[float]]
            The lowest ask price for the option that day.
        bid_high : Optional[Union[float]]
            The highest bid price for the option that day.
        bid_low : Optional[Union[float]]
            The lowest bid price for the option that day.
        implied_volatility : Optional[Union[float]]
            Implied volatility of the option.
        delta : Optional[Union[float]]
            Delta of the option.
        gamma : Optional[Union[float]]
            Gamma of the option.
        theta : Optional[Union[float]]
            Theta of the option.
        vega : Optional[Union[float]]
            Vega of the option.
        bid_size : Optional[Union[int]]
            Bid size for the option. (provider: cboe)
        ask_size : Optional[Union[int]]
            Ask size for the option. (provider: cboe)
        theoretical : Optional[Union[float]]
            Theoretical value of the option. (provider: cboe)
        last_trade_price : Optional[Union[float]]
            Last trade price of the option. (provider: cboe)
        tick : Optional[Union[str]]
            Whether the last tick was up or down in price. (provider: cboe)
        prev_close : Optional[Union[float]]
            Previous closing price of the option. (provider: cboe)
        change : Optional[Union[float]]
            Change in  price of the option. (provider: cboe)
        change_percent : Optional[Union[float]]
            Change, in percent, of the option. (provider: cboe)
        rho : Optional[Union[float]]
            Rho of the option. (provider: cboe)
        last_trade_timestamp : Optional[Union[datetime]]
            Last trade timestamp of the option. (provider: cboe)
        dte : Optional[Union[int]]
            Days to expiration for the option. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.options.chains(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/options/chains",
            **inputs,
        )

    @validate
    def unusual(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. (the underlying symbol)"
            ),
        ] = None,
        provider: Union[Literal["intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Union[str, None]
            Symbol to get data for. (the underlying symbol)
        provider : Union[Literal['intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        source : Literal['delayed', 'realtime']
            The source of the data. Either realtime or delayed. (provider: intrinio)

        Returns
        -------
        OBBject
            results : Union[List[OptionsUnusual]]
                Serializable results.
            provider : Union[Literal['intrinio'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        OptionsUnusual
        --------------
        underlying_symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data. (the underlying symbol)
        contract_symbol : str
            Contract symbol for the option.
        trade_type : Optional[Union[str]]
            The type of unusual trade. (provider: intrinio)
        sentiment : Optional[Union[str]]
            Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. (provider: intrinio)
        total_value : Optional[Union[int, float]]
            The aggregated value of all option contract premiums included in the trade. (provider: intrinio)
        total_size : Optional[Union[int]]
            The total number of contracts involved in a single transaction. (provider: intrinio)
        average_price : Optional[Union[float]]
            The average premium paid per option contract. (provider: intrinio)
        ask_at_execution : Optional[Union[float]]
            Ask price at execution. (provider: intrinio)
        bid_at_execution : Optional[Union[float]]
            Bid price at execution. (provider: intrinio)
        underlying_price_at_execution : Optional[Union[float]]
            Price of the underlying security at execution of trade. (provider: intrinio)
        timestamp : Optional[Union[datetime]]
            The UTC timestamp of order placement. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.options.unusual()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/options/unusual",
            **inputs,
        )
