### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union
from warnings import simplefilter, warn

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_fixedincome(Container):
    """/fixedincome
    bond_indices
    /corporate
    /government
    mortgage_indices
    /rate
    sofr
    /spreads
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def bond_indices(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        index_type: Annotated[
            Literal["yield", "yield_to_worst", "total_return", "oas"],
            OpenBBField(
                description="The type of series. OAS is the option-adjusted spread. Default is yield."
            ),
        ] = "yield",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Bond Indices.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['yield', 'yield_to_worst', 'total_return', 'oas']
            The type of series. OAS is the option-adjusted spread. Default is yield.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        category : Literal['high_yield', 'us', 'emerging_markets']
            The type of index category. Used in conjunction with 'index', default is 'us'. (provider: fred)
        index : str
            The specific index to query. Used in conjunction with 'category' and 'index_type', default is 'yield_curve'. Multiple comma separated items allowed. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
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
        aggregation_method : Literal['avg', 'sum', 'eop']

                A key that indicates the aggregation method used for frequency aggregation.
                This parameter has no affect if the frequency parameter is not set, default is 'avg'.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[BondIndices]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BondIndices
        -----------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        value : float
            Index values.
        maturity : Optional[str]
            The maturity range of the bond index. Only applicable when 'index' is 'yield_curve'. (provider: fred)
        title : Optional[str]
            The title of the index. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> # The default state for FRED are series for constructing the US Corporate Bond Yield Curve.
        >>> obb.fixedincome.bond_indices(provider='fred')
        >>> # Multiple indices, from within the same 'category', can be requested.
        >>> obb.fixedincome.bond_indices(category='high_yield', index='us,europe,emerging', index_type='total_return', provider='fred')
        >>> # From FRED, there are three main categories, 'high_yield', 'us', and 'emerging_markets'. Emerging markets is a broad category.
        >>> obb.fixedincome.bond_indices(category='emerging_markets', index='corporate,private_sector,public_sector', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/bond_indices",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.bond_indices",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "index_type": index_type,
                },
                extra_params=kwargs,
                info={
                    "index": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "a",
                                "aa",
                                "aaa",
                                "asia",
                                "b",
                                "bb",
                                "bbb",
                                "ccc",
                                "corporate",
                                "crossover",
                                "emea",
                                "high_grade",
                                "high_yield",
                                "latam",
                                "liquid_aaa",
                                "liquid_asia",
                                "liquid_bbb",
                                "liquid_corporate",
                                "liquid_emea",
                                "liquid_latam",
                                "non_financial",
                                "private_sector",
                                "public_sector",
                                "seasoned_corporate",
                                "yield_curve",
                            ],
                        }
                    }
                },
            )
        )

    @property
    def corporate(self):
        # pylint: disable=import-outside-toplevel
        from . import fixedincome_corporate

        return fixedincome_corporate.ROUTER_fixedincome_corporate(
            command_runner=self._command_runner
        )

    @property
    def government(self):
        # pylint: disable=import-outside-toplevel
        from . import fixedincome_government

        return fixedincome_government.ROUTER_fixedincome_government(
            command_runner=self._command_runner
        )

    @exception_handler
    @validate
    def mortgage_indices(
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
        """Mortgage Indices.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        index : Union[Literal['primary', 'ltv_lte_80', 'ltv_gt_80', 'conforming_30y', 'conforming_30y_na', 'jumbo_30y', 'fha_30y', 'va_30y', 'usda_30y', 'conforming_15y', 'ltv_lte80_fico_ge740', 'ltv_lte80_fico_a720b739', 'ltv_lte80_fico_a700b719', 'ltv_lte80_fico_a680b699', 'ltv_lte80_fico_lt680', 'ltv_gt80_fico_ge740', 'ltv_gt80_fico_a720b739', 'ltv_gt80_fico_a700b719', 'ltv_gt80_fico_a680b699', 'ltv_gt80_fico_lt680'], str]
            The specific index, or index group, to query. Default is the 'primary' group. Multiple comma separated items allowed. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
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
        aggregation_method : Literal['avg', 'sum', 'eop']

                A key that indicates the aggregation method used for frequency aggregation.
                This parameter has no affect if the frequency parameter is not set, default is 'avg'.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[MortgageIndices]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MortgageIndices
        ---------------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the index.
        rate : float
            Mortgage rate.

        Examples
        --------
        >>> from openbb import obb
        >>> # The default state for FRED are the primary mortgage indices from Optimal Blue.
        >>> obb.fixedincome.mortgage_indices(provider='fred')
        >>> # Multiple indices can be requested.
        >>> obb.fixedincome.mortgage_indices(index='jumbo_30y,conforming_30y,conforming_15y', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/mortgage_indices",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.mortgage_indices",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "index": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "primary",
                                "ltv_lte_80",
                                "ltv_gt_80",
                                "conforming_30y",
                                "conforming_30y_na",
                                "jumbo_30y",
                                "fha_30y",
                                "va_30y",
                                "usda_30y",
                                "conforming_15y",
                                "ltv_lte80_fico_ge740",
                                "ltv_lte80_fico_a720b739",
                                "ltv_lte80_fico_a700b719",
                                "ltv_lte80_fico_a680b699",
                                "ltv_lte80_fico_lt680",
                                "ltv_gt80_fico_ge740",
                                "ltv_gt80_fico_a720b739",
                                "ltv_gt80_fico_a700b719",
                                "ltv_gt80_fico_a680b699",
                                "ltv_gt80_fico_lt680",
                            ],
                        }
                    }
                },
            )
        )

    @property
    def rate(self):
        # pylint: disable=import-outside-toplevel
        from . import fixedincome_rate

        return fixedincome_rate.ROUTER_fixedincome_rate(
            command_runner=self._command_runner
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint is deprecated; use `/fixedincome/rate/sofr` instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def sofr(
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
            Optional[Literal["federal_reserve", "fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Secured Overnight Financing Rate.

        The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
        borrowing cash overnight collateralizing by Treasury securities.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve', 'fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve, fred.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
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
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[SOFR]
                Serializable results.
            provider : Optional[Literal['federal_reserve', 'fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SOFR
        ----
        date : date
            The date of the data.
        rate : float
            Effective federal funds rate.
        percentile_1 : Optional[float]
            1st percentile of the distribution.
        percentile_25 : Optional[float]
            25th percentile of the distribution.
        percentile_75 : Optional[float]
            75th percentile of the distribution.
        percentile_99 : Optional[float]
            99th percentile of the distribution.
        volume : Optional[float]
            The trading volume.The notional volume of transactions (Billions of $).
        average_30d : Optional[float]
            30-Day Average SOFR (provider: fred)
        average_90d : Optional[float]
            90-Day Average SOFR (provider: fred)
        average_180d : Optional[float]
            180-Day Average SOFR (provider: fred)
        index : Optional[float]
            SOFR index as 2018-04-02 = 1 (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.sofr(provider='fred')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; use `/fixedincome/rate/sofr` instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/sofr",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.sofr",
                        ("federal_reserve", "fred"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @property
    def spreads(self):
        # pylint: disable=import-outside-toplevel
        from . import fixedincome_spreads

        return fixedincome_spreads.ROUTER_fixedincome_spreads(
            command_runner=self._command_runner
        )
