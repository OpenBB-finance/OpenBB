### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_options(Container):
    @filter_call
    @validate_arguments
    def chains(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Get the complete options chain for a ticker.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[cboe]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        OptionsChains
        -------------
        expiration : datetime
            The expiration date of the contract.
        strike : float
            The strike price of the contract.
        optionType : str
            Call or Put.
        bid : float
            The bid price of the contract.
        ask : float
            The ask price of the contract.
        openInterest : float
            The open interest on the contract.
        volume : float
            The current trading volume on the contract.

        cboe
        ====

        Parameters
        ----------
        All fields are standardized.


        OptionsChains
        -------------
        contractSymbol : str
            The contract symbol for the option.
        dte : int
            The days to expiration for the option.
        bidSize : int
            The bid size for the option.
        askSize : int
            The ask size for the option.
        impliedVolatility : float
            The implied volatility of the option.
        delta : float
            The delta of the option.
        gamma : float
            The gamma of the option.
        theta : float
            The theta of the option.
        rho : float
            The rho of the option.
        vega : float
            The vega of the option.
        theoretical : float
            The theoretical value of the option.
        open : float
            The opening price of the option.
        high : float
            The high price of the option.
        low : float
            The low price of the option.
        lastTradePrice : float
            The last trade price of the option.
        tick : str
            Whether the last tick was up or down in price.
        previousClose : float
            The previous closing price of the option.
        change : float
            The change in  price of the option.
        changePercent : float
            The change, in percent, of the option.
        lastTradeTimestamp : datetime
            The last trade timestamp of the option."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Gets option chain at a specific date."""  # noqa: E501
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
    def expirations(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return options expirations."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/expirations",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def grhist(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Plot option greek history."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/grhist",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Display option information (volatility, IV rank, etc.)."""  # noqa: E501
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
    def last_price(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return last price of an option."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/last_price",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def oi(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Plot option open interest."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/oi",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pcr(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Show unusual options activity."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/unu",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def voi(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Plot volume and open interest."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/voi",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def vol(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Plot volume."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/vol",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def vsurf(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Show 3D volatility surface."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/vsurf",
            **inputs,
        ).output

        return filter_output(o)
