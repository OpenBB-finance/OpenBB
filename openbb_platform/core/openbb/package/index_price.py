### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_index_price(Container):
    """/index/price
    historical
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, list[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, polygon, yfinance."
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
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "polygon", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Historical Index Levels.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon, yfinance.
        symbol : Union[str, list[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, polygon, yfinance.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        interval : str
            Time interval of the data to return. (provider: fmp, polygon, yfinance)
            Choices for fmp: '1m', '5m', '15m', '30m', '1h', '4h', '1d'
            Choices for yfinance: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1W', '1M', '1Q'
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio, polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. (provider: polygon)

        Returns
        -------
        OBBject
            results : list[IndexHistorical]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        IndexHistorical
        ---------------
        date : Union[date, datetime]
            The date of the data.
        open : Optional[Annotated[float, Strict(strict=True)]]
            The open price.
        high : Optional[Annotated[float, Strict(strict=True)]]
            The high price.
        low : Optional[Annotated[float, Strict(strict=True)]]
            The low price.
        close : Optional[Annotated[float, Strict(strict=True)]]
            The close price.
        volume : Optional[int]
            The trading volume.
        vwap : Optional[float]
            Volume Weighted Average Price over the period. (provider: fmp)
        change : Optional[float]
            Change in the price from the previous close. (provider: fmp)
        change_percent : Optional[float]
            Change in the price from the previous close, as a normalized percent. (provider: fmp)
        transactions : Optional[Annotated[int, Gt(gt=0)]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.index.price.historical(symbol='^GSPC', provider='fmp')
        >>> # Not all providers have the same symbols.
        >>> obb.index.price.historical(symbol='SPX', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/index/price/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "index.price.historical",
                        ("fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                        "polygon": {"multiple_items_allowed": True, "choices": None},
                        "yfinance": {"multiple_items_allowed": True, "choices": None},
                    },
                    "interval": {
                        "fmp": {
                            "multiple_items_allowed": False,
                            "choices": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                        },
                        "yfinance": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "1m",
                                "2m",
                                "5m",
                                "15m",
                                "30m",
                                "60m",
                                "90m",
                                "1h",
                                "1d",
                                "5d",
                                "1W",
                                "1M",
                                "1Q",
                            ],
                        },
                    },
                },
            )
        )
