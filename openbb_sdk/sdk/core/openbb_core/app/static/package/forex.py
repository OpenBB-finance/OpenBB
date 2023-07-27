### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import Literal, Optional, Union

from pydantic import validate_arguments

from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_forex(Container):
    @filter_call
    @validate_arguments
    def pairs(
        self,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Forex Available Pairs."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/forex/pairs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def load(
        self,
        symbol: str,
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Forex Intraday Price."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/forex/load",
            **inputs,
        ).output

        return filter_output(o)
