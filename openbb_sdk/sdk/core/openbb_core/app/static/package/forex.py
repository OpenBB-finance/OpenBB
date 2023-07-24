### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

from pydantic import validate_arguments

from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_forex(Container):
    @filter_call
    @validate_arguments
    def pairs(
        self, chart: bool = False, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> CommandOutput[typing.List]:
        """Forex Available Pairs.

        Available providers: fmp,

        Standard
        ========


        Returns
        -------
        symbol : str
            The symbol of the currency pair.
        name : str
            The name of the currency pair separated by '/'.
        currency : str
            The base currency of the currency pair.
        stock_exchange : Optional[str]
            The stock exchange of the currency pair.
        exchange_short_name : Optional[str]
            The short name of the stock exchange of the currency pair.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price

        """
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
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Forex Intraday Price.

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the forex currency pair.


        Returns
        -------
        date : datetime
            The date of the forex currency pair.
        open : PositiveFloat
            The open price of the forex currency pair.
        high : PositiveFloat
            The high price of the forex currency pair.
        low : PositiveFloat
            The low price of the forex currency pair.
        close : PositiveFloat
            The close price of the forex currency pair.
        adj_close : Optional[PositiveFloat]
            The adjusted close price of the forex currency pair.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/forex/get_v2_aggs_ticker__forexticker__range__multiplier___timespan___from___to

        Parameters
        ----------
        stocksTicker : str
            The ticker symbol of the stocks to fetch.
        start_date : Union[date, datetime], optional
            The start date of the query.
        end_date : Union[date, datetime], optional
            The end date of the query.
        timespan : Timespan, optional
            The timespan of the query, by default Timespan.day
        sort : Literal["asc", "desc"], optional
            The sort order of the query, by default "desc"
        limit : PositiveInt, optional
            The limit of the query, by default 49999
        adjusted : bool, optional
            Whether the query is adjusted, by default True
        multiplier : PositiveInt, optional
            The multiplier of the query, by default 1


        Returns
        -------
        Documentation not available.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/forex/load",
            **inputs,
        ).output

        return filter_output(o)
