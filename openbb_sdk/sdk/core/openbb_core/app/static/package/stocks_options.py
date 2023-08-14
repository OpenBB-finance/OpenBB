### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_options(Container):
    @filter_call
    @validate_arguments
    def chains(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return options chains with greeks."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/chains",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dte(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/dte",
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
    def expirations(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return options expirations."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Plot option greek history."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Plot option history."""
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
    def last_price(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return last price of an option."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Plot option open interest."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Display put/call ratio for ticker."""
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
    def price(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/price",
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

    @filter_call
    @validate_arguments
    def voi(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Plot volume and open interest."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Plot volume."""
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
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show 3D volatility surface."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/options/vsurf",
            **inputs,
        ).output

        return filter_output(o)
