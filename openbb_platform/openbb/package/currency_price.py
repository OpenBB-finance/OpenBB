### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_currency_price(Container):
    """/currency/price
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
                description="Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format."
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
        provider: Optional[Literal["fmp", "polygon", "tiingo"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Currency Historical Price. Currency historical data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'polygon', 'tiingo']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Data granularity. (provider: fmp, tiingo)
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

        Returns
        -------
        OBBject
            results : List[CurrencyHistorical]
                Serializable results.
            provider : Optional[Literal['fmp', 'polygon', 'tiingo']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CurrencyHistorical
        ------------------
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
        volume : Optional[float]
            The trading volume.
        vwap : Optional[Annotated[float, Gt(gt=0)]]
            Volume Weighted Average Price over the period.
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
        transactions : Optional[Annotated[int, Gt(gt=0)]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.currency.price.historical(symbol="EURUSD")
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
            "/currency/price/historical",
            **inputs,
        )
