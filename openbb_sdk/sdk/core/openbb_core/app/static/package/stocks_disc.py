### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###


from pydantic import validate_arguments

import openbb_core.app.model.results.empty
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_disc(Container):
    @filter_call
    @validate_arguments
    def active(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Most active stocks by intraday trade volumes."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/active",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def arkord(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Order by ARK INvestment Management LLC."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/arkord",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def asc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Small cap stocks with revenue and earnings growth more than 25%."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/asc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dividends(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/dividends",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def filings(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """The most-recent form submissions to the SEC."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/filings",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Future IPOs dates."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/fipo",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gainers(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show latest top gainers."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/gainers",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gtech(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Tech stocks with revenue and earnings growth more than 25%."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/gtech",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hotpenny(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Today's hot penny stocks."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/hotpenny",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/ipo",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def losers(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show latest top losers."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/losers",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lowfloat(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Low float stocks under 10M shares float."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/lowfloat",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Past IPOs dates."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/pipo",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rtat(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Top 10 retail traded stocks per day."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/rtat",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def trending(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Trending news."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/trending",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ugs(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Undervalued stocks with revenue and earnings growth above 25%."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/ugs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ulc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Potentially undervalued large cap stocks."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/ulc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def upcoming(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Upcoming earnings release dates."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/disc/upcoming",
            **inputs,
        ).output

        return filter_output(o)
