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


class ROUTER_economy(Container):
    """/economy
    available_indices
    const
    cot
    cot_search
    cpi
    econcal
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
        self, provider: Optional[Literal["cboe", "fmp", "yfinance"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Available Indices. Available indices for a given provider.

        Parameters
        ----------
        provider : Optional[Literal['cboe', 'fmp', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        europe : bool
            Filter for European indices. False for US indices. (provider: cboe)

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
        isin : Optional[str]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        region : Optional[str]
            Region for the index. Valid only for European indices (provider: cboe)
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
            ID code for keying the index in the OpenBB Terminal. (provider: yfinance)"""  # noqa: E501

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
    def const(
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
        """Major Indices Constituents. Constituents of an index.

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
            results : List[MajorIndicesConstituents]
                Serializable results.
            provider : Optional[Literal['fmp']]
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
            Symbol to get data for.
        name : str
            Name of the constituent company in the index.
        sector : str
            Sector the constituent company in the index belongs to.
        sub_sector : Optional[str]
            Sub-sector the constituent company in the index belongs to.
        headquarter : Optional[str]
            Location of the headquarter of the constituent company in the index.
        date_first_added : Optional[Union[date, str]]
            Date the constituent company was added to the index.
        cik : int
            Central Index Key of the constituent company in the index.
        founded : Optional[Union[date, str]]
            Founding year of the constituent company in the index."""  # noqa: E501

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
        self, provider: Optional[Literal["quandl"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Commitment of Traders Reports. Lookup Commitment of Traders Reports by series ID.

        Parameters
        ----------
        provider : Optional[Literal['quandl']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'quandl' if there is
            no default.
        code : str

                    CFTC series code.  Use search_cot() to find the code.
                    Codes not listed in the curated list, but are published by on the Nasdaq Data Link website, are valid.
                    Certain symbols, such as "ES=F", or exact names are also valid.
                    Default report is: S&P 500 Consolidated (CME))
                     (provider: quandl)
        data_type : Optional[Literal['F', 'FO', 'CITS']]

                    The type of data to reuturn. Default is "FO".

                    F = Futures only

                    FO = Futures and Options

                    CITS = Commodity Index Trader Supplemental. Only valid for commodities.
                 (provider: quandl)
        legacy_format : Optional[bool]
            Returns the legacy format of report. Default is False. (provider: quandl)
        report_type : Optional[Literal['ALL', 'CHG', 'OLD', 'OTR']]

                    The type of report to return. Default is "ALL".

                        ALL = All

                        CHG = Change in Positions

                        OLD = Old Crop Years

                        OTR = Other Crop Years
                 (provider: quandl)
        measure : Optional[Literal['CR', 'NT', 'OI', 'CHG']]

                    The measure to return. Default is None.

                    CR = Concentration Ratios

                    NT = Number of Traders

                    OI = Percent of Open Interest

                    CHG = Change in Positions. Only valid when data_type is "CITS".
                 (provider: quandl)
        start_date : Optional[datetime.date]
            The start date of the time series. Defaults to all. (provider: quandl)
        end_date : Optional[datetime.date]
            The end date of the time series. Defaults to the most recent data. (provider: quandl)
        transform : Optional[Literal['diff', 'rdiff', 'cumul', 'normalize']]
            Transform the data as w/w difference, percent change, cumulative, or normalize. (provider: quandl)

        Returns
        -------
        OBBject
            results : List[COT]
                Serializable results.
            provider : Optional[Literal['quandl']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        COT
        ---"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/economy/cot",
            **inputs,
        )

    @validate
    def cot_search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        provider: Optional[Literal["quandl"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """
            Curated Commitment of Traders Reports.
            Fuzzy search and list of curated Commitment of Traders Reports series information.


        Parameters
        ----------
        query : str
            Search query.
        provider : Optional[Literal['quandl']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'quandl' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[COTSearch]
                Serializable results.
            provider : Optional[Literal['quandl']]
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
        category : Optional[str]
            Category of the underlying asset.
        subcategory : Optional[str]
            Subcategory of the underlying asset.
        units : Optional[str]
            The units for one contract.
        symbol : Optional[str]
            Trading symbol representing the underlying asset."""  # noqa: E501

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
        countries: Annotated[
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
        units: Annotated[
            Literal["growth_previous", "growth_same", "index_2015"],
            OpenBBCustomParameter(description="The data units."),
        ] = "growth_same",
        frequency: Annotated[
            Literal["monthly", "quarter", "annual"],
            OpenBBCustomParameter(description="The data time frequency."),
        ] = "monthly",
        harmonized: Annotated[
            bool,
            OpenBBCustomParameter(
                description="Whether you wish to obtain harmonized data."
            ),
        ] = False,
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
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """CPI. Consumer Price Index.

        Parameters
        ----------
        countries : List[Literal['australia', 'austria', 'belgium', 'brazil', 'bulgar...
            The country or countries to get data.
        units : Literal['growth_previous', 'growth_same', 'index_2015']
            The data units.
        frequency : Literal['monthly', 'quarter', 'annual']
            The data time frequency.
        harmonized : bool
            Whether you wish to obtain harmonized data.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[CPI]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CPI
        ---
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            CPI value on the date."""  # noqa: E501

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
    def econcal(
        self,
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
        importance: Annotated[
            Literal["Low", "Medium", "High"],
            OpenBBCustomParameter(description="Importance of the event."),
        ] = None,
        group: Annotated[
            Literal[
                "interest rate",
                "inflation",
                "bonds",
                "consumer",
                "gdp",
                "government",
                "housing",
                "labour",
                "markets",
                "money",
                "prices",
                "trade",
                "business",
            ],
            OpenBBCustomParameter(description="Grouping of events"),
        ] = None,
        country: Annotated[
            Union[List[str], str, None],
            OpenBBCustomParameter(description="Country of the event"),
        ] = None,
        provider: Optional[Literal["tradingeconomics"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        importance : Literal['Low', 'Medium', 'High']
            Importance of the event.
        group : Literal['interest rate', 'inflation', 'bonds', 'consumer', 'gdp', 'gover...
            Grouping of events
        country : Union[List[str], str, None]
            Country of the event
        provider : Optional[Literal['tradingeconomics']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'tradingeconomics' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EconomicCalendar]
                Serializable results.
            provider : Optional[Literal['tradingeconomics']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EconomicCalendar
        ----------------
        date : Optional[datetime]
            Date and time of event.
        country : Optional[str]
            Country of event.
        category : Optional[str]
            Category of event.
        event : Optional[str]
            Event name.
        reference : Optional[str]
            Abbreviated period for which released data refers to.
        source : Optional[str]
            Source of the data.
        sourceurl : Optional[str]
            Source URL.
        actual : Optional[str]
            Latest released value.
        previous : Optional[str]
            Value for the previous period after the revision (if revision is applicable).
        consensus : Optional[str]
            Average forecast among a representative group of economists.
        forecast : Optional[str]
            Trading Economics projections
        url : Optional[str]
            Trading Economics URL
        importance : Optional[Literal[0, 1, 2, 3]]
            Importance of the event. 1-Low, 2-Medium, 3-High
        currency : Optional[str]
            Currency of the data.
        unit : Optional[str]
            Unit of the data."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
                "importance": importance,
                "group": group,
                "country": country,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/econcal",
            **inputs,
        )

    @validate
    def european_index(
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
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """European Index Historical. Historical close values for selected European indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        interval : Optional[Literal['1d', '1m']]
            Data granularity. (provider: cboe)

        Returns
        -------
        OBBject
            results : List[EuropeanIndexHistorical]
                Serializable results.
            provider : Optional[Literal['cboe']]
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
        open : Optional[float]
            Opening price for the interval. Only valid when interval is 1m. (provider: cboe)
        high : Optional[float]
            High price for the interval. Only valid when interval is 1m. (provider: cboe)
        low : Optional[float]
            Low price for the interval. Only valid when interval is 1m. (provider: cboe)
        utc_datetime : Optional[datetime]
            UTC datetime. Only valid when interval is 1m. (provider: cboe)"""  # noqa: E501

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
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get  current levels for constituents of select European indices.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EuropeanIndexConstituents]
                Serializable results.
            provider : Optional[Literal['cboe']]
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
            Symbol of the constituent company in the index.
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
        prev_close : Optional[float]
            Previous closing  price. (provider: cboe)
        change : Optional[float]
            Change in price. (provider: cboe)
        change_percent : Optional[float]
            Change in price as a percentage. (provider: cboe)
        tick : Optional[str]
            Whether the last sale was an up or down tick. (provider: cboe)
        last_trade_timestamp : Optional[datetime]
            Last trade timestamp for the symbol. (provider: cboe)
        exchange_id : Optional[int]
            The Exchange ID number. (provider: cboe)
        seqno : Optional[int]
            Sequence number of the last trade on the tape. (provider: cboe)
        asset_type : Optional[str]
            Type of asset. (provider: cboe)"""  # noqa: E501

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
        """Fred Historical. Historical close values for selected Fred indices.

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

        Returns
        -------
        OBBject
            results : List[FredHistorical]
                Serializable results.
            provider : Optional[Literal['intrinio']]
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
        value : Optional[Annotated[float, Gt(gt=0)]]
            Value of the index."""  # noqa: E501

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
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(
                description="Units for nominal GDP period.  Either quarter or annual."
            ),
        ] = "annual",
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
        type: Annotated[
            Literal["nominal", "real"],
            OpenBBCustomParameter(
                description="Type of GDP to get forecast of.  Either nominal or real."
            ),
        ] = "real",
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        period : Literal['quarter', 'annual']
            Units for nominal GDP period.  Either quarter or annual.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        type : Literal['nominal', 'real']
            Type of GDP to get forecast of.  Either nominal or real.
        provider : Optional[Literal['oecd']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['argentina', 'asia', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_17', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'non-oecd', 'norway', 'oecd_total', 'peru', 'poland', 'portugal', 'romania', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states', 'world']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GDPForecast]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPForecast
        -----------
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            Nominal GDP value on the date."""  # noqa: E501

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
        units: Annotated[
            Literal["usd", "usd_cap"],
            OpenBBCustomParameter(
                description="Units to get nominal GDP in.  Either usd or usd_cap indicating per capita."
            ),
        ] = "usd",
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        units : Literal['usd', 'usd_cap']
            Units to get nominal GDP in.  Either usd or usd_cap indicating per capita.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['australia', 'austria', 'belgium', 'brazil', 'canada', 'chile', 'colombia', 'costa_rica', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'european_union', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GDPNom]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPNom
        ------
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            Nominal GDP value on the date."""  # noqa: E501

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
        units: Annotated[
            Literal["idx", "qoq", "yoy"],
            OpenBBCustomParameter(
                description="Units to get real GDP in. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)"
            ),
        ] = "yoy",
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """GDP Data.

        Parameters
        ----------
        units : Literal['idx', 'qoq', 'yoy']
            Units to get real GDP in. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['G20', 'G7', 'argentina', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_19', 'europe', 'european_union_27', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'oecd_total', 'poland', 'portugal', 'romania', 'russia', 'saudi_arabia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GDPReal]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GDPReal
        -------
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            Nominal GDP value on the date."""  # noqa: E501

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
        provider: Optional[Literal["cboe", "fmp", "polygon", "yfinance"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Major Indices Historical. Historical  levels for an index.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['cboe', 'fmp', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        interval : Optional[Union[Literal['1d', '1m'], Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']]]
            Use interval, 1m, for intraday prices during the most recent trading period. (provider: cboe); Data granularity. (provider: fmp); Data granularity. (provider: yfinance)
        timeseries : Optional[Annotated[int, Ge(ge=0)]]
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
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Time period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        rounding : bool
            Round prices to two decimals? (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[MajorIndicesHistorical]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'polygon', 'yfinance']]
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
        volume : Optional[Annotated[int, Strict(strict=True)]]
            The volume of the symbol.
        calls_volume : Optional[float]
            Number of calls traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        puts_volume : Optional[float]
            Number of puts traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
        total_options_volume : Optional[float]
            Total number of options traded during the most recent trading period. Only valid if interval is 1m. (provider: cboe)
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
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        symbol: Annotated[
            Union[bool, List[str]],
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Index Search. Search for indices.

        Parameters
        ----------
        query : str
            Search query.
        symbol : bool
            Whether to search by ticker symbol.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        europe : bool
            Filter for European indices. False for US indices. (provider: cboe)

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
            Symbol of the index.
        name : str
            Name of the index.
        isin : Optional[str]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        region : Optional[str]
            Region for the index. Valid only for European indices (provider: cboe)
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
            Tick period for the index. Valid only for US indices. (provider: cboe)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
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
        region: Annotated[
            Optional[Literal["US", "EU"]],
            OpenBBCustomParameter(
                description="The region to return. Currently supports US and EU."
            ),
        ] = "US",
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Index Snapshots. Current levels for all indices from a provider.

        Parameters
        ----------
        region : Optional[Literal['US', 'EU']]
            The region to return. Currently supports US and EU.
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
            Symbol of the index.
        name : Optional[str]
            Name of the index.
        currency : Optional[str]
            Currency of the index.
        price : Optional[float]
            Current price of the index.
        open : Optional[float]
            Opening price of the index.
        high : Optional[float]
            Highest price of the index.
        low : Optional[float]
            Lowest price of the index.
        close : Optional[float]
            Closing price of the index.
        prev_close : Optional[float]
            Previous closing price of the index.
        change : Optional[float]
            Change of the index.
        change_percent : Optional[float]
            Change percent of the index.
        isin : Optional[str]
            ISIN code for the index. Valid only for European indices. (provider: cboe)
        last_trade_timestamp : Optional[datetime]
            Last trade timestamp for the index. (provider: cboe)"""  # noqa: E501

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
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Market Risk Premium. Historical market risk premium.

        Parameters
        ----------
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[RiskPremium]
                Serializable results.
            provider : Optional[Literal['fmp']]
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
        continent : Optional[str]
            Continent of the country.
        total_equity_risk_premium : Optional[Annotated[float, Gt(gt=0)]]
            Total equity risk premium for the country.
        country_risk_premium : Optional[Annotated[float, Ge(ge=0)]]
            Country-specific risk premium."""  # noqa: E501

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
        series_name: Annotated[
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
        start_date: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="The start date of the time series. Format: YYYY-MM-DD"
            ),
        ] = "",
        end_date: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="The end date of the time series. Format: YYYY-MM-DD"
            ),
        ] = "",
        collapse: Annotated[
            Optional[Literal["daily", "weekly", "monthly", "quarterly", "annual"]],
            OpenBBCustomParameter(
                description="Collapse the frequency of the time series."
            ),
        ] = "monthly",
        transform: Annotated[
            Optional[Literal["diff", "rdiff", "cumul", "normalize"]],
            OpenBBCustomParameter(description="The transformation of the time series."),
        ] = None,
        provider: Optional[Literal["quandl"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """S&P 500 Multiples. Historical S&P 500 multiples and Shiller PE ratios.

        Parameters
        ----------
        series_name : Literal['Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Rat...
            The name of the series. Defaults to 'PE Ratio by Month'.
        start_date : Optional[str]
            The start date of the time series. Format: YYYY-MM-DD
        end_date : Optional[str]
            The end date of the time series. Format: YYYY-MM-DD
        collapse : Optional[Literal['daily', 'weekly', 'monthly', 'quarterly', 'annu...
            Collapse the frequency of the time series.
        transform : Optional[Literal['diff', 'rdiff', 'cumul', 'normalize']]
            The transformation of the time series.
        provider : Optional[Literal['quandl']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'quandl' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SP500Multiples]
                Serializable results.
            provider : Optional[Literal['quandl']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SP500Multiples
        --------------
        date : str
            The date data for the time series.
        value : float
            The data value for the time series."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "series_name": series_name,
                "start_date": start_date,
                "end_date": end_date,
                "collapse": collapse,
                "transform": transform,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/economy/sp500_multiples",
            **inputs,
        )
