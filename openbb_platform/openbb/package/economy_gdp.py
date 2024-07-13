### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_economy_gdp(Container):
    """/economy/gdp
    forecast
    nominal
    real
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def forecast(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["oecd"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get Forecasted GDP Data.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        country : str
            Country, or countries, to get forward GDP projections for. Default is all. Multiple comma separated items allowed. (provider: oecd)
        frequency : Literal['annual', 'quarter']
            Frequency of the data, default is annual. (provider: oecd)
        units : Literal['current_prices', 'volume', 'capita', 'growth', 'deflator']
            Units of the data, default is volume (chain linked volume, 2015).current_prices, volume, and capita are expressed in USD; growth as a percent; deflator as an index. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GdpForecast]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        GdpForecast
        -----------
        date : date
            The date of the data.
        country : str
            None
        value : Union[int, float]
            Forecasted GDP value for the country and date.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.gdp.forecast(provider='oecd')
        >>> obb.economy.gdp.forecast(country='united_states,germany,france', frequency='annual', units='capita', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/gdp/forecast",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.gdp.forecast",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True}}},
            )
        )

    @exception_handler
    @validate
    def nominal(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["econdb", "oecd"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, oecd."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get Nominal GDP Data.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['econdb', 'oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, oecd.
        country : str
            The country to get data.Use 'all' to get data for all available countries. Multiple comma separated items allowed. (provider: econdb, oecd)
        use_cache : bool
            If True, the request will be cached for one day. Using cache is recommended to avoid needlessly requesting the same data. (provider: econdb)
        frequency : Literal['quarter', 'annual']
            Frequency of the data. (provider: oecd)
        units : Literal['level', 'index', 'capita']
            The unit of measurement for the data.Both 'level' and 'capita' (per) are measured in USD. (provider: oecd)
        price_base : Literal['current_prices', 'volume']
            Price base for the data, volume is chain linked volume. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GdpNominal]
                Serializable results.
            provider : Optional[Literal['econdb', 'oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        GdpNominal
        ----------
        date : date
            The date of the data.
        country : Optional[str]
            The country represented by the GDP value.
        value : Union[int, float]
            GDP value for the country and date.
        real_growth_qoq : Optional[float]
            Real GDP growth rate quarter over quarter. (provider: econdb)
        real_growth_yoy : Optional[float]
            Real GDP growth rate year over year. (provider: econdb)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.gdp.nominal(provider='oecd')
        >>> obb.economy.gdp.nominal(units='capita', country='all', frequency='annual', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/gdp/nominal",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.gdp.nominal",
                        ("econdb", "oecd"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "country": {
                        "econdb": {"multiple_items_allowed": True},
                        "oecd": ["multiple_items_allowed"],
                    }
                },
            )
        )

    @exception_handler
    @validate
    def real(
        self,
        units: Annotated[
            Literal["idx", "qoq", "yoy"],
            OpenBBField(
                description="The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)"
            ),
        ] = "yoy",
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["oecd"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get Real GDP Data.

        Parameters
        ----------
        units : Literal['idx', 'qoq', 'yoy']
            The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        country : Literal['G20', 'G7', 'argentina', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_20', 'euro_area_19', 'europe', 'european_union_27', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'oecd_total', 'poland', 'portugal', 'romania', 'russia', 'saudi_arabia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states', 'all']
            Country to get GDP for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[GdpReal]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        GdpReal
        -------
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            Nominal GDP value on the date.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.gdp.real(provider='oecd')
        >>> obb.economy.gdp.real(units='yoy', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/gdp/real",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.gdp.real",
                        ("oecd",),
                    )
                },
                standard_params={
                    "units": units,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )
