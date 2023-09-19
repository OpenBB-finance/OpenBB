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
        provider : Union[Literal['cboe', 'intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        date : Union[datetime.date, str, None]
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
        bid_size : Optional[int]
            Bid size for the option. (provider: cboe)
        ask_size : Optional[int]
            Ask size for the option. (provider: cboe)
        theoretical : Optional[float]
            Theoretical value of the option. (provider: cboe)
        open : Optional[float]
            Opening price of the option. (provider: cboe, intrinio)
        high : Optional[float]
            High price of the option. (provider: cboe, intrinio)
        low : Optional[float]
            Low price of the option. (provider: cboe, intrinio)
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
        implied_volatility : Optional[float]
            Implied volatility of the option. (provider: cboe, intrinio)
        delta : Optional[float]
            Delta of the option. (provider: cboe, intrinio)
        gamma : Optional[float]
            Gamma of the option. (provider: cboe, intrinio)
        vega : Optional[float]
            Vega of the option. (provider: cboe, intrinio)
        theta : Optional[float]
            Theta of the option. (provider: cboe, intrinio)
        rho : Optional[float]
            Rho of the option. (provider: cboe)
        last_trade_timestamp : Optional[datetime]
            Last trade timestamp of the option. (provider: cboe)
        dte : Optional[int]
            Days to expiration for the option. (provider: cboe, intrinio)
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
        close : Optional[float]
            Close price for the option that day. (provider: intrinio)
        eod_date : Optional[date]
            Historical date for which the options chains data is from. (provider: intrinio)
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

        return self._command_runner.run(
            "/stocks/options/chains",
            **inputs,
        )
