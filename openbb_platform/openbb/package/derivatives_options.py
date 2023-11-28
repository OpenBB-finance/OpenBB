### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_derivatives_options(Container):
    """/derivatives/options
    chains
    unusual
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def chains(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
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
            Date for which the options chains are returned. (provider: intrinio)

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
            extra: Dict[str, Any]
                Extra info.

        OptionsChains
        -------------
        contract_symbol : str
            Contract symbol for the option.
        symbol : Optional[str]
            Symbol representing the entity requested in the data. Here its the underlying symbol for the option.
        expiration : date
            Expiration date of the contract.
        strike : float
            Strike price of the contract.
        option_type : str
            Call or Put.
        eod_date : Optional[date]
            Date for which the options chains are returned.
        close : Optional[float]
            The close price.
        close_bid : Optional[float]
            The closing bid price for the option that day.
        close_ask : Optional[float]
            The closing ask price for the option that day.
        volume : Optional[float]
            The trading volume.
        open : Optional[float]
            The open price.
        open_bid : Optional[float]
            The opening bid price for the option that day.
        open_ask : Optional[float]
            The opening ask price for the option that day.
        open_interest : Optional[float]
            Open interest on the contract.
        high : Optional[float]
            The high price.
        low : Optional[float]
            The low price.
        mark : Optional[float]
            The mid-price between the latest bid-ask spread.
        ask_high : Optional[float]
            The highest ask price for the option that day.
        ask_low : Optional[float]
            The lowest ask price for the option that day.
        bid_high : Optional[float]
            The highest bid price for the option that day.
        bid_low : Optional[float]
            The lowest bid price for the option that day.
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.derivatives.options.chains(symbol="AAPL")
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
            "/derivatives/options/chains",
            **inputs,
        )

    @validate
    def unusual(
        self,
        symbol: Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. (the underlying symbol)"
            ),
        ] = None,
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for. (the underlying symbol)
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
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
            extra: Dict[str, Any]
                Extra info.

        OptionsUnusual
        --------------
        underlying_symbol : Optional[str]
            Symbol representing the entity requested in the data. (the underlying symbol)
        contract_symbol : str
            Contract symbol for the option.
        trade_type : Optional[str]
            The type of unusual trade. (provider: intrinio)
        sentiment : Optional[str]
            Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. (provider: intrinio)
        total_value : Optional[Union[int, float]]
            The aggregated value of all option contract premiums included in the trade. (provider: intrinio)
        total_size : Optional[int]
            The total number of contracts involved in a single transaction. (provider: intrinio)
        average_price : Optional[float]
            The average premium paid per option contract. (provider: intrinio)
        ask_at_execution : Optional[float]
            Ask price at execution. (provider: intrinio)
        bid_at_execution : Optional[float]
            Bid price at execution. (provider: intrinio)
        underlying_price_at_execution : Optional[float]
            Price of the underlying security at execution of trade. (provider: intrinio)
        timestamp : Optional[datetime]
            The UTC timestamp of order placement. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.derivatives.options.unusual()
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
            "/derivatives/options/unusual",
            **inputs,
        )
