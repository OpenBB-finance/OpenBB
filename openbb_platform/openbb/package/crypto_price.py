### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_crypto_price(Container):
    """/crypto/price
    historical
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed: fmp, polygon, yfinance."
            ),
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
        provider: Optional[Literal["fmp", "polygon", "tiingo", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get historical price data for cryptocurrency pair(s) within a provider.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed: fmp, polygon, yfinance.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'polygon', 'tiingo', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        timeseries : Optional[Annotated[int, Ge(ge=0)]]
            Number of days to look back. (provider: fmp)
        interval : Optional[Union[Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], str, Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
            Data granularity. (provider: fmp, polygon, tiingo, yfinance)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: polygon)
        exchanges : Optional[List[str]]
            To limit the query to a subset of exchanges e.g. ['POLONIEX', 'GDAX'] (provider: tiingo)
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Time period of the data to return. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[CryptoHistorical]
                Serializable results.
            provider : Optional[Literal['fmp', 'polygon', 'tiingo', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CryptoHistorical
        ----------------
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
        vwap : Optional[Annotated[float, Gt(gt=0)]]
            Volume Weighted Average Price over the period.
        adj_close : Optional[float]
            The adjusted close price. (provider: fmp)
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
        transactions : Optional[Union[Annotated[int, Gt(gt=0)], int]]
            Number of transactions for the symbol in the time period. (provider: polygon, tiingo)
        volume_notional : Optional[float]
            The last size done for the asset on the specific date in the quote currency. The volume of the asset on the specific date in the quote currency. (provider: tiingo)

        Example
        -------
        >>> from openbb import obb
        >>> obb.crypto.price.historical(symbol="BTCUSD")
        >>> obb.crypto.price.historical("BTCUSD", start_date="2024-01-01", end_date="2024-01-31")
        >>> obb.crypto.price.historical("ETH-USD", provider="yfinance", interval="1mo", start_date="2024-01-01", end_date="2024-12-31")
        >>> obb.crypto.price.historical("BTCUSD,ETH-USD", provider="yfinance", interval="1d", start_date="2024-01-01", end_date="2024-01-31")
        >>> obb.crypto.price.historical(["BTCUSD", "ETH-USD"], start_date="2024-01-01", end_date="2024-01-31")
        """  # noqa: E501

        return self._run(
            "/crypto/price/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/crypto/price/historical",
                        ("fmp", "polygon", "tiingo", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {"multiple_items_allowed": ["fmp", "polygon", "yfinance"]}
                },
            )
        )
