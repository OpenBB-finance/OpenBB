### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_derivatives_futures(Container):
    """/derivatives/futures
    curve
    historical
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def curve(
        self,
        symbol: Annotated[str, OpenBBField(description="Symbol to get data for.")],
        date: Annotated[
            Union[datetime.date, str, None, List[Union[datetime.date, str, None]]],
            OpenBBField(
                description="A specific date to get data for. Multiple comma separated items allowed for provider(s): yfinance."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Futures Term Structure, current or historical.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        date : Union[date, str, None, List[Union[date, str, None]]]
            A specific date to get data for. Multiple comma separated items allowed for provider(s): yfinance.
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.

        Returns
        -------
        OBBject
            results : List[FuturesCurve]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FuturesCurve
        ------------
        date : Optional[date]
            The date of the data.
        expiration : str
            Futures expiration month.
        price : Optional[float]
            The price of the futures contract.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.derivatives.futures.curve(symbol='NG', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/derivatives/futures/curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "derivatives.futures.curve",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "date": date,
                },
                extra_params=kwargs,
                info={
                    "date": {
                        "yfinance": {"multiple_items_allowed": True, "choices": None}
                    }
                },
            )
        )

    @exception_handler
    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): yfinance."
            ),
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        expiration: Annotated[
            Optional[str],
            OpenBBField(description="Future expiry date with format YYYY-MM"),
        ] = None,
        provider: Annotated[
            Optional[Literal["yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Historical futures prices.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): yfinance.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        expiration : Optional[str]
            Future expiry date with format YYYY-MM
        provider : Optional[Literal['yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: yfinance.
        interval : Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1W', '1M', '1Q']
            Time interval of the data to return. (provider: yfinance)

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
            extra : Dict[str, Any]
                Extra info.

        FuturesHistorical
        -----------------
        date : datetime
            The date of the data.
        open : float
            The open price.
        high : float
            The high price.
        low : float
            The low price.
        close : float
            The close price.
        volume : float
            The trading volume.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.derivatives.futures.historical(symbol='ES', provider='yfinance')
        >>> # Enter multiple symbols.
        >>> obb.derivatives.futures.historical(symbol='ES,NQ', provider='yfinance')
        >>> # Enter expiration dates as "YYYY-MM".
        >>> obb.derivatives.futures.historical(symbol='ES', provider='yfinance', expiration='2025-12')
        """  # noqa: E501

        return self._run(
            "/derivatives/futures/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "derivatives.futures.historical",
                        ("yfinance",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "expiration": expiration,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "yfinance": {"multiple_items_allowed": True, "choices": None}
                    }
                },
            )
        )
