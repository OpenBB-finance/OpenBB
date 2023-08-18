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
        """Most active stocks by intraday trade volumes."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/active",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def arkord(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Order by ARK INvestment Management LLC."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/arkord",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def asc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Small cap stocks with revenue and earnings growth more than 25%."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/asc",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dividends(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/dividends",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def filings(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """The most-recent form submissions to the SEC."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/filings",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Future IPOs dates."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/fipo",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gainers(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show latest top gainers."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/gainers",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gtech(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Tech stocks with revenue and earnings growth more than 25%."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/gtech",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hotpenny(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Today's hot penny stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/hotpenny",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/ipo",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def losers(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Show latest top losers."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/losers",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def lowfloat(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Low float stocks under 10M shares float."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/lowfloat",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pipo(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Past IPOs dates."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/pipo",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rtat(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Top 10 retail traded stocks per day."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/rtat",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def trending(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Trending news."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/trending",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ugs(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Undervalued stocks with revenue and earnings growth above 25%."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/ugs",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ulc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Potentially undervalued large cap stocks."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/ulc",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def upcoming(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Upcoming earnings release dates."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner.run(
            "/stocks/disc/upcoming",
            **inputs,
        )

        return filter_output(o)
