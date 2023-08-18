### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_dps(Container):
    @filter_call
    @validate_arguments
    def ctb(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Cost to borrow of stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/ctb",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dpotc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Dark pools (ATS) vs OTC data."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/dpotc",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ftd(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Fails-to-deliver data."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/ftd",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hsi(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show top high short interest stocks of over 20% ratio."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/hsi",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pos(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Dark pool short position."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/pos",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def prom(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Promising tickers based on dark pool shares regression."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/prom",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def psi(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Price vs short interest volume"""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/psi",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def psi_q(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/psi_q",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def psi_sg(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/psi_sg",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def shorted(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Most shorted stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/shorted",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sidtc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Short interest and days to cover."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/sidtc",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def spos(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Net short vs position."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/dps/spos",
            **inputs,
        )

        return filter_output(o)
