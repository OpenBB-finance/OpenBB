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


class ROUTER_economy(Container):
    """/economy
    calendar
    cpi
    /gdp
    risk_premium
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def calendar(
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
        provider: Optional[Literal["fmp", "tradingeconomics"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Economic Calendar.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'tradingeconomics']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        country : Optional[Union[str, List[str]]]
            Country of the event (provider: tradingeconomics)
        importance : Optional[Literal['Low', 'Medium', 'High']]
            Importance of the event. (provider: tradingeconomics)
        group : Optional[Literal['interest rate', 'inflation', 'bonds', 'consumer', 'gdp', 'government', 'housing', 'labour', 'markets', 'money', 'prices', 'trade', 'business']]
            Grouping of events (provider: tradingeconomics)

        Returns
        -------
        OBBject
            results : List[EconomicCalendar]
                Serializable results.
            provider : Optional[Literal['fmp', 'tradingeconomics']]
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
            The date of the data.
        country : Optional[str]
            Country of event.
        event : Optional[str]
            Event name.
        reference : Optional[str]
            Abbreviated period for which released data refers to.
        source : Optional[str]
            Source of the data.
        sourceurl : Optional[str]
            Source URL.
        actual : Optional[Union[str, float]]
            Latest released value.
        previous : Optional[Union[str, float]]
            Value for the previous period after the revision (if revision is applicable).
        consensus : Optional[Union[str, float]]
            Average forecast among a representative group of economists.
        forecast : Optional[Union[str, float]]
            Trading Economics projections
        url : Optional[str]
            Trading Economics URL
        importance : Optional[Union[Literal[0, 1, 2, 3], str]]
            Importance of the event. 1-Low, 2-Medium, 3-High
        currency : Optional[str]
            Currency of the data.
        unit : Optional[str]
            Unit of the data.
        change : Optional[float]
            Value change since previous. (provider: fmp)
        change_percent : Optional[float]
            Percentage change since previous. (provider: fmp)
        updated_at : Optional[datetime]
            Last updated timestamp. (provider: fmp)
        created_at : Optional[datetime]
            Created at timestamp. (provider: fmp)

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
            OpenBBCustomParameter(
                description="The unit of measurement for the data.\n    Options:\n    - `growth_previous`: growth from the previous period\n    - `growth_same`: growth from the same period in the previous year\n    - `index_2015`: index with base year 2015."
            ),
        ] = "growth_same",
        frequency: Annotated[
            Literal["monthly", "quarter", "annual"],
            OpenBBCustomParameter(
                description="The frequency of the data.\n    Options: `monthly`, `quarter`, and `annual`."
            ),
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
        """Consumer Price Index (CPI) Data.

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
            results : List[ConsumerPriceIndex]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ConsumerPriceIndex
        ------------------
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

    @property
    def gdp(self):  # route = "/economy/gdp"
        from . import economy_gdp

        return economy_gdp.ROUTER_economy_gdp(command_runner=self._command_runner)

    @validate
    def risk_premium(
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Market Risk Premium.

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
            Country-specific risk premium.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.risk_premium()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/economy/risk_premium",
            **inputs,
        )
