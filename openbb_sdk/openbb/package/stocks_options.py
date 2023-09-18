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
        provider: Union[Literal["cboe", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        provider : Union[Literal['cboe', 'intrinio'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        date : Union[datetime.date, NoneType]
            Date for which the options chains are returned. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[OptionsChains]
                Serializable results.
            provider : Union[Literal['cboe', 'intrinio'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        OptionsChains
        -------------
        contract_symbol : Optional[str]
            Contract symbol for the option.
        symbol : Optional[str]
            Underlying symbol for the option.
        expiration : Optional[date]
            Expiration date of the contract.
        strike : Optional[float]
            Strike price of the contract.
        type : Optional[str]
            Call or Put.
        date : Optional[date]
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
            Vega of the option.
        bid_size : Optional[int]
            Bid size for the option. (provider: cboe)
        ask_size : Optional[int]
            Ask size for the option. (provider: cboe)
        theoretical : Optional[float]
            Theoretical value of the option. (provider: cboe)
        last_trade_price : Optional[float]
            Last trade price of the option. (provider: cboe)
        tick : Optional[str]
            Whether the last tick was up or down in price. (provider: cboe)
        prev_close : Optional[float]
            Previous closing price of the option. (provider: cboe)
        change : Optional[float]
            Change in  price of the option. (provider: cboe)
        change_percent : Optional[float]
            Change, in percent, of the option. (provider: cboe)
        rho : Optional[float]
            Rho of the option. (provider: cboe)
        last_trade_timestamp : Optional[datetime]
            Last trade timestamp of the option. (provider: cboe)
        dte : Optional[int]
            Days to expiration for the option. (provider: cboe)"""  # noqa: E501

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
