### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import BaseModel, validate_arguments
from typing_extensions import Annotated


class CLASS_economy(Container):
    """/economy
    available_indices
    balance
    bigmac
    const
    corecpi
    cot
    cot_search
    country_codes
    cpi
    cpi_options
    currencies
    debt
    european_index
    european_index_constituents
    events
    fgdp
    fred
    fred_search
    futures
    gdp
    glbonds
    index
    indices
    macro
    macro_countries
    macro_parameters
    overview
    perfmap
    performance
    revenue
    rgdp
    risk
    rtps
    search_index
    sp500_multiples
    spending
    trust
    usbonds
    valuation
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def available_indices(
        self,
        chart: bool = False,
        provider: Optional[Literal["cboe", "fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """AVAILABLE_INDICES.

        Parameters
        ----------
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['cboe', 'fmp']]
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
            provider : Optional[Literal['cboe', 'fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

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
            Symbol for the index. (provider: cboe)
        description : Optional[str]
            Description for the index. Valid only for US indices. (provider: cboe)
        data_delay : Optional[int]
            Data delay for the index. Valid only for US indices. (provider: cboe)
        open_time : Optional[time]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[time]
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
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/available_indices",
            **inputs,
        )

    @validate_arguments
    def balance(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """BALANCE."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/balance",
            **inputs,
        )

    @validate_arguments
    def bigmac(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """BIGMAC."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/bigmac",
            **inputs,
        )

    @validate_arguments
    def const(
        self,
        index: Annotated[
            Literal["nasdaq", "sp500", "dowjones"],
            OpenBBCustomParameter(
                description="Index for which we want to fetch the constituents."
            ),
        ] = "dowjones",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get the constituents of an index.

        Parameters
        ----------
        index : Literal['nasdaq', 'sp500', 'dowjones']
            Index for which we want to fetch the constituents.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        MajorIndicesConstituents
        ------------------------
        symbol : Optional[str]
            Symbol to get data for.
        name : Optional[str]
            Name of the constituent company in the index.
        sector : Optional[str]
            Sector the constituent company in the index belongs to.
        sub_sector : Optional[str]
            Sub-sector the constituent company in the index belongs to.
        headquarter : Optional[str]
            Location of the headquarter of the constituent company in the index.
        date_first_added : Union[date, str, NoneType]
            Date the constituent company was added to the index.
        cik : Optional[int]
            Central Index Key of the constituent company in the index.
        founded : Union[date, str]
            Founding year of the constituent company in the index."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "index": index,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/const",
            **inputs,
        )

    @validate_arguments
    def corecpi(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """CORECPI."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/corecpi",
            **inputs,
        )

    @validate_arguments
    def cot(
        self,
        chart: bool = False,
        provider: Optional[Literal["quandl"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get  CFTC Commitment of Traders Reports.  Data is released every Friday.

        Parameters
        ----------
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        COT
        ---"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/cot",
            **inputs,
        )

    @validate_arguments
    def cot_search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        chart: bool = False,
        provider: Optional[Literal["quandl"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Search within a curated list of CFTC Commitment of Traders Reports.

        Parameters
        ----------
        query : str
            Search query.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        COTSearch
        ---------
        code : Optional[str]
            CFTC Code of the report.
        name : Optional[str]
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
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/cot_search",
            **inputs,
        )

    @validate_arguments
    def country_codes(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """COUNTRY_CODES."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/country_codes",
            **inputs,
        )

    @validate_arguments
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
        chart: bool = False,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """CPI.

        Parameters
        ----------
        countries : List[Literal['australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'croatia', 'cyprus', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'malta', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'romania', 'russian_federation', 'slovak_republic', 'slovakia', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']]
            The country or countries to get data.
        units : Literal['growth_previous', 'growth_same', 'index_2015']
            The data units.
        frequency : Literal['monthly', 'quarter', 'annual']
            The data time frequency.
        harmonized : bool
            Whether you wish to obtain harmonized data.
        start_date : Union[datetime.date, NoneType, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, NoneType, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        CPI
        ---
        date : Optional[date]
            The date of the data.
        realtime_start : Optional[date]
            Date the data was updated.
        realtime_end : Optional[date]
            Date the data was updated.
        value : Optional[float]
            Value of the data."""  # noqa: E501

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
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/cpi",
            **inputs,
        )

    @validate_arguments
    def cpi_options(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Get the options for v3 cpi(options=True)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/cpi_options",
            **inputs,
        )

    @validate_arguments
    def currencies(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """CURRENCIES."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/currencies",
            **inputs,
        )

    @validate_arguments
    def debt(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """DEBT."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/debt",
            **inputs,
        )

    @validate_arguments
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
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get historical closine values for an index.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, NoneType, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, NoneType, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['cboe']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EuropeanIndicesEOD]
                Serializable results.
            provider : Optional[Literal['cboe']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        EuropeanIndicesEOD
        ------------------
        date : Optional[date]
            The date of the data.
        close : Optional[float]
            The close price of the symbol."""  # noqa: E501

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
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/european_index",
            **inputs,
        )

    @validate_arguments
    def european_index_constituents(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol of the constituent company in the index."
            ),
        ],
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get historical closine values for an index.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol of the constituent company in the index.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        EuropeanIndexConstituents
        -------------------------
        symbol : Optional[str]
            Symbol of the constituent company in the index.
        price : Optional[float]
            Current price of the constituent company in the index.
        open : Optional[float]
            The open price of the symbol.
        high : Optional[float]
            The high price of the symbol.
        low : Optional[float]
            The low price of the symbol.
        close : Optional[float]
            The close price of the symbol.
        volume : Optional[float]
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
        type : Optional[str]
            Type of asset. (provider: cboe)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/european_index_constituents",
            **inputs,
        )

    @validate_arguments
    def events(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """EVENTS."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/events",
            **inputs,
        )

    @validate_arguments
    def fgdp(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """FGDP."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/fgdp",
            **inputs,
        )

    @validate_arguments
    def fred(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """FRED."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/fred",
            **inputs,
        )

    @validate_arguments
    def fred_search(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """FRED Search (was fred_notes)."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/fred_search",
            **inputs,
        )

    @validate_arguments
    def futures(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """FUTURES. 2 sources"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/futures",
            **inputs,
        )

    @validate_arguments
    def gdp(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """GDP."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/gdp",
            **inputs,
        )

    @validate_arguments
    def glbonds(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """GLBONDS."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/glbonds",
            **inputs,
        )

    @validate_arguments
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
        chart: bool = False,
        provider: Optional[Literal["cboe", "fmp", "polygon", "yfinance"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get OHLCV data for an index.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        start_date : Union[datetime.date, NoneType, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, NoneType, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['cboe', 'fmp', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'cboe' if there is
            no default.
        timeseries : Optional[pydantic.types.NonNegativeInt]
            Number of days to look back. (provider: fmp)
        interval : Union[Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day'], Literal['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], NoneType]
            None
        timespan : Literal['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
            Timespan of the data. (provider: polygon)
        sort : Literal['asc', 'desc']
            Sort order of the data. (provider: polygon)
        limit : PositiveInt
            The number of data entries to return. (provider: polygon)
        adjusted : bool
            Whether the data is adjusted. (provider: polygon)
        multiplier : PositiveInt
            Multiplier of the timespan. (provider: polygon)
        period : Optional[Literal['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']]
            Period of the data to return. (provider: yfinance)
        prepost : bool
            Include Pre and Post market data. (provider: yfinance)
        adjust : bool
            Adjust all the data automatically. (provider: yfinance)
        back_adjust : bool
            Back-adjusted data to mimic true historical prices. (provider: yfinance)

        Returns
        -------
        OBBject
            results : List[MajorIndicesEOD]
                Serializable results.
            provider : Optional[Literal['cboe', 'fmp', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        MajorIndicesEOD
        ---------------
        date : Union[datetime, date]
            The date of the data.
        open : Optional[PositiveFloat]
            The open price of the symbol.
        high : Optional[PositiveFloat]
            The high price of the symbol.
        low : Optional[PositiveFloat]
            The low price of the symbol.
        close : Optional[PositiveFloat]
            The close price of the symbol.
        volume : Optional[float]
            The volume of the symbol.
        adj_close : Optional[float]
            Adjusted Close Price of the symbol. (provider: fmp)
        unadjusted_volume : Optional[float]
            Unadjusted volume of the symbol. (provider: fmp)
        change : Optional[float]
            Change in the price of the symbol from the previous day. (provider: fmp)
        change_percent : Optional[float]
            Change \\% in the price of the symbol. (provider: fmp)
        label : Optional[str]
            Human readable format of the date. (provider: fmp)
        change_over_time : Optional[float]
            Change \\% in the price of the symbol over a period of time. (provider: fmp)
        vwap : Optional[float]
            Volume Weighted Average Price of the symbol. (provider: fmp)
        n : Optional[PositiveInt]
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
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/index",
            **inputs,
        )

    @validate_arguments
    def indices(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """INDICES."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/indices",
            **inputs,
        )

    @validate_arguments
    def macro(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Query EconDB for macro data."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/macro",
            **inputs,
        )

    @validate_arguments
    def macro_countries(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """MACRO_COUNTRIES."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/macro_countries",
            **inputs,
        )

    @validate_arguments
    def macro_parameters(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """MACRO_PARAMETERS."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/macro_parameters",
            **inputs,
        )

    @validate_arguments
    def overview(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """OVERVIEW."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/overview",
            **inputs,
        )

    @validate_arguments
    def perfmap(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """PERFMAP."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/perfmap",
            **inputs,
        )

    @validate_arguments
    def performance(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """PERFORMANCE."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/performance",
            **inputs,
        )

    @validate_arguments
    def revenue(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """REVENUE."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/revenue",
            **inputs,
        )

    @validate_arguments
    def rgdp(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """RGDP."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/rgdp",
            **inputs,
        )

    @validate_arguments
    def risk(
        self, chart: bool = False, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List]:
        """Market Risk Premium.

        Parameters
        ----------
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        RiskPremium
        -----------
        country : Optional[str]
            Market country.
        continent : Optional[str]
            Continent of the country.
        total_equity_risk_premium : Optional[PositiveFloat]
            Total equity risk premium for the country.
        country_risk_premium : Optional[NonNegativeFloat]
            Country-specific risk premium."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/risk",
            **inputs,
        )

    @validate_arguments
    def rtps(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """RTPS."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/rtps",
            **inputs,
        )

    @validate_arguments
    def search_index(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        ticker: Annotated[
            bool,
            OpenBBCustomParameter(description="Whether to search by ticker symbol."),
        ] = False,
        chart: bool = False,
        provider: Optional[Literal["cboe"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Search Available Indices.

        Parameters
        ----------
        query : str
            Search query.
        ticker : bool
            Whether to search by ticker symbol.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        IndexSearch
        -----------
        symbol : Optional[str]
            Symbol of the index.
        name : Optional[str]
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
        open_time : Optional[time]
            Opening time for the index. Valid only for US indices. (provider: cboe)
        close_time : Optional[time]
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
                "ticker": ticker,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/search_index",
            **inputs,
        )

    @validate_arguments
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
        chart: bool = False,
        provider: Optional[Literal["quandl"]] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Get historical values, multiples, and ratios for the S&P 500.

        Parameters
        ----------
        series_name : Literal['Shiller PE Ratio by Month', 'Shiller PE Ratio by Year', 'PE Ratio by Year', 'PE Ratio by Month', 'Dividend by Year', 'Dividend by Month', 'Dividend Growth by Quarter', 'Dividend Growth by Year', 'Dividend Yield by Year', 'Dividend Yield by Month', 'Earnings by Year', 'Earnings by Month', 'Earnings Growth by Year', 'Earnings Growth by Quarter', 'Real Earnings Growth by Year', 'Real Earnings Growth by Quarter', 'Earnings Yield by Year', 'Earnings Yield by Month', 'Real Price by Year', 'Real Price by Month', 'Inflation Adjusted Price by Year', 'Inflation Adjusted Price by Month', 'Sales by Year', 'Sales by Quarter', 'Sales Growth by Year', 'Sales Growth by Quarter', 'Real Sales by Year', 'Real Sales by Quarter', 'Real Sales Growth by Year', 'Real Sales Growth by Quarter', 'Price to Sales Ratio by Year', 'Price to Sales Ratio by Quarter', 'Price to Book Value Ratio by Year', 'Price to Book Value Ratio by Quarter', 'Book Value per Share by Year', 'Book Value per Share by Quarter']
            The name of the series. Defaults to 'PE Ratio by Month'.
        start_date : Optional[str]
            The start date of the time series. Format: YYYY-MM-DD
        end_date : Optional[str]
            The end date of the time series. Format: YYYY-MM-DD
        collapse : Optional[Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual']]
            Collapse the frequency of the time series.
        transform : Optional[Literal['diff', 'rdiff', 'cumul', 'normalize']]
            The transformation of the time series.
        chart : bool
            Whether to create a chart or not, by default False.
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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        SP500Multiples
        --------------
        date : Optional[str]
            The date data for the time series.
        value : Optional[float]
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
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/sp500_multiples",
            **inputs,
        )

    @validate_arguments
    def spending(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """SPENDING."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/spending",
            **inputs,
        )

    @validate_arguments
    def trust(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """TRUST."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/trust",
            **inputs,
        )

    @validate_arguments
    def usbonds(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """USBONDS."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/usbonds",
            **inputs,
        )

    @validate_arguments
    def valuation(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga",
                "cboe",
                "fmp",
                "fred",
                "intrinio",
                "polygon",
                "quandl",
                "yfinance",
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """VALUATION."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/valuation",
            **inputs,
        )
