### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, validate_arguments

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_forex(Container):
    @filter_call
    @validate_arguments
    def pairs(
        self,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs,
    ) -> Obbject[List]:
        """Forex Available Pairs.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        All fields are standardized.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        ForexPairs
        ----------
        name : str
            The name of the currency pair.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        ForexPairs
        ----------
        symbol : str
            The symbol of the currency pair.
        currency : str
            The base currency of the currency pair.
        stockExchange : Optional[str]
            The stock exchange of the currency pair.
        exchange_short_name : Optional[str]
            The short name of the stock exchange of the currency pair.

        polygon
        =======

        Parameters
        ----------
        symbol : Optional[str]
            Symbol of the pair to search.
        date : Optional[date]
            A specific date to get data for.
        search : Optional[str]
            Search for terms within the ticker and/or company name.
        active : Optional[Literal[True, False]]
            Specify if the tickers returned should be actively traded on the queried date.
        order : Optional[Literal['asc', 'desc']]
            Order data by ascending or descending.
        sort : Optional[Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc']]
            Sort field used for ordering.
        limit : Optional[PositiveInt]
            The number of data entries to return.


        ForexPairs
        ----------
        market : str
            The name of the trading market. Always 'fx'.
        locale : str
            The locale of the currency pair.
        currency_symbol : str
            The symbol of the quote currency.
        currency_name : str
            The name of the quote currency.
        base_currency_symbol : str
            The symbol of the base currency.
        base_currency_name : str
            The name of the base currency.
        last_updated_utc : datetime
            The last updated timestamp in UTC.
        delisted_utc : Optional[datetime]
            The delisted timestamp in UTC."""  # noqa: E501
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
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon", "yfinance"]] = None,
        **kwargs,
    ) -> Obbject[BaseModel]:
        """Forex Intraday Price.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon, yfinance]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format.

        Returns
        -------
        Obbject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        ForexEOD
        --------
        date : datetime
            The date of the data.
        open : PositiveFloat
            The open price of the symbol.
        high : PositiveFloat
            The high price of the symbol.
        low : PositiveFloat
            The low price of the symbol.
        close : PositiveFloat
            The close price of the symbol.
        volume : NonNegativeFloat
            The volume of the symbol.
        vwap : Optional[PositiveFloat]
            Volume Weighted Average Price of the symbol.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        ForexEOD
        --------
        adjClose : float
            Adjusted Close Price of the symbol.
        unadjustedVolume : float
            Unadjusted volume of the symbol.
        change : float
            Change in the price of the symbol from the previous day.
        changePercent : float
            Change \\% in the price of the symbol.
        label : str
            Human readable format of the date.
        changeOverTime : float
            Change \\% in the price of the symbol over a period of time.

        polygon
        =======

        Parameters
        ----------
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            The timespan of the data.
        sort : Literal['asc', 'desc']
            Sort order of the data.
        limit : PositiveInt
            The number of data entries to return.
        adjusted : bool
            Whether the data is adjusted.
        multiplier : PositiveInt
            The multiplier of the timespan.


        ForexEOD
        --------
        n : PositiveInt
            The number of transactions for the symbol in the time period.

        yfinance
        ========

        Parameters
        ----------
        interval : Optional[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]
            Data granularity.
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Period of the data to return (quarterly or annually).


        ForexEOD
        --------
        All fields are standardized."""  # noqa: E501
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
