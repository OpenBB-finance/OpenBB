### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

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
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): cboe, fmp, intrinio, polygon, yfinance."
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
        chart: Annotated[
            bool,
            OpenBBField(
                description="Whether to create a chart or not, by default False."
            ),
        ] = False,
        provider: Annotated[
            Optional[Literal["cboe", "fmp", "intrinio", "polygon", "yfinance"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, fmp, intrinio, polygon, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Historical Index Levels.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): cboe, fmp, intrinio, polygon, yfinance.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cboe, fmp, intrinio, polygon, yfinance.
        interval : Union[Literal['1m', '1d'], Literal['1m', '5m', '15m', '30m', '1h', '4h', '1d'], str, Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1W', '1M', '1Q']]
            Time interval of the data to return. The most recent trading day is not including in daily historical data. Intraday data is only available for the most recent trading day at 1 minute intervals. (provider: cboe);
            Time interval of the data to return. (provider: fmp);
            Time interval of the data to return. The numeric portion of the interval can be any positive integer. The letter portion can be one of the following: s, m, h, d, W, M, Q, Y (provider: polygon);
            Time interval of the data to return. (provider: yfinance)
        use_cache : bool
            When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio, polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[IndexHistorical]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
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
        calls_volume : Optional[float]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[float]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[float]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
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
                        ("cboe", "fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                chart=chart,
                info={
                    "symbol": {
                        "cboe": {"multiple_items_allowed": True, "choices": None},
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                        "polygon": {"multiple_items_allowed": True, "choices": None},
                        "yfinance": {"multiple_items_allowed": True, "choices": None},
                    },
                    "interval": {
                        "cboe": {
                            "multiple_items_allowed": False,
                            "choices": ["1m", "1d"],
                        },
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
