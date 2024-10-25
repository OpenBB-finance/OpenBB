### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_fixedincome_government(Container):
    """/fixedincome/government
    tips_yields
    treasury_rates
    us_yield_curve
    yield_curve
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def tips_yields(
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
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get current Treasury inflation-protected securities yields.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        maturity : Optional[Literal[5, 10, 20, 30]]
            The maturity of the security in years - 5, 10, 20, 30 - defaults to all. Note that the maturity is the tenor of the security, not the time to maturity. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert high frequency data to lower frequency.
                    None = No change
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    d = Daily
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]
            A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca']]
            Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[TipsYields]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TipsYields
        ----------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        due : Optional[date]
            The due date (maturation date) of the security.
        name : Optional[str]
            The name of the security.
        value : Optional[float]
            The yield value.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.tips_yields(provider='fred')
        >>> obb.fixedincome.government.tips_yields(maturity=10, provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/tips_yields",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.tips_yields",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def treasury_rates(
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
            Optional[Literal["federal_reserve", "fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Government Treasury Rates.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fmp.

        Returns
        -------
        OBBject
            results : List[TreasuryRates]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TreasuryRates
        -------------
        date : date
            The date of the data.
        week_4 : Optional[float]
            4 week Treasury bills rate (secondary market).
        month_1 : Optional[float]
            1 month Treasury rate.
        month_2 : Optional[float]
            2 month Treasury rate.
        month_3 : Optional[float]
            3 month Treasury rate.
        month_6 : Optional[float]
            6 month Treasury rate.
        year_1 : Optional[float]
            1 year Treasury rate.
        year_2 : Optional[float]
            2 year Treasury rate.
        year_3 : Optional[float]
            3 year Treasury rate.
        year_5 : Optional[float]
            5 year Treasury rate.
        year_7 : Optional[float]
            7 year Treasury rate.
        year_10 : Optional[float]
            10 year Treasury rate.
        year_20 : Optional[float]
            20 year Treasury rate.
        year_30 : Optional[float]
            30 year Treasury rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.treasury_rates(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/treasury_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.treasury_rates",
                        ("federal_reserve", "fmp"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
        category=OpenBBDeprecationWarning,
    )
    def us_yield_curve(
        self,
        date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(
                description="A specific date to get data for. Defaults to the most recent FRED entry."
            ),
        ] = None,
        inflation_adjusted: Annotated[
            Optional[bool], OpenBBField(description="Get inflation adjusted rates.")
        ] = False,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """US Yield Curve. Get United States yield curve.

        Parameters
        ----------
        date : Union[date, None, str]
            A specific date to get data for. Defaults to the most recent FRED entry.
        inflation_adjusted : Optional[bool]
            Get inflation adjusted rates.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

        Returns
        -------
        OBBject
            results : List[USYieldCurve]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        USYieldCurve
        ------------
        maturity : float
            Maturity of the treasury rate in years.
        rate : float
            Associated rate given in decimal form (0.05 is 5%)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.us_yield_curve(provider='fred')
        >>> obb.fixedincome.government.us_yield_curve(inflation_adjusted=True, provider='fred')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint will be removed in a future version. Use, `/fixedincome/government/yield_curve`, instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.4.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/government/us_yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.us_yield_curve",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                    "inflation_adjusted": inflation_adjusted,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def yield_curve(
        self,
        date: Annotated[
            Union[str, datetime.date, None, List[Union[str, datetime.date, None]]],
            OpenBBField(
                description="A specific date to get data for. By default is the current data. Multiple comma separated items allowed for provider(s): econdb, federal_reserve, fmp, fred."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["econdb", "federal_reserve", "fmp", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, federal_reserve, fmp, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get yield curve data by country and date.

        Parameters
        ----------
        date : Union[str, date, None, List[Union[str, date, None]]]
            A specific date to get data for. By default is the current data. Multiple comma separated items allowed for provider(s): econdb, federal_reserve, fmp, fred.
        provider : Optional[Literal['econdb', 'federal_reserve', 'fmp', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, federal_reserve, fmp, fred.
        country : Literal['australia', 'canada', 'china', 'hong_kong', 'india', 'japan', 'mexico', 'new_zealand', 'russia', 'saudi_arabia', 'singapore', 'south_africa', 'south_korea', 'taiwan', 'thailand', 'united_kingdom', 'united_states']
            The country to get data. New Zealand, Mexico, Singapore, and Thailand have only monthly data. The nearest date to the requested one will be used. (provider: econdb)
        use_cache : bool
            If true, cache the request for four hours. (provider: econdb)
        yield_curve_type : Literal['nominal', 'real', 'breakeven', 'treasury_minus_fed_funds', 'corporate_spot', 'corporate_par']
            Yield curve type. Nominal and Real Rates are available daily, others are monthly. The closest date to the requested date will be returned. (provider: fred)

        Returns
        -------
        OBBject
            results : List[YieldCurve]
                Serializable results.
            provider : Optional[Literal['econdb', 'federal_reserve', 'fmp', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        YieldCurve
        ----------
        date : Optional[date]
            The date of the data.
        maturity : str
            Maturity length of the security.
        rate : float
            The yield as a normalized percent (0.05 is 5%)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.government.yield_curve(provider='federal_reserve')
        >>> obb.fixedincome.government.yield_curve(date='2023-05-01,2024-05-01', provider='fmp')
        >>> obb.fixedincome.government.yield_curve(date='2023-05-01', country='united_kingdom', provider='econdb')
        >>> obb.fixedincome.government.yield_curve(provider='fred', yield_curve_type='real', date='2023-05-01,2024-05-01')
        """  # noqa: E501

        return self._run(
            "/fixedincome/government/yield_curve",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.government.yield_curve",
                        ("econdb", "federal_reserve", "fmp", "fred"),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                info={
                    "date": {
                        "econdb": {"multiple_items_allowed": True, "choices": None},
                        "federal_reserve": {
                            "multiple_items_allowed": True,
                            "choices": None,
                        },
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "fred": {"multiple_items_allowed": True, "choices": None},
                    }
                },
            )
        )
