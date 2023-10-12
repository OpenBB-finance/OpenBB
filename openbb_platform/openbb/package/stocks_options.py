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
        provider: Union[Literal["intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        date : Optional[Union[str]]
            Date for which the options chains are returned. (provider: intrinio)

        Returns
        -------
        OBBject
            results : Union[List[OptionsChains]]
                Serializable results.
            provider : Union[Literal['intrinio'], None]
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
        symbol : str
            Underlying symbol for the option.
        expiration : date
            Expiration date of the contract.
        strike : float
            Strike price of the contract.
        type : str
            Call or Put.
        date : date
            Date for which the options chains are returned.
        close : Optional[Union[float]]
            Close price for the option that day.
        close_bid : Optional[Union[float]]
            The closing bid price for the option that day.
        close_ask : Optional[Union[float]]
            The closing ask price for the option that day.
        volume : Optional[Union[float]]
            Current trading volume on the contract.
        open : Optional[Union[float]]
            Opening price of the option.
        open_bid : Optional[Union[float]]
            The opening bid price for the option that day.
        open_ask : Optional[Union[float]]
            The opening ask price for the option that day.
        open_interest : Optional[Union[float]]
            Open interest on the contract.
        high : Optional[Union[float]]
            High price of the option.
        low : Optional[Union[float]]
            Low price of the option.
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
            Vega of the option."""  # noqa: E501

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
