### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_stocks_options(Container):
    """/stocks/options
    chains
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
        date : Optional[str]
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
        close : Optional[float]
            Close price for the option that day.
        close_bid : Optional[float]
            The closing bid price for the option that day.
        close_ask : Optional[float]
            The closing ask price for the option that day.
        volume : Optional[float]
            Current trading volume on the contract.
        open : Optional[float]
            Opening price of the option.
        open_bid : Optional[float]
            The opening bid price for the option that day.
        open_ask : Optional[float]
            The opening ask price for the option that day.
        open_interest : Optional[float]
            Open interest on the contract.
        high : Optional[float]
            High price of the option.
        low : Optional[float]
            Low price of the option.
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
