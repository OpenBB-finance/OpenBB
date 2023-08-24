### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from pydantic import validate_arguments

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs


class CLASS_futures(Container):
    """/futures
    curve
    load
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def curve(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="Historical date to search curve for."),
        ] = None,
        chart: bool = False,
        provider: Union[Literal["yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Futures EOD Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        date : Union[datetime.date, NoneType]
            Historical date to search curve for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['yfinance'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'yfinance' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[FuturesCurve]
                Serializable results.
            provider : Union[Literal['yfinance'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        FuturesCurve
        ------------
        expiration : Optional[str]
            Futures expiration month.
        price : Optional[float]
            The close price of the symbol."""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "date": date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/futures/curve",
            **inputs,
        )

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
        expiration: typing_extensions.Annotated[
            Union[str, None],
            OpenBBCustomParameter(description="Future expiry date with format YYYY-MM"),
        ] = None,
        chart: bool = False,
        provider: Union[Literal["yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Futures EOD Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, NoneType, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, NoneType, str]
            End date of the data, in YYYY-MM-DD format.
        expiration : Union[str, NoneType]
            Future expiry date with format YYYY-MM
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['yfinance'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'yfinance' if there is
            no default.
        interval : Union[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], NoneType]
            Data granularity. (provider: yfinance)
        period : Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], NoneType]
            Period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        adjust : bool
            Adjust all the data automatically. (provider: yfinance)
        back_adjust : bool
            Back-adjusted data to mimic true historical prices. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[FuturesEOD]
                Serializable results.
            provider : Union[Literal['yfinance'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        FuturesEOD
        ----------
        date : Optional[datetime]
            The date of the data.
        open : Optional[float]
            The open price of the symbol.
        high : Optional[float]
            The high price of the symbol.
        low : Optional[float]
            The low price of the symbol.
        close : Optional[float]
            The close price of the symbol.
        volume : Optional[float]
            The volume of the symbol."""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
                "expiration": expiration,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/futures/load",
            **inputs,
        )
