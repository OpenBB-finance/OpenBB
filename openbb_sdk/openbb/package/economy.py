### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class CLASS_economy(Container):
    """/economy
    available_indices
    const
    cpi
    index
    risk
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def available_indices(
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List]:
        """AVAILABLE_INDICES.

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
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        AvailableIndices
        ----------------
        symbol : Optional[str]
            Symbol to get data for.
        name : Optional[str]
            Name of the index.
        currency : Optional[str]
            Currency the index is traded in.
        stock_exchange : Optional[str]
            Stock exchange where the index is listed.
        exchange_short_name : Optional[str]
            Short name of the stock exchange where the index is listed."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get the constituents of an index.

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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
    def country_codes(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
    def events(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
        provider: Optional[Literal["fmp", "polygon", "yfinance"]] = None,
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
        provider : Optional[Literal['fmp', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
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
            results : List[MajorIndicesHistorical]
                Serializable results.
            provider : Optional[Literal['fmp', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        MajorIndicesHistorical
        ----------------------
        date : Optional[datetime]
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
        vwap : Optional[float]
            Volume Weighted Average Price of the symbol.
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List]:
        """Market Risk Premium.

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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
            ]
        ] = None,
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """SEARCH_INDEX."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        return self._command_runner.run(
            "/economy/search_index",
            **inputs,
        )

    @validate_arguments
    def spending(
        self,
        chart: bool = False,
        provider: Optional[
            Literal[
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
                "benzinga", "cboe", "fmp", "fred", "intrinio", "polygon", "yfinance"
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
