### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from pydantic import BaseModel, validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_options(Container):
    @filter_call
    @validate_arguments
    def chains(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Get the complete options chain for a ticker.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['cboe'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[OptionsChains]
                Serializable results.
            provider : Union[Literal['cboe'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            error : Optional[Error]
                Caught exceptions.
            chart : Optional[Chart]
                Chart object.

        OptionsChains
        -------------
        expiration : Optional[datetime]
            The expiration date of the contract.
        strike : Optional[float]
            The strike price of the contract.
        optionType : Optional[str]
            Call or Put.
        bid : Optional[float]
            The bid price of the contract.
        ask : Optional[float]
            The ask price of the contract.
        openInterest : Optional[float]
            The open interest on the contract.
        volume : Optional[float]
            The current trading volume on the contract.
        contractSymbol : Optional[str]
            The contract symbol for the option. (provider: cboe)
        dte : Optional[int]
            The days to expiration for the option. (provider: cboe)
        bidSize : Optional[int]
            The bid size for the option. (provider: cboe)
        askSize : Optional[int]
            The ask size for the option. (provider: cboe)
        impliedVolatility : Optional[float]
            The implied volatility of the option. (provider: cboe)
        delta : Optional[float]
            The delta of the option. (provider: cboe)
        gamma : Optional[float]
            The gamma of the option. (provider: cboe)
        theta : Optional[float]
            The theta of the option. (provider: cboe)
        rho : Optional[float]
            The rho of the option. (provider: cboe)
        vega : Optional[float]
            The vega of the option. (provider: cboe)
        theoretical : Optional[float]
            The theoretical value of the option. (provider: cboe)
        open : Optional[float]
            The opening price of the option. (provider: cboe)
        high : Optional[float]
            The high price of the option. (provider: cboe)
        low : Optional[float]
            The low price of the option. (provider: cboe)
        lastTradePrice : Optional[float]
            The last trade price of the option. (provider: cboe)
        tick : Optional[str]
            Whether the last tick was up or down in price. (provider: cboe)
        previousClose : Optional[float]
            The previous closing price of the option. (provider: cboe)
        change : Optional[float]
            The change in  price of the option. (provider: cboe)
        changePercent : Optional[float]
            The change, in percent, of the option. (provider: cboe)
        lastTradeTimestamp : Optional[datetime]
            The last trade timestamp of the option. (provider: cboe)"""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/chains",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def eodchain(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Gets option chain at a specific date."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/eodchain",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Get historical data for a single option contract."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/hist",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def info(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Display option information (volatility, IV rank, etc.)."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/info",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pcr(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Display historical rolling put/call ratio for ticker over a defined window."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/pcr",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def unu(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show unusual options activity."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/unu",
            **inputs,
        ).output

        return filter_output(o)
