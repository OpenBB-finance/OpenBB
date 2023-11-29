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


class ROUTER_index(Container):
    """/index
    available
    constituents
    fred
    market
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def available(
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Available Indices. Available indices for a given provider.

        Parameters
        ----------
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[AvailableIndices]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        AvailableIndices
        ----------------
        name : Optional[str]
            Name of the index.
        currency : Optional[str]
            Currency the index is traded in.
        stock_exchange : Optional[str]
            Stock exchange where the index is listed. (provider: fmp)
        exchange_short_name : Optional[str]
            Short name of the stock exchange where the index is listed. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.available()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/index/available",
            **inputs,
        )

    @validate
    def constituents(
        self,
        index: Annotated[
            Literal["nasdaq", "sp500", "dowjones"],
            OpenBBCustomParameter(
                description="Index for which we want to fetch the constituents."
            ),
        ] = "dowjones",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Index Constituents. Constituents of an index.

        Parameters
        ----------
        index : Literal['nasdaq', 'sp500', 'dowjones']
            Index for which we want to fetch the constituents.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[IndexConstituents]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IndexConstituents
        -----------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the constituent company in the index.
        sector : str
            Sector the constituent company in the index belongs to.
        sub_sector : Optional[str]
            Sub-sector the constituent company in the index belongs to.
        headquarter : Optional[str]
            Location of the headquarter of the constituent company in the index.
        date_first_added : Optional[Union[str, date]]
            Date the constituent company was added to the index.
        cik : int
            Central Index Key (CIK) for the requested entity.
        founded : Optional[Union[str, date]]
            Founding year of the constituent company in the index.

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.constituents(index="dowjones")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "index": index,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/index/constituents",
            **inputs,
        )

    @validate
    def fred(
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
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Fred Indices. Close values for selected Fred indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        next_page : Optional[str]
            Token to get the next page of data from a previous API call. (provider: intrinio)
        all_pages : Optional[bool]
            Returns all pages of data from the API call at once. (provider: intrinio)
        sleep : Optional[float]
            Time to sleep between requests to avoid rate limiting. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[FredIndices]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FredIndices
        -----------
        date : date
            The date of the data.
        value : Optional[float]
            Value of the index.

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.fred(symbol="SPX", limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/index/fred",
            **inputs,
        )

    @validate
    def market(
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
        provider: Optional[Literal["fmp", "intrinio", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Market Indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        timeseries : Optional[Annotated[int, Ge(ge=0)]]
            Number of days to look back. (provider: fmp)
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Data granularity. (provider: fmp)
        tag : Optional[str]
            Index tag. (provider: intrinio)
        type : Optional[str]
            Index type. (provider: intrinio)
        sort : Literal['asc', 'desc']
            Sort order. (provider: intrinio);
            Sort order of the data. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: intrinio, polygon)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : int
            Multiplier of the timespan. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[MarketIndices]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MarketIndices
        -------------
        date : datetime
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
        value : Optional[float]
            Index value. (provider: intrinio)
        transactions : Optional[Annotated[int, Gt(gt=0)]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.market(symbol="SPX")
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
            "/index/market",
            **inputs,
        )
