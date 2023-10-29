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


class ROUTER_futures(Container):
    """/futures
    curve
    load
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def curve(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        provider: Union[Literal["cboe", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Futures Historical Price. Futures historical data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        date : Union[datetime.date, None]
            A specific date to get data for.
        provider : Union[Literal['cboe', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[FuturesCurve]]
                Serializable results.
            provider : Union[Literal['cboe', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FuturesCurve
        ------------
        expiration : str
            Futures expiration month.
        price : Optional[Union[float]]
            The close price of the symbol.
        symbol : Optional[Union[str]]
            The trading symbol for the tenor of future. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.futures.curve(symbol="VX")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "date": date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/futures/curve",
            **inputs,
        )

    @validate
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
        provider: Union[Literal["yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Futures Historical Price. Futures historical data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        expiration : Union[str, None]
            Future expiry date with format YYYY-MM
        provider : Union[Literal['yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'yfinance' if there is
            no default.
        interval : Optional[Union[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
            Data granularity. (provider: yfinance)
        period : Optional[Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]]
            Time period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        adjust : bool
            Adjust all the data automatically. (provider: yfinance)
        back_adjust : bool
            Back-adjusted data to mimic true historical prices. (provider: yfinance)

        Returns
        -------
        OBBject
            results : Union[List[FuturesHistorical]]
                Serializable results.
            provider : Union[Literal['yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FuturesHistorical
        -----------------
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.futures.load(symbol="ES")
        """  # noqa: E501

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
        )

        return self._run(
            "/futures/load",
            **inputs,
        )
