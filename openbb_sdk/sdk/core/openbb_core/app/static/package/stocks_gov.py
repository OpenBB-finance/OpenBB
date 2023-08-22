### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs


class CLASS_stocks_gov(Container):
    """/stocks/gov
    contracts
    government_trading
    gtrades
    histcont
    lastcontracts
    lasttrades
    lobbying
    qtrcontracts
    topbuys
    toplobbying
    topsells
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def contracts(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return government contracts."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/contracts",
            **inputs,
        )

    @validate_arguments
    def government_trading(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return government trading."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/government_trading",
            **inputs,
        )

    @validate_arguments
    def gtrades(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return government trades."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/gtrades",
            **inputs,
        )

    @validate_arguments
    def histcont(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Historical quarterly government contracts."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/histcont",
            **inputs,
        )

    @validate_arguments
    def lastcontracts(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Return last government contracts given out."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/lastcontracts",
            **inputs,
        )

    @validate_arguments
    def lasttrades(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Last trades."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/lasttrades",
            **inputs,
        )

    @validate_arguments
    def lobbying(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Corporate lobbying details."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/lobbying",
            **inputs,
        )

    @validate_arguments
    def qtrcontracts(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Quarterly government contracts analysis."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/qtrcontracts",
            **inputs,
        )

    @validate_arguments
    def topbuys(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show most purchased stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/topbuys",
            **inputs,
        )

    @validate_arguments
    def toplobbying(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Top corporate lobbying tickers."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/toplobbying",
            **inputs,
        )

    @validate_arguments
    def topsells(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show most sold stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/gov/topsells",
            **inputs,
        )
