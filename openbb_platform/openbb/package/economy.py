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
    const
    cpi
    fred_index
    index
    risk
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def available_indices(
        self, provider: Union[Literal["fmp"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Lists of available indices from a provider.

        Parameters
        ----------
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[AvailableIndices]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        stock_exchange : Optional[Union[str]]
            Stock exchange where the index is listed. (provider: fmp)
        exchange_short_name : Optional[Union[str]]
            Short name of the stock exchange where the index is listed. (provider: fmp)
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
        """Get the constituents of an index.

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
            Symbol to get data for.
        name : str
            Name of the constituent company in the index.
        sector : str
            Sector the constituent company in the index belongs to.
        sub_sector : Optional[Union[str]]
            Sub-sector the constituent company in the index belongs to.
        headquarter : Optional[Union[str]]
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

    @validate(listify_params={"countries": 1})
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
            OpenBBCustomParameter(description="The data units."),
        ] = "growth_same",
        frequency: typing_extensions.Annotated[
            Literal["monthly", "quarter", "annual"],
            OpenBBCustomParameter(description="The data time frequency."),
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
        """CPI.

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
        date : Optional[Union[date]]
            The date of the data.
        value : Optional[Union[float]]
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
        """Fred Historical.

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
        provider: Union[Literal["fmp", "polygon"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get historical  levels for an index.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp', 'polygon'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        timeseries : Optional[Union[typing_extensions.Annotated[int, Ge(ge=0)]]]
            Number of days to look back. (provider: fmp)
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour', '1day']
            Data granularity. (provider: fmp)
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

        Returns
        -------
        OBBject
            results : Union[List[MajorIndicesHistorical]]
                Serializable results.
            provider : Union[Literal['fmp', 'polygon'], None]
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
        volume : Optional[int]
            The volume of the symbol.
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
    def risk(
        self, provider: Union[Literal["fmp"], None] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Market Risk Premium.

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
