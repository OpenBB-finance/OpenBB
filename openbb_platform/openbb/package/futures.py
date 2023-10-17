### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data
from typing_extensions import Annotated


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
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(description="Historical date to search curve for."),
        ] = None,
        provider: Optional[Literal["cboe", "yfinance"]] = None,
        **kwargs,
    ) -> OBBject[List[Data]]:
        """Futures Historical Price. Futures historical data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        date : Optional[datetime.date]
            Historical date to search curve for.
        provider : Optional[Literal['cboe', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[FuturesCurve]
                Serializable results.
            provider : Optional[Literal['cboe', 'yfinance']]
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
        price : Optional[float]
            The close price of the symbol.
        symbol : Optional[str]
            The trading symbol for the tenor of future. (provider: cboe)"""  # noqa: E501

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
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
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
        expiration: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Future expiry date with format YYYY-MM"),
        ] = None,
        provider: Optional[Literal["yfinance"]] = None,
        **kwargs,
    ) -> OBBject[List[Data]]:
        """Futures Historical Price. Futures historical data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        expiration : Optional[str]
            Future expiry date with format YYYY-MM
        provider : Optional[Literal['yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'yfinance' if there is
            no default.
        interval : Optional[Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]
            Data granularity. (provider: yfinance)
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
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
            results : List[FuturesHistorical]
                Serializable results.
            provider : Optional[Literal['yfinance']]
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
            The volume of the symbol."""  # noqa: E501

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
