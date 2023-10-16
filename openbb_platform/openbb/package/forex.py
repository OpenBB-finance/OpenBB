### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_forex(Container):
    """/forex
    load
    pairs
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def load(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol Pair to get data for in CURR1-CURR2 or CURR1CURR2 format."
            ),
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
        provider: Union[Literal["fmp", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Forex Intraday Price.

        Parameters
        ----------
        symbol : str
            Symbol Pair to get data for in CURR1-CURR2 or CURR1CURR2 format.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'polygon', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        interval : Optional[Union[Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
            Data granularity. (provider: fmp, yfinance)
        multiplier : int
            Multiplier of the timespan. (provider: polygon)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        period : Optional[Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]]
            Time period of the data to return. (provider: yfinance)

        Returns
        -------
        OBBject
            results : Union[List[ForexHistorical]]
                Serializable results.
            provider : Union[Literal['fmp', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ForexHistorical
        ---------------
        date : datetime
            The date of the data.
        open : float
            The open price of the symbol.
        high : float
            The high price of the symbol.
        low : float
            The low price of the symbol.
        close : float
            The close price of the symbol.
        volume : float
            The volume of the symbol.
        vwap : Optional[Union[typing_extensions.Annotated[float, Gt(gt=0)]]]
            Volume Weighted Average Price of the symbol.
        adj_close : Optional[Union[float]]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[Union[float]]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[Union[float]]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[Union[float]]
            Change % in the price of the symbol. (provider: fmp)
        label : Optional[Union[str]]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[Union[float]]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        transactions : Optional[Union[typing_extensions.Annotated[int, Gt(gt=0)]]]
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

        return self._run(
            "/forex/load",
            **inputs,
        )

    @validate
    def pairs(
        self,
        provider: Union[Literal["fmp", "intrinio", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Forex Available Pairs.

        Parameters
        ----------
        provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        symbol : Optional[Union[str]]
            Symbol of the pair to search. (provider: polygon)
        date : Optional[Union[datetime.date]]
            A specific date to get data for. (provider: polygon)
        search : Optional[Union[str]]
            Search for terms within the ticker and/or company name. (provider: polygon)
        active : Optional[Union[bool]]
            Specify if the tickers returned should be actively traded on the queried date. (provider: polygon)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order data by ascending or descending. (provider: polygon)
        sort : Optional[Union[Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc']]]
            Sort field used for ordering. (provider: polygon)
        limit : Optional[Union[typing_extensions.Annotated[int, Gt(gt=0)]]]
            The number of data entries to return. (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[ForexPairs]]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ForexPairs
        ----------
        name : str
            Name of the currency pair.
        symbol : Optional[Union[str]]
            Symbol of the currency pair. (provider: fmp)
        currency : Optional[Union[str]]
            Base currency of the currency pair. (provider: fmp)
        stock_exchange : Optional[Union[str]]
            Stock exchange of the currency pair. (provider: fmp)
        exchange_short_name : Optional[Union[str]]
            Short name of the stock exchange of the currency pair. (provider: fmp)
        code : Optional[Union[str]]
            Code of the currency pair. (provider: intrinio)
        base_currency : Optional[Union[str]]
            ISO 4217 currency code of the base currency. (provider: intrinio)
        quote_currency : Optional[Union[str]]
            ISO 4217 currency code of the quote currency. (provider: intrinio)
        market : Optional[Union[str]]
            Name of the trading market. Always 'fx'. (provider: polygon)
        locale : Optional[Union[str]]
            Locale of the currency pair. (provider: polygon)
        currency_symbol : Optional[Union[str]]
            The symbol of the quote currency. (provider: polygon)
        currency_name : Optional[Union[str]]
            Name of the quote currency. (provider: polygon)
        base_currency_symbol : Optional[Union[str]]
            The symbol of the base currency. (provider: polygon)
        base_currency_name : Optional[Union[str]]
            Name of the base currency. (provider: polygon)
        last_updated_utc : Optional[Union[datetime]]
            The last updated timestamp in UTC. (provider: polygon)
        delisted_utc : Optional[Union[datetime]]
            The delisted timestamp in UTC. (provider: polygon)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/forex/pairs",
            **inputs,
        )
