### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_stocks_ins(Container):
    """/stocks/ins
    act
    blcp
    blcs
    blip
    blis
    blop
    blos
    filt
    lcb
    lins
    lip
    lis
    lit
    lpsb
    print_insider_data
    stats
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def act(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Insider activity over time."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/act",
            **inputs,
        )

    @validate_arguments
    def blcp(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest CEO/CFO purchaces ($25k+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blcp",
            **inputs,
        )

    @validate_arguments
    def blcs(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest CEO/CFO sales ($100k+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blcs",
            **inputs,
        )

    @validate_arguments
    def blip(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest insider purchaces ($25+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blip",
            **inputs,
        )

    @validate_arguments
    def blis(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest insider sales ($100k+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blis",
            **inputs,
        )

    @validate_arguments
    def blop(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest officer purchaces ($25k+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blop",
            **inputs,
        )

    @validate_arguments
    def blos(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Big latest officer sales ($100k+)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/blos",
            **inputs,
        )

    @validate_arguments
    def filt(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Filter insiders based on preset."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/filt",
            **inputs,
        )

    @validate_arguments
    def lcb(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest cluster buys."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lcb",
            **inputs,
        )

    @validate_arguments
    def lins(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Last insider trading of the company."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lins",
            **inputs,
        )

    @validate_arguments
    def lip(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider purchaces."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lip",
            **inputs,
        )

    @validate_arguments
    def lis(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider sales."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lis",
            **inputs,
        )

    @validate_arguments
    def lit(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest insider trading (all filings)."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lit",
            **inputs,
        )

    @validate_arguments
    def lpsb(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Latest penny stock buys."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/lpsb",
            **inputs,
        )

    @validate_arguments
    def print_insider_data(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Print insider data."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/print_insider_data",
            **inputs,
        )

    @validate_arguments
    def stats(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Insider stats of the company."""  # noqa: E501

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/stocks/ins/stats",
            **inputs,
        )
