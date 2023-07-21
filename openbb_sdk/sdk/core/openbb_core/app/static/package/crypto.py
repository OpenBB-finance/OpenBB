### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import Literal, Optional, Union

from pydantic import validate_arguments

from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_crypto(Container):
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
        """Crypto Intraday Price.

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        start_date : Optional[date]
            The start date of the stock data from which to retrieve the data.
        end_date : Optional[date]
            The end date of the stock data up to which to retrieve the data.


        Returns
        -------
        date : datetime
            The date of the stock.
        open : PositiveFloat
            The open price of the stock.
        high : PositiveFloat
            The high price of the stock.
        low : PositiveFloat
            The low price of the stock.
        close : PositiveFloat
            The close price of the stock.
        adj_close : Optional[PositiveFloat]
            The adjusted close price of the stock.
        volume : PositiveFloat
            The volume of the stock.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Cryptocurrencies

        Parameter
        ---------
        timeseries : Optional[int]
            The number of days to look back.
        serietype : Optional[Literal["line"]]
            The type of the series. Only "line" is supported.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/crypto/get_v2_aggs_ticker__cryptoticker__range__multiplier___timespan___from___to

        Parameters
        ----------
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
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/crypto/load",
            **inputs,
        ).output

        return filter_output(o)
