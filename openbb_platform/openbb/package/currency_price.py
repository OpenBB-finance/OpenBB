### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
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
                description="Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed: polygon, yfinance."
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
        """
        Currency Historical Price. Currency historical data.

        Currency historical prices refer to the past exchange rates of one currency against
        another over a specific period.
        This data provides insight into the fluctuations and trends in the foreign exchange market,
        helping analysts, traders, and economists understand currency performance,
        evaluate economic health, and make predictions about future movements.


            Parameters
            ----------
            symbol : Union[str, List[str]]
                Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. Multiple items allowed: polygon, yfinance.
            start_date : Union[datetime.date, None, str]
                Start date of the data, in YYYY-MM-DD format.
            end_date : Union[datetime.date, None, str]
                End date of the data, in YYYY-MM-DD format.
            provider : Optional[Literal['fmp', 'polygon', 'tiingo', 'yfinance']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'fmp' if there is
                no default.
            interval : Optional[Union[Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], str, Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
                Data granularity. (provider: fmp, polygon, tiingo, yfinance)
            sort : Literal['asc', 'desc']
                Sort order of the data. (provider: polygon)
            limit : int
                The number of data entries to return. (provider: polygon)
            period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
                Time period of the data to return. (provider: yfinance)

            Returns
            -------
            OBBject
                results : List[CurrencyHistorical]
                    Serializable results.
                provider : Optional[Literal['fmp', 'polygon', 'tiingo', 'yfinance']]
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
            transactions : Optional[Annotated[int, Gt(gt=0)]]
                Number of transactions for the symbol in the time period. (provider: polygon)

            Example
            -------
            >>> from openbb import obb
            >>> obb.currency.price.historical(symbol="EURUSD")
            >>> # Filter historical data with specific start and end date.
            >>> obb.currency.price.historical(symbol='EURUSD', start_date='2023-01-01', end_date='20213-12-31')
            >>> # Get data with different granularity.
            >>> obb.currency.price.historical(symbol='EURUSD', interval='15m', provider='polygon')
        """  # noqa: E501

        return self._run(
            "/currency/price/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/currency/price/historical",
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
                    "symbol": {"multiple_items_allowed": ["polygon", "yfinance"]}
                },
            )
        )
