### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_fixedincome(Container):
    @filter_call
    @validate_arguments
    def treasury(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = "2023-07-24",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Get treasury rates.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        start_date : Optional[str]
            Start date of the data, default is None.
        end_date : Optional[str]
            End date of the data, default is today.


        Returns
        -------
        date : dateType
            The date of the treasury rates.
        month_1 : float
            The 1 month treasury rate.
        month_2 : float
            The 2 month treasury rate.
        month_3 : float
            The 3 month treasury rate.
        month_6 : float
            The 6 month treasury rate.
        year_1 : float
            The 1 year treasury rate.
        year_2 : float
            The 2 year treasury rate.
        year_3 : float
            The 3 year treasury rate.
        year_5 : float
            The 5 year treasury rate.
        year_7 : float
            The 7 year treasury rate.
        year_10 : float
            The 10 year treasury rate.
        year_20 : float
            The 20 year treasury rate.
        year_30 : float
            The 30 year treasury rate.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/treasury-rates-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/fixedincome/treasury",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ycrv(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Yield curve."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/fixedincome/ycrv",
            **inputs,
        ).output

        return filter_output(o)
