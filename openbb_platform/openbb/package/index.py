### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from annotated_types import Gt
from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_index(Container):
    """/index
    available
    constituents
    market
    /price
    search
    snapshots
    sp500_multiples
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def available(
        self, provider: Optional[Literal["cboe", "fmp", "yfinance"]] = None, **kwargs
    ) -> OBBject:
        """All indices available from a given provider.

        Parameters
        ----------
        provider : Optional[Literal['cboe', 'fmp', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        use_cache : bool
            When True, the Cboe Index directory will be cached for 24 hours. Set as False to bypass. (provider: cboe)

        Returns
        -------
        OBBject
            results : List[AvailableIndices]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'yfinance']]
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
        symbol : Optional[str]
            Symbol for the index. (provider: cboe, yfinance)
        description : Optional[str]
            Description for the index. Valid only for US indices. (provider: cboe)
        data_delay : Optional[int]
            Data delay for the index. Valid only for US indices. (provider: cboe)
        open_time : Optional[datetime.time]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[datetime.time]
            Closing time for the index. Valid only for US indices. (provider: cboe)
        time_zone : Optional[str]
            Time zone for the index. Valid only for US indices. (provider: cboe)
        tick_days : Optional[str]
            The trading days for the index. Valid only for US indices. (provider: cboe)
        tick_frequency : Optional[str]
            The frequency of the index ticks. Valid only for US indices. (provider: cboe)
        tick_period : Optional[str]
            The period of the index ticks. Valid only for US indices. (provider: cboe)
        stock_exchange : Optional[str]
            Stock exchange where the index is listed. (provider: fmp)
        exchange_short_name : Optional[str]
            Short name of the stock exchange where the index is listed. (provider: fmp)
        code : Optional[str]
            ID code for keying the index in the OpenBB Terminal. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.available(provider="yfinance").to_df()
        """  # noqa: E501

        return self._run(
            "/index/available",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/available",
                        ("cboe", "fmp", "yfinance"),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @validate
    def constituents(
        self,
        index: Annotated[
            str,
            OpenBBCustomParameter(description="Index to fetch the constituents of."),
        ],
        provider: Optional[Literal["cboe", "fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Index Constituents.

        Parameters
        ----------
        index : str
            Index to fetch the constituents of.
        provider : Optional[Literal['cboe', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[IndexConstituents]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp']]
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
        name : Optional[str]
            Name of the constituent company in the index.
        security_type : Optional[str]
            The type of security represented. (provider: cboe)
        last_price : Optional[float]
            Last price for the symbol. (provider: cboe)
        open : Optional[float]
            The open price. (provider: cboe)
        high : Optional[float]
            The high price. (provider: cboe)
        low : Optional[float]
            The low price. (provider: cboe)
        close : Optional[float]
            The close price. (provider: cboe)
        volume : Optional[int]
            The trading volume. (provider: cboe)
        prev_close : Optional[float]

        change : Optional[float]
            Change in price. (provider: cboe)
        change_percent : Optional[float]
            Change in price as a normalized percentage. (provider: cboe)
        tick : Optional[str]
            Whether the last sale was an up or down tick. (provider: cboe)
        last_trade_time : Optional[datetime]
            Last trade timestamp for the symbol. (provider: cboe)
        asset_type : Optional[str]
            Type of asset. (provider: cboe)
        sector : Optional[str]
            Sector the constituent company in the index belongs to. (provider: fmp)
        sub_sector : Optional[str]
            Sub-sector the constituent company in the index belongs to. (provider: fmp)
        headquarter : Optional[str]
            Location of the headquarter of the constituent company in the index. (provider: fmp)
        date_first_added : Optional[Union[str, date]]
            Date the constituent company was added to the index. (provider: fmp)
        cik : Optional[int]
            Central Index Key (CIK) for the requested entity. (provider: fmp)
        founded : Optional[Union[str, date]]
            Founding year of the constituent company in the index. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.constituents("dowjones", provider="fmp").to_df()
        >>> #### Providers other than FMP will use the ticker symbol. ####
        >>> obb.index.constituents("BEP50P", provider="cboe").to_df()
        """  # noqa: E501

        return self._run(
            "/index/constituents",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/constituents",
                        ("cboe", "fmp"),
                    )
                },
                standard_params={
                    "index": index,
                },
                extra_params=kwargs,
            )
        )

    @validate
    @deprecated(
        "This endpoint is deprecated; use `/index/price/historical` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.3.",
        category=OpenBBDeprecationWarning,
    )
    def market(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: cboe, intrinio, polygon, yfinance."
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
        interval: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Time interval of the data to return."),
        ] = "1d",
        limit: Annotated[
            Optional[Annotated[int, Gt(gt=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10000,
        sort: Annotated[
            Optional[Literal["asc", "desc"]],
            OpenBBCustomParameter(
                description="Sort the data in ascending or descending order."
            ),
        ] = "asc",
        provider: Optional[
            Literal["cboe", "fmp", "intrinio", "polygon", "yfinance"]
        ] = None,
        **kwargs
    ) -> OBBject:
        """Historical Market Indices.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: cboe, intrinio, polygon, yfinance.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        interval : Optional[str]
            Time interval of the data to return.
        limit : Optional[Annotated[int, Gt(gt=0)]]
            The number of data entries to return.
        sort : Optional[Literal['asc', 'desc']]
            Sort the data in ascending or descending order.
        provider : Optional[Literal['cboe', 'fmp', 'intrinio', 'polygon', 'yfinance'...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        use_cache : bool
            When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass. (provider: cboe)
        timeseries : Optional[Annotated[int, Ge(ge=0)]]
            Number of days to look back. (provider: fmp)
        tag : Optional[str]
            Index tag. (provider: intrinio)
        type : Optional[str]
            Index type. (provider: intrinio)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : int
            Multiplier of the timespan. (provider: polygon)
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Time period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        rounding : bool
            Round prices to two decimals? (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[MarketIndices]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'intrinio', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MarketIndices
        -------------
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
        >>> obb.index.market(symbol="SPX", interval="1d", limit=10000, sort="asc")
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; use `/index/price/historical` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.3.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/index/market",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/market",
                        ("cboe", "fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "limit": limit,
                    "sort": sort,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {
                        "multiple_items_allowed": [
                            "cboe",
                            "intrinio",
                            "polygon",
                            "yfinance",
                        ]
                    }
                },
            )
        )

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import index_price

        return index_price.ROUTER_index_price(command_runner=self._command_runner)

    @validate
    def search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        is_symbol: Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject:
        """Filters indices for rows containing the query.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        use_cache : bool
            When True, the Cboe Index directory will be cached for 24 hours. Set as False to bypass. (provider: cboe)

        Returns
        -------
        OBBject
            results : List[IndexSearch]
                Serializable results.
            provider : Optional[Literal['cboe']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IndexSearch
        -----------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the index.
        description : Optional[str]
            Description for the index. (provider: cboe)
        data_delay : Optional[int]
            Data delay for the index. Valid only for US indices. (provider: cboe)
        currency : Optional[str]
            Currency for the index. (provider: cboe)
        time_zone : Optional[str]
            Time zone for the index. Valid only for US indices. (provider: cboe)
        open_time : Optional[datetime.time]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[datetime.time]
            Closing time for the index. Valid only for US indices. (provider: cboe)
        tick_days : Optional[str]
            The trading days for the index. Valid only for US indices. (provider: cboe)
        tick_frequency : Optional[str]
            Tick frequency for the index. Valid only for US indices. (provider: cboe)
        tick_period : Optional[str]
            Tick period for the index. Valid only for US indices. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.search(query='SPX', provider='cboe').to_df()
        """  # noqa: E501

        return self._run(
            "/index/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/search",
                        ("cboe",),
                    )
                },
                standard_params={
                    "query": query,
                    "is_symbol": is_symbol,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def snapshots(
        self,
        region: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="The region to return data for - i.e. 'us' or 'eu'."
            ),
        ] = None,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject:
        """Index Snapshots. Current levels for all indices from a provider, grouped by `region`.

        Parameters
        ----------
        region : Optional[str]
            The region to return data for - i.e. 'us' or 'eu'.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[IndexSnapshots]
                Serializable results.
            provider : Optional[Literal['cboe']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IndexSnapshots
        --------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the index.
        currency : Optional[str]
            Currency of the index.
        price : Optional[float]
            Current price of the index.
        open : Optional[float]
            The open price.
        high : Optional[float]
            The high price.
        low : Optional[float]
            The low price.
        close : Optional[float]
            The close price.
        volume : Optional[int]
            The trading volume.
        prev_close : Optional[float]

        change : Optional[float]
            Change in value of the index.
        change_percent : Optional[float]
            Change, in normalized percentage points, of the index.
        bid : Optional[float]
            Current bid price. (provider: cboe)
        ask : Optional[float]
            Current ask price. (provider: cboe)
        last_trade_time : Optional[datetime]
            Last trade timestamp for the symbol. (provider: cboe)
        status : Optional[str]
            Status of the market, open or closed. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.snapshots(region="us",provider="cboe").to_df()
        """  # noqa: E501

        return self._run(
            "/index/snapshots",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/snapshots",
                        ("cboe",),
                    )
                },
                standard_params={
                    "region": region,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def sp500_multiples(
        self,
        series_name: Annotated[
            Literal[
                "shiller_pe_month",
                "shiller_pe_year",
                "pe_year",
                "pe_month",
                "dividend_year",
                "dividend_month",
                "dividend_growth_quarter",
                "dividend_growth_year",
                "dividend_yield_year",
                "dividend_yield_month",
                "earnings_year",
                "earnings_month",
                "earnings_growth_year",
                "earnings_growth_quarter",
                "real_earnings_growth_year",
                "real_earnings_growth_quarter",
                "earnings_yield_year",
                "earnings_yield_month",
                "real_price_year",
                "real_price_month",
                "inflation_adjusted_price_year",
                "inflation_adjusted_price_month",
                "sales_year",
                "sales_quarter",
                "sales_growth_year",
                "sales_growth_quarter",
                "real_sales_year",
                "real_sales_quarter",
                "real_sales_growth_year",
                "real_sales_growth_quarter",
                "price_to_sales_year",
                "price_to_sales_quarter",
                "price_to_book_value_year",
                "price_to_book_value_quarter",
                "book_value_year",
                "book_value_quarter",
            ],
            OpenBBCustomParameter(
                description="The name of the series. Defaults to 'pe_month'."
            ),
        ] = "pe_month",
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        transform: Annotated[
            Literal["diff", "rdiff", "cumul", "normalize", None],
            OpenBBCustomParameter(
                description="Transform the data as difference, percent change, cumulative, or normalize."
            ),
        ] = None,
        collapse: Annotated[
            Literal["daily", "weekly", "monthly", "quarterly", "annual", None],
            OpenBBCustomParameter(
                description="Collapse the frequency of the time series."
            ),
        ] = None,
        provider: Optional[Literal["nasdaq"]] = None,
        **kwargs
    ) -> OBBject:
        """Historical S&P 500 multiples and Shiller PE ratios.

        Parameters
        ----------
        series_name : Literal['shiller_pe_month', 'shiller_pe_year', 'pe_year', 'pe_month', 'd...
            The name of the series. Defaults to 'pe_month'.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        transform : Literal['diff', 'rdiff', 'cumul', 'normalize', None]
            Transform the data as difference, percent change, cumulative, or normalize.
        collapse : Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual', None]
            Collapse the frequency of the time series.
        provider : Optional[Literal['nasdaq']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'nasdaq' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SP500Multiples]
                Serializable results.
            provider : Optional[Literal['nasdaq']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SP500Multiples
        --------------
        date : date
            The date of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.index.sp500_multiples(series_name="shiller_pe_year", provider="nasdaq").to_df()
        """  # noqa: E501

        return self._run(
            "/index/sp500_multiples",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/index/sp500_multiples",
                        ("nasdaq",),
                    )
                },
                standard_params={
                    "series_name": series_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "transform": transform,
                    "collapse": collapse,
                },
                extra_params=kwargs,
            )
        )
