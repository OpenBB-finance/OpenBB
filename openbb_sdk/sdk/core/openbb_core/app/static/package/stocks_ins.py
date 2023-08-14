### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_ins(Container):
    @filter_call
    @validate_arguments
    def act(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Insider activity over time."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/act",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blcp(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest CEO/CFO purchaces ($25k+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blcp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blcs(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest CEO/CFO sales ($100k+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blcs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blip(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest insider purchaces ($25+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blip",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blis(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest insider sales ($100k+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blis",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blop(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest officer purchaces ($25k+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blop",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def blos(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest officer sales ($100k+)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/blos",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def filt(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Filter insiders based on preset."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/filt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lcb(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest cluster buys."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lcb",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lins(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Last insider trading of the company."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lins",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lip(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider purchaces."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lip",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lis(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider sales."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lis",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lit(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider trading (all filings)."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lit",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lpsb(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest penny stock buys."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/lpsb",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def print_insider_data(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Print insider data."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/print_insider_data",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def stats(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Insider stats of the company."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ins/stats",
            **inputs,
        ).output

        return filter_output(o)
