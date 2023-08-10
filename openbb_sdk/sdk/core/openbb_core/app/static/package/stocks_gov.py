### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_gov(Container):
    @filter_call
    @validate_arguments
    def contracts(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return government contracts."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/contracts",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def government_trading(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return government trading."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/government_trading",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gtrades(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return government trades."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/gtrades",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def histcont(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Historical quarterly government contracts."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/histcont",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lastcontracts(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Return last government contracts given out."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/lastcontracts",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lasttrades(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Last trades."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/lasttrades",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lobbying(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Corporate lobbying details."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/lobbying",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def qtrcontracts(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Quarterly government contracts analysis."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/qtrcontracts",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def topbuys(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Show most purchased stocks."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/topbuys",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def toplobbying(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Top corporate lobbying tickers."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/toplobbying",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def topsells(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Show most sold stocks."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/gov/topsells",
            **inputs,
        ).output

        return filter_output(o)
