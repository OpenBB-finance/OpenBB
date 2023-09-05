### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_stocks_options(Container):
    """/stocks/options
    chains
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def chains(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        provider : Union[Literal['intrinio'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        date : Union[datetime.date, str, NoneType]
            Date for which the options chains are returned. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[OptionsChains]
                Serializable results.
            provider : Union[Literal['intrinio'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        OptionsChains
        -------------
        expiration : Optional[datetime]
            Expiration date of the contract.
        strike : Optional[float]
            Strike price of the contract.
        option_type : Optional[str]
            Call or Put.
        contract_symbol : Optional[str]
            Contract symbol for the option.
        bid : Optional[float]
            Bid price of the contract.
        ask : Optional[float]
            Ask price of the contract.
        open_interest : Optional[float]
            Open interest on the contract.
        volume : Optional[float]
            Current trading volume on the contract.
        mark : Optional[float]
            The mid-price between the latest bid-ask spread. (provider: intrinio)
        open_bid : Optional[float]
            The lowest bid price for the option that day. (provider: intrinio)
        open_ask : Optional[float]
            The lowest ask price for the option that day. (provider: intrinio)
        bid_low : Optional[float]
            The lowest bid price for the option that day. (provider: intrinio)
        ask_low : Optional[float]
            The lowest ask price for the option that day. (provider: intrinio)
        bid_high : Optional[float]
            The highest bid price for the option that day. (provider: intrinio)
        ask_high : Optional[float]
            The highest ask price for the option that day. (provider: intrinio)
        open : Optional[float]
            The open price for the option that day. (provider: intrinio)
        high : Optional[float]
            The high price for the option that day. (provider: intrinio)
        low : Optional[float]
            The low price for the option that day. (provider: intrinio)
        close : Optional[float]
            The close price for the option that day. (provider: intrinio)
        implied_volatility : Optional[float]
            The implied volatility for the option at the end of day. (provider: intrinio)
        delta : Optional[float]
            The delta value at the end of day. (provider: intrinio)
        gamma : Optional[float]
            The gamma value at the end of day. (provider: intrinio)
        vega : Optional[float]
            The vega value at the end of day. (provider: intrinio)
        theta : Optional[float]
            The theta value at the end of day. (provider: intrinio)
        eod_date : Optional[date]
            Historical date for which the options chains data is from. (provider: intrinio)
        dte : Optional[int]
            The number of days until expiry. (provider: intrinio)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/stocks/options/chains",
            **inputs,
        )
