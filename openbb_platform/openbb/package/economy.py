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


class ROUTER_economy(Container):
    """/economy
    available_indices
    calendar
    const
    cot
    cot_search
    cpi
    european_index
    european_index_constituents
    fred_index
    gdpforecast
    gdpnom
    gdpreal
    index
    index_search
    index_snapshots
    risk
    sp500_multiples
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def available_indices(
        self, provider: Union[Literal["cboe", "fmp", "yfinance"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Available Indices. Available indices for a given provider.

        Parameters
        ----------
        provider : Union[Literal['cboe', 'fmp', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        europe : bool
            Filter for European indices. False for US indices. (provider: cboe)

        Returns
        -------
        OBBject
            results : Union[List[AvailableIndices]]
                Serializable results.
            provider : Union[Literal['cboe', 'fmp', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        AvailableIndices
        ----------------
        name : Optional[Union[str]]
            Name of the index.
        currency : Optional[Union[str]]
            Currency the index is traded in.
        isin : Optional[Union[str]]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        region : Optional[Union[str]]
            Region for the index. Valid only for European indices (provider: cboe)
        symbol : Optional[Union[str]]
            Symbol for the index. (provider: cboe, yfinance)
        description : Optional[Union[str]]
            Description for the index. Valid only for US indices. (provider: cboe)
        data_delay : Optional[Union[int]]
            Data delay for the index. Valid only for US indices. (provider: cboe)
        open_time : Optional[Union[datetime.time]]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[Union[datetime.time]]
            Closing time for the index. Valid only for US indices. (provider: cboe)
        time_zone : Optional[Union[str]]
            Time zone for the index. Valid only for US indices. (provider: cboe)
        tick_days : Optional[Union[str]]
            The trading days for the index. Valid only for US indices. (provider: cboe)
        tick_frequency : Optional[Union[str]]
            The frequency of the index ticks. Valid only for US indices. (provider: cboe)
        tick_period : Optional[Union[str]]
            The period of the index ticks. Valid only for US indices. (provider: cboe)
        stock_exchange : Optional[Union[str]]
            Stock exchange where the index is listed. (provider: fmp)
        exchange_short_name : Optional[Union[str]]
            Short name of the stock exchange where the index is listed. (provider: fmp)
        code : Optional[Union[str]]
            ID code for keying the index in the OpenBB Terminal. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.available_indices()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/economy/available_indices",
            **inputs,
        )

    @validate
    def calendar(
        self,
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
        provider: Union[Literal["fmp", "nasdaq", "tradingeconomics"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Economic Calendar.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'nasdaq', 'tradingeconomics'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        country : Optional[Union[str, List[str]]]
            Country of the event (provider: nasdaq, tradingeconomics)
        importance : Literal['Low', 'Medium', 'High']
            Importance of the event. (provider: tradingeconomics)
        group : Literal['interest rate', 'inflation', 'bonds', 'consumer', 'gdp', 'government', 'housing', 'labour', 'markets', 'money', 'prices', 'trade', 'business']
            Grouping of events (provider: tradingeconomics)

        Returns
        -------
        OBBject
            results : Union[List[EconomicCalendar]]
                Serializable results.
            provider : Union[Literal['fmp', 'nasdaq', 'tradingeconomics'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EconomicCalendar
        ----------------
        date : Optional[Union[datetime]]
            The date of the data.
        country : Optional[Union[str]]
            Country of event.
        event : Optional[Union[str]]
            Event name.
        reference : Optional[Union[str]]
            Abbreviated period for which released data refers to.
        source : Optional[Union[str]]
            Source of the data.
        sourceurl : Optional[Union[str]]
            Source URL.
        actual : Optional[Union[str, float]]
            Latest released value.
        previous : Optional[Union[str, float]]
            Value for the previous period after the revision (if revision is applicable).
        consensus : Optional[Union[str, float]]
            Average forecast among a representative group of economists.
        forecast : Optional[Union[str, float]]
            Trading Economics projections
        url : Optional[Union[str]]
            Trading Economics URL
        importance : Optional[Union[Literal[0, 1, 2, 3], str]]
            Importance of the event. 1-Low, 2-Medium, 3-High
        currency : Optional[Union[str]]
            Currency of the data.
        unit : Optional[Union[str]]
            Unit of the data.
        change : Optional[Union[float]]
            Value change since previous. (provider: fmp)
        change_percent : Optional[Union[float]]
            Percentage change since previous. (provider: fmp)
        updated_at : Optional[Union[datetime]]
            Last updated timestamp. (provider: fmp)
        created_at : Optional[Union[datetime]]
            Created at timestamp. (provider: fmp)
        description : Optional[Union[str]]
            Event description. (provider: nasdaq)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.calendar()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/calendar",
            **inputs,
        )

    @validate
    def const(
        self,
        index: typing_extensions.Annotated[
            Literal["nasdaq", "sp500", "dowjones"],
            OpenBBCustomParameter(
                description="Index for which we want to fetch the constituents."
            ),
        ] = "dowjones",
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Major Indices Constituents. Constituents of an index.

        Parameters
        ----------
        index : Literal['nasdaq', 'sp500', 'dowjones']
            Index for which we want to fetch the constituents.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[MajorIndicesConstituents]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MajorIndicesConstituents
        ------------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the constituent company in the index.
        sector : str
            Sector the constituent company in the index belongs to.
        sub_sector : Optional[Union[str]]
            Sub-sector the constituent company in the index belongs to.
        headquarter : Optional[Union[str]]
            Location of the headquarter of the constituent company in the index.
        date_first_added : Optional[Union[str, date]]
            Date the constituent company was added to the index.
        cik : int
            Central Index Key of the constituent company in the index.
        founded : Optional[Union[str, date]]
            Founding year of the constituent company in the index.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.const(index="dowjones")
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
            "/economy/const",
            **inputs,
        )

    @validate
    def cot(
        self,
        id: typing_extensions.Annotated[
            str,
            OpenBBCustomParameter(
                description="The series ID string for the report. Default report is Two-Year Treasury Note Futures."
            ),
        ] = "042601",
        provider: Union[Literal["nasdaq"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Commitment of Traders Reports. Lookup Commitment of Traders Reports by series ID.

        Parameters
        ----------
        id : str
            The series ID string for the report. Default report is Two-Year Treasury Note Futures.
        provider : Union[Literal['nasdaq'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'nasdaq' if there is
            no default.
        data_type : Optional[Union[Literal['F', 'FO', 'CITS']]]

                    The type of data to reuturn. Default is "FO".

                    F = Futures only

                    FO = Futures and Options

                    CITS = Commodity Index Trader Supplemental. Only valid for commodities.
                     (provider: nasdaq)
        legacy_format : Optional[Union[bool]]
            Returns the legacy format of report. Default is False. (provider: nasdaq)
        report_type : Optional[Union[Literal['ALL', 'CHG', 'OLD', 'OTR']]]

                    The type of report to return. Default is "ALL".

                    ALL = All

                    CHG = Change in Positions

                    OLD = Old Crop Years

                    OTR = Other Crop Years
                     (provider: nasdaq)
        measure : Optional[Union[Literal['CR', 'NT', 'OI', 'CHG']]]

                    The measure to return. Default is None.

                    CR = Concentration Ratios

                    NT = Number of Traders

                    OI = Percent of Open Interest

                    CHG = Change in Positions. Only valid when data_type is "CITS".
                     (provider: nasdaq)
        start_date : Optional[Union[datetime.date]]
            The start date of the time series. Defaults to all. (provider: nasdaq)
        end_date : Optional[Union[datetime.date]]
            The end date of the time series. Defaults to the most recent data. (provider: nasdaq)
        transform : Optional[Union[Literal['diff', 'rdiff', 'cumul', 'normalize']]]
            Transform the data as w/w difference, percent change, cumulative, or normalize. (provider: nasdaq)

        Returns
        -------
        OBBject
            results : Union[List[COT]]
                Serializable results.
            provider : Union[Literal['nasdaq'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        COT
        ---
        date : date
            The date of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.cot(id="042601")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "id": id,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/cot",
            **inputs,
        )

    @validate
    def cot_search(
        self,
        query: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Union[Literal["nasdaq"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Curated Commitment of Traders Reports.
            Fuzzy search and list of curated Commitment of Traders Reports series information.


        Parameters
        ----------
        query : str
            Search query.
        provider : Union[Literal['nasdaq'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'nasdaq' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[COTSearch]]
                Serializable results.
            provider : Union[Literal['nasdaq'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        COTSearch
        ---------
        code : str
            CFTC Code of the report.
        name : str
            Name of the underlying asset.
        category : Optional[Union[str]]
            Category of the underlying asset.
        subcategory : Optional[Union[str]]
            Subcategory of the underlying asset.
        units : Optional[Union[str]]
            The units for one contract.
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.cot_search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/cot_search",
            **inputs,
        )

    @validate
    def cpi(
        self,
        countries: typing_extensions.Annotated[
            List[
                Literal[
                    "australia",
                    "austria",
                    "belgium",
                    "brazil",
                    "bulgaria",
                    "canada",
                    "chile",
                    "china",
                    "croatia",
                    "cyprus",
                    "czech_republic",
                    "denmark",
                    "estonia",
                    "euro_area",
                    "finland",
                    "france",
                    "germany",
                    "greece",
                    "hungary",
                    "iceland",
                    "india",
                    "indonesia",
                    "ireland",
                    "israel",
                    "italy",
                    "japan",
                    "korea",
                    "latvia",
                    "lithuania",
                    "luxembourg",
                    "malta",
                    "mexico",
                    "netherlands",
                    "new_zealand",
                    "norway",
                    "poland",
                    "portugal",
                    "romania",
                    "russian_federation",
                    "slovak_republic",
                    "slovakia",
                    "slovenia",
                    "south_africa",
                    "spain",
                    "sweden",
                    "switzerland",
                    "turkey",
                    "united_kingdom",
                    "united_states",
                ]
            ],
            OpenBBCustomParameter(description="The country or countries to get data."),
        ],
        units: typing_extensions.Annotated[
            Literal["growth_previous", "growth_same", "index_2015"],
            OpenBBCustomParameter(
                description="The unit of measurement for the data.\n    Options:\n    - `growth_previous`: growth from the previous period\n    - `growth_same`: growth from the same period in the previous year\n    - `index_2015`: index with base year 2015."
            ),
        ] = "growth_same",
        frequency: typing_extensions.Annotated[
            Literal["monthly", "quarter", "annual"],
            OpenBBCustomParameter(
                description="The frequency of the data.\n    Options: `monthly`, `quarter`, and `annual`."
            ),
        ] = "monthly",
        harmonized: typing_extensions.Annotated[
            bool,
            OpenBBCustomParameter(
                description="Whether you wish to obtain harmonized data."
            ),
        ] = False,
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
        provider: Union[Literal["fred"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """CPI. Consumer Price Index.

        Parameters
        ----------
        countries : List[Literal['australia', 'austria', 'belgium', 'brazil', 'bulgar...
            The country or countries to get data.
        units : Literal['growth_previous', 'growth_same', 'index_2015']
            The unit of measurement for the data.
            Options:
            - `growth_previous`: growth from the previous period
            - `growth_same`: growth from the same period in the previous year
            - `index_2015`: index with base year 2015.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data.
            Options: `monthly`, `quarter`, and `annual`.
        harmonized : bool
            Whether you wish to obtain harmonized data.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fred'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[CPI]]
                Serializable results.
            provider : Union[Literal['fred'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CPI
        ---
        date : date
            The date of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.cpi(countries=['portugal', 'spain'], units="growth_same", frequency="monthly")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "countries": countries,
                "units": units,
                "frequency": frequency,
                "harmonized": harmonized,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/cpi",
            **inputs,
        )

    @validate
    def european_index(
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
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """European Index Historical. Historical close values for selected European indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['cboe'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        interval : Optional[Union[Literal['1d', '1m']]]
            Data granularity. (provider: cboe)

        Returns
        -------
        OBBject
            results : Union[List[EuropeanIndexHistorical]]
                Serializable results.
            provider : Union[Literal['cboe'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EuropeanIndexHistorical
        -----------------------
        date : datetime
            The date of the data.
        close : float
            The close price of the symbol.
        open : Optional[Union[float]]
            Opening price for the interval. Only valid when interval is 1m. (provider: cboe)
        high : Optional[Union[float]]
            High price for the interval. Only valid when interval is 1m. (provider: cboe)
        low : Optional[Union[float]]
            Low price for the interval. Only valid when interval is 1m. (provider: cboe)
        utc_datetime : Optional[Union[datetime]]
            UTC datetime. Only valid when interval is 1m. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.european_index(symbol="BUKBUS")
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
            "/economy/european_index",
            **inputs,
        )

    @validate
    def european_index_constituents(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get  current levels for constituents of select European indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['cboe'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[EuropeanIndexConstituents]]
                Serializable results.
            provider : Union[Literal['cboe'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EuropeanIndexConstituents
        -------------------------
        symbol : str
            Symbol representing the entity requested in the data. The symbol is the constituent company in the index.
        price : float
            Current price of the constituent company in the index.
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
        prev_close : Optional[Union[float]]
            Previous closing  price. (provider: cboe)
        change : Optional[Union[float]]
            Change in price. (provider: cboe)
        change_percent : Optional[Union[float]]
            Change in price as a percentage. (provider: cboe)
        tick : Optional[Union[str]]
            Whether the last sale was an up or down tick. (provider: cboe)
        last_trade_timestamp : Optional[Union[datetime]]
            Last trade timestamp for the symbol. (provider: cboe)
        exchange_id : Optional[Union[int]]
            The Exchange ID number. (provider: cboe)
        seqno : Optional[Union[int]]
            Sequence number of the last trade on the tape. (provider: cboe)
        asset_type : Optional[Union[str]]
            Type of asset. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.european_index_constituents(symbol="BUKBUS")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/european_index_constituents",
            **inputs,
        )

    @validate
    def fred_index(
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
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Union[Literal["intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Fred Historical. Historical close values for selected Fred indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        next_page : Optional[Union[str]]
            Token to get the next page of data from a previous API call. (provider: intrinio)
        all_pages : Optional[Union[bool]]
            Returns all pages of data from the API call at once. (provider: intrinio)

        Returns
        -------
        OBBject
            results : Union[List[FredHistorical]]
                Serializable results.
            provider : Union[Literal['intrinio'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FredHistorical
        --------------
        date : date
            The date of the data.
        value : Optional[Union[typing_extensions.Annotated[float, Gt(gt=0)]]]
            Value of the index.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.fred_index(symbol="SPX", limit=100)
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
            "/economy/fred_index",
            **inputs,
        )

    @validate
    def gdpforecast(
        self,
        period: typing_extensions.Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(
                description="Time period of the data to return. Units for nominal GDP period. Either quarter or annual."
            ),
        ] = "annual",
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
        type: typing_extensions.Annotated[
            Literal["nominal", "real"],
            OpenBBCustomParameter(
                description="Type of GDP to get forecast of.  Either nominal or real."
            ),
        ] = "real",
        provider: Union[Literal["oecd"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        period : Literal['quarter', 'annual']
            Time period of the data to return. Units for nominal GDP period. Either quarter or annual.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        type : Literal['nominal', 'real']
            Type of GDP to get forecast of.  Either nominal or real.
        provider : Union[Literal['oecd'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['argentina', 'asia', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_17', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'non-oecd', 'norway', 'oecd_total', 'peru', 'poland', 'portugal', 'romania', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states', 'world']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : Union[List[GDPForecast]]
                Serializable results.
            provider : Union[Literal['oecd'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPForecast
        -----------
        date : Optional[Union[date]]
            The date of the data.
        value : Optional[Union[float]]
            Nominal GDP value on the date.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.gdpforecast(period="annual", type="real")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "period": period,
                "start_date": start_date,
                "end_date": end_date,
                "type": type,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/gdpforecast",
            **inputs,
        )

    @validate
    def gdpnom(
        self,
        units: typing_extensions.Annotated[
            Literal["usd", "usd_cap"],
            OpenBBCustomParameter(
                description="The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita."
            ),
        ] = "usd",
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
        provider: Union[Literal["oecd"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        units : Literal['usd', 'usd_cap']
            The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['oecd'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['australia', 'austria', 'belgium', 'brazil', 'canada', 'chile', 'colombia', 'costa_rica', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'european_union', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : Union[List[GDPNom]]
                Serializable results.
            provider : Union[Literal['oecd'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPNom
        ------
        date : Optional[Union[date]]
            The date of the data.
        value : Optional[Union[float]]
            Nominal GDP value on the date.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.gdpnom(units="usd")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "units": units,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/gdpnom",
            **inputs,
        )

    @validate
    def gdpreal(
        self,
        units: typing_extensions.Annotated[
            Literal["idx", "qoq", "yoy"],
            OpenBBCustomParameter(
                description="The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)"
            ),
        ] = "yoy",
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
        provider: Union[Literal["oecd"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        units : Literal['idx', 'qoq', 'yoy']
            The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['oecd'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['G20', 'G7', 'argentina', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_19', 'europe', 'european_union_27', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'oecd_total', 'poland', 'portugal', 'romania', 'russia', 'saudi_arabia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : Union[List[GDPReal]]
                Serializable results.
            provider : Union[Literal['oecd'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPReal
        -------
        date : Optional[Union[date]]
            The date of the data.
        value : Optional[Union[float]]
            Nominal GDP value on the date.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.gdpreal(units="yoy")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "units": units,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/gdpreal",
            **inputs,
        )

    @validate
    def index(
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
        provider: Union[Literal["cboe", "fmp", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Major Indices Historical. Historical  levels for an index.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['cboe', 'fmp', 'polygon', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        interval : Optional[Union[Literal['1d', '1m'], Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
            Use interval, 1m, for intraday prices during the most recent trading period. (provider: cboe); Data granularity. (provider: fmp); Data granularity. (provider: yfinance)
        timeseries : Optional[Union[typing_extensions.Annotated[int, Ge(ge=0)]]]
            Number of days to look back. (provider: fmp)
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : int
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : int
            Multiplier of the timespan. (provider: polygon)
        period : Optional[Union[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]]
            Time period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        rounding : bool
            Round prices to two decimals? (provider: yfinance)

        Returns
        -------
        OBBject
            results : Union[List[MajorIndicesHistorical]]
                Serializable results.
            provider : Union[Literal['cboe', 'fmp', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MajorIndicesHistorical
        ----------------------
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
        volume : Optional[Union[typing_extensions.Annotated[int, Strict(strict=True)]]]
            The volume of the symbol.
        calls_volume : Optional[Union[float]]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[Union[float]]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[Union[float]]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        adj_close : Optional[Union[float]]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[Union[float]]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[Union[float]]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[Union[float]]
            Change % in the price of the symbol. (provider: fmp)
        label : Optional[Union[str]]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[Union[float]]
            Change % in the price of the symbol over a period of time. (provider: fmp)
        transactions : Optional[Union[typing_extensions.Annotated[int, Gt(gt=0)]]]
            Number of transactions for the symbol in the time period. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.index(symbol="SPX")
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
            "/economy/index",
            **inputs,
        )

    @validate
    def index_search(
        self,
        query: typing_extensions.Annotated[
            str, OpenBBCustomParameter(description="Search query.")
        ] = "",
        is_symbol: typing_extensions.Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Index Search. Search for indices.

        Parameters
        ----------
        query : str
            Search query.
        is_symbol : bool
            Whether to search by ticker symbol.
        provider : Union[Literal['cboe'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        europe : bool
            Filter for European indices. False for US indices. (provider: cboe)

        Returns
        -------
        OBBject
            results : Union[List[IndexSearch]]
                Serializable results.
            provider : Union[Literal['cboe'], None]
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
        isin : Optional[Union[str]]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        region : Optional[Union[str]]
            Region for the index. Valid only for European indices (provider: cboe)
        description : Optional[Union[str]]
            Description for the index. (provider: cboe)
        data_delay : Optional[Union[int]]
            Data delay for the index. Valid only for US indices. (provider: cboe)
        currency : Optional[Union[str]]
            Currency for the index. (provider: cboe)
        time_zone : Optional[Union[str]]
            Time zone for the index. Valid only for US indices. (provider: cboe)
        open_time : Optional[Union[datetime.time]]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[Union[datetime.time]]
            Closing time for the index. Valid only for US indices. (provider: cboe)
        tick_days : Optional[Union[str]]
            The trading days for the index. Valid only for US indices. (provider: cboe)
        tick_frequency : Optional[Union[str]]
            Tick frequency for the index. Valid only for US indices. (provider: cboe)
        tick_period : Optional[Union[str]]
            Tick period for the index. Valid only for US indices. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.index_search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "is_symbol": is_symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/index_search",
            **inputs,
        )

    @validate
    def index_snapshots(
        self,
        region: typing_extensions.Annotated[
            Union[Literal["US", "EU"], None],
            OpenBBCustomParameter(
                description="The region to return. Currently supports US and EU."
            ),
        ] = "US",
        provider: Union[Literal["cboe"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Index Snapshots. Current levels for all indices from a provider.

        Parameters
        ----------
        region : Union[Literal['US', 'EU'], None]
            The region to return. Currently supports US and EU.
        provider : Union[Literal['cboe'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[IndexSnapshots]]
                Serializable results.
            provider : Union[Literal['cboe'], None]
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
        name : Optional[Union[str]]
            Name of the index.
        currency : Optional[Union[str]]
            Currency of the index.
        price : Optional[Union[float]]
            Current price of the index.
        open : Optional[Union[float]]
            The open price of the symbol.
        high : Optional[Union[float]]
            The high price of the symbol.
        low : Optional[Union[float]]
            The low price of the symbol.
        close : Optional[Union[float]]
            The close price of the symbol.
        prev_close : Optional[Union[float]]
            Previous closing price of the index.
        change : Optional[Union[float]]
            Change of the index.
        change_percent : Optional[Union[float]]
            Change percent of the index.
        isin : Optional[Union[str]]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        last_trade_timestamp : Optional[Union[datetime]]
            Last trade timestamp for the index. (provider: cboe)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.index_snapshots(region="US")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "region": region,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/index_snapshots",
            **inputs,
        )

    @validate
    def risk(
        self, provider: Union[Literal["fmp"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Market Risk Premium. Historical market risk premium.

        Parameters
        ----------
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[RiskPremium]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        RiskPremium
        -----------
        country : str
            Market country.
        continent : Optional[Union[str]]
            Continent of the country.
        total_equity_risk_premium : Optional[Union[typing_extensions.Annotated[float, Gt(gt=0)]]]
            Total equity risk premium for the country.
        country_risk_premium : Optional[Union[typing_extensions.Annotated[float, Ge(ge=0)]]]
            Country-specific risk premium.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.risk()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/economy/risk",
            **inputs,
        )

    @validate
    def sp500_multiples(
        self,
        series_name: typing_extensions.Annotated[
            Literal[
                "Shiller PE Ratio by Month",
                "Shiller PE Ratio by Year",
                "PE Ratio by Year",
                "PE Ratio by Month",
                "Dividend by Year",
                "Dividend by Month",
                "Dividend Growth by Quarter",
                "Dividend Growth by Year",
                "Dividend Yield by Year",
                "Dividend Yield by Month",
                "Earnings by Year",
                "Earnings by Month",
                "Earnings Growth by Year",
                "Earnings Growth by Quarter",
                "Real Earnings Growth by Year",
                "Real Earnings Growth by Quarter",
                "Earnings Yield by Year",
                "Earnings Yield by Month",
                "Real Price by Year",
                "Real Price by Month",
                "Inflation Adjusted Price by Year",
                "Inflation Adjusted Price by Month",
                "Sales by Year",
                "Sales by Quarter",
                "Sales Growth by Year",
                "Sales Growth by Quarter",
                "Real Sales by Year",
                "Real Sales by Quarter",
                "Real Sales Growth by Year",
                "Real Sales Growth by Quarter",
                "Price to Sales Ratio by Year",
                "Price to Sales Ratio by Quarter",
                "Price to Book Value Ratio by Year",
                "Price to Book Value Ratio by Quarter",
                "Book Value per Share by Year",
                "Book Value per Share by Quarter",
            ],
            OpenBBCustomParameter(
                description="The name of the series. Defaults to 'PE Ratio by Month'."
            ),
        ] = "PE Ratio by Month",
        start_date: typing_extensions.Annotated[
            Union[str, None],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = "",
        end_date: typing_extensions.Annotated[
            Union[str, None],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = "",
        provider: Union[Literal["nasdaq"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios.

        Parameters
        ----------
        series_name : Literal['Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Rat...
            The name of the series. Defaults to 'PE Ratio by Month'.
        start_date : Union[str, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[str, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['nasdaq'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'nasdaq' if there is
            no default.
        collapse : Optional[Union[Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual']]]
            Collapse the frequency of the time series. (provider: nasdaq)
        transform : Optional[Union[Literal['diff', 'rdiff', 'cumul', 'normalize']]]
            The transformation of the time series. (provider: nasdaq)

        Returns
        -------
        OBBject
            results : Union[List[SP500Multiples]]
                Serializable results.
            provider : Union[Literal['nasdaq'], None]
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
        >>> obb.economy.sp500_multiples(series_name="PE Ratio by Month")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "series_name": series_name,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/sp500_multiples",
            **inputs,
        )
