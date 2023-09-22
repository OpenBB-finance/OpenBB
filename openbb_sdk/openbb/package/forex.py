### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class ROUTER_forex(Container):
    """/forex
    load
    pairs
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def load(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        start_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        provider: Union[Literal["fmp", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Forex Intraday Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Data granularity. (provider: fmp)
        multiplier : PositiveInt
            Multiplier of the timespan. (provider: polygon)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : PositiveInt
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[ForexHistorical]
                Serializable results.
            provider : Union[Literal['fmp', 'polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        ForexHistorical
        ---------------
        date : Optional[datetime]
            The date of the data.
        open : Optional[PositiveFloat]
            The open price of the symbol.
        high : Optional[PositiveFloat]
            The high price of the symbol.
        low : Optional[PositiveFloat]
            The low price of the symbol.
        close : Optional[PositiveFloat]
            The close price of the symbol.
        volume : Optional[NonNegativeFloat]
            The volume of the symbol.
        vwap : Optional[PositiveFloat]
            Volume Weighted Average Price of the symbol.
        adj_close : Optional[float]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[float]
            Change % in the price of the symbol. (provider: fmp)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        transactions : Optional[PositiveInt]
            Number of transactions for the symbol in the time period. (provider: polygon)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/forex/load",
            **inputs,
        )

    @validate_arguments
    def pairs(
        self,
        provider: Union[Literal["fmp", "intrinio", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Forex Available Pairs.

        Parameters
        ----------
        provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        symbol : Union[str, None]
            Symbol of the pair to search. (provider: polygon)
        date : Union[datetime.date, None]
            A specific date to get data for. (provider: polygon)
        search : Union[str, None]
            Search for terms within the ticker and/or company name. (provider: polygon)
        active : Union[Literal[True, False], None]
            Specify if the tickers returned should be actively traded on the queried date. (provider: polygon)
        order : Union[Literal['asc', 'desc'], None]
            Order data by ascending or descending. (provider: polygon)
        sort : Union[Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc'], None]
            Sort field used for ordering. (provider: polygon)
        limit : Union[pydantic.types.PositiveInt, None]
            The number of data entries to return. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[ForexPairs]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        ForexPairs
        ----------
        name : Optional[str]
            Name of the currency pair.
        symbol : Optional[str]
            Symbol of the currency pair. (provider: fmp)
        currency : Optional[str]
            Base currency of the currency pair. (provider: fmp)
        stock_exchange : Optional[str]
            Stock exchange of the currency pair. (provider: fmp)
        exchange_short_name : Optional[str]
            Short name of the stock exchange of the currency pair. (provider: fmp)
        code : Optional[str]
            Code of the currency pair. (provider: intrinio)
        base_currency : Optional[str]
            ISO 4217 currency code of the base currency. (provider: intrinio)
        quote_currency : Optional[str]
            ISO 4217 currency code of the quote currency. (provider: intrinio)
        market : Optional[str]
            The name of the trading market. Always 'fx'. (provider: polygon)
        locale : Optional[str]
            The locale of the currency pair. (provider: polygon)
        currency_symbol : Optional[str]
            The symbol of the quote currency. (provider: polygon)
        currency_name : Optional[str]
            The name of the quote currency. (provider: polygon)
        base_currency_symbol : Optional[str]
            The symbol of the base currency. (provider: polygon)
        base_currency_name : Optional[str]
            The name of the base currency. (provider: polygon)
        last_updated_utc : Optional[datetime]
            The last updated timestamp in UTC. (provider: polygon)
        delisted_utc : Optional[datetime]
            The delisted timestamp in UTC. (provider: polygon)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/forex/pairs",
            **inputs,
        )
