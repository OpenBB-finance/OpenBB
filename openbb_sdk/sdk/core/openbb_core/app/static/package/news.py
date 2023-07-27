### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

import pydantic
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_news(Container):
    @filter_call
    @validate_arguments
    def globalnews(
        self,
        page: pydantic.types.NonNegativeInt = 0,
        chart: bool = False,
        provider: Optional[Literal["benzinga"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Global News."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "page": page,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/news/globalnews",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sectornews(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Sector news."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/news/sectornews",
            **inputs,
        ).output

        return filter_output(o)
