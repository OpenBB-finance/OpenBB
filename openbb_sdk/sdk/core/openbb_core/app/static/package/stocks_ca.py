### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from pydantic import BaseModel, validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_ca(Container):
    @filter_call
    @validate_arguments
    def balance(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company balance sheet."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/balance",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cashflow(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company cashflow."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/cashflow",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hcorr(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company historical correlation."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/hcorr",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def hist(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company historical prices."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/hist",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def income(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company income statement."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/income",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def peers(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Company peers.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['fmp'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[StockPeers]
                Serializable results.
            provider : Union[Literal['fmp'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            error : Optional[Error]
                Caught exceptions.
            chart : Optional[Chart]
                Chart object.

        StockPeers
        ----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        peers_list : Optional[List[str]]
            A list of stock peers based on sector, exchange and market cap."""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/peers",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def scorr(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company sector correlation."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/scorr",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def screener(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company screener."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/screener",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sentiment(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company sentiment."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/sentiment",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def similar(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company similar."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/similar",
            **inputs,
        )

        return filter_output(o)

    @filter_call
    @validate_arguments
    def volume(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Company volume."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/ca/volume",
            **inputs,
        )

        return filter_output(o)
