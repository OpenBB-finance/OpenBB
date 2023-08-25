### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_stocks_options(Container):
    """/stocks/options
    eodchain
    hist
    info
    pcr
    unu
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def eodchain(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Gets option chain at a specific date."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/options/eodchain",
            **inputs,
        )

    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Get historical data for a single option contract."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/options/hist",
            **inputs,
        )

    @validate_arguments
    def info(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Display option information (volatility, IV rank, etc.)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/options/info",
            **inputs,
        )

    @validate_arguments
    def pcr(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Display historical rolling put/call ratio for ticker over a defined window."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/options/pcr",
            **inputs,
        )

    @validate_arguments
    def unu(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show unusual options activity."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/options/unu",
            **inputs,
        )
