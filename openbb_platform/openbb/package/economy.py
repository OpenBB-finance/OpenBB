### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_economy(Container):
    """/economy
    calendar
    composite_leading_indicator
    cpi
    fred_regional
    fred_search
    fred_series
    /gdp
    long_term_interest_rate
    money_measures
    risk_premium
    short_term_interest_rate
    unemployment
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
    ) -> OBBject:
        """Get the upcoming, or historical, economic calendar of global events.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'tradingeconomics']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        country : Optional[str]
            Country of the event. Multiple items allowed. (provider: tradingeconomics)
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
        >>> obb.economy.calendar(provider="fmp", start_date="2020-03-01", end_date="2020-03-31")
        >>> #### By default, the calendar will be forward-looking. ####
        >>> obb.economy.calendar(provider="nasdaq")
        """  # noqa: E501

        return self._run(
            "/economy/calendar",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/calendar",
                        ("fmp", "tradingeconomics"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def composite_leading_indicator(
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject:
        """The composite leading indicator (CLI) is designed to provide early signals of turning points
        in business cycles showing fluctuation of the economic activity around its long term potential level.
        CLIs show short-term economic movements in qualitative rather than quantitative terms.


            Parameters
            ----------
            start_date : Union[datetime.date, None, str]
                Start date of the data, in YYYY-MM-DD format.
            end_date : Union[datetime.date, None, str]
                End date of the data, in YYYY-MM-DD format.
            provider : Optional[Literal['oecd']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'oecd' if there is
                no default.
            country : Literal['united_states', 'united_kingdom', 'japan', 'mexico', 'indonesia', 'australia', 'brazil', 'canada', 'italy', 'germany', 'turkey', 'france', 'south_africa', 'south_korea', 'spain', 'india', 'china', 'g7', 'g20', 'all']
                Country to get GDP for. (provider: oecd)

            Returns
            -------
            OBBject
                results : List[CLI]
                    Serializable results.
                provider : Optional[Literal['oecd']]
                    Provider name.
                warnings : Optional[List[Warning_]]
                    List of warnings.
                chart : Optional[Chart]
                    Chart object.
                extra: Dict[str, Any]
                    Extra info.

            CLI
            ---
            date : Optional[date]
                The date of the data.
            value : Optional[float]
                CLI value
            country : Optional[str]
                Country for which CLI is given

            Example
            -------
            >>> from openbb import obb
            >>> obb.economy.composite_leading_indicator(country="all").to_df()
        """  # noqa: E501

        return self._run(
            "/economy/composite_leading_indicator",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/composite_leading_indicator",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def cpi(
        self,
        country: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The country to get data. Multiple items allowed: fred."
            ),
        ],
        units: Annotated[
            Literal["growth_previous", "growth_same", "index_2015"],
            OpenBBCustomParameter(
                description="The unit of measurement for the data.\n    Options:\n    - `growth_previous`: Percent growth from the previous period.\n      If monthly data, this is month-over-month, etc\n    - `growth_same`: Percent growth from the same period in the previous year.\n      If looking at monthly data, this would be year-over-year, etc.\n    - `index_2015`: Rescaled index value, such that the value in 2015 is 100."
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
    ) -> OBBject:
        """Consumer Price Index (CPI).  Returns either the rescaled index value, or a rate of change (inflation).

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple items allowed: fred.
        units : Literal['growth_previous', 'growth_same', 'index_2015']
            The unit of measurement for the data.
            Options:
            - `growth_previous`: Percent growth from the previous period.
              If monthly data, this is month-over-month, etc
            - `growth_same`: Percent growth from the same period in the previous year.
              If looking at monthly data, this would be year-over-year, etc.
            - `index_2015`: Rescaled index value, such that the value in 2015 is 100.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data.
            Options: `monthly`, `quarter`, and `annual`.
        harmonized : bool
            Whether you wish to obtain harmonized data.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
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
        >>> obb.economy.cpi(countries=["japan", "china", "turkey"]).to_df()
        >>> #### Use the `units` parameter to define the reference period for the change in values. ####
        >>> obb.economy.cpi(countries=["united_states", "united_kingdom"], units="growth_previous").to_df()
        """  # noqa: E501

        return self._run(
            "/economy/cpi",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/cpi",
                        ("fred",),
                    )
                },
                standard_params={
                    "country": country,
                    "units": units,
                    "frequency": frequency,
                    "harmonized": harmonized,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                extra_info={"country": {"multiple_items_allowed": ["fred"]}},
            )
        )

    @validate
    def fred_regional(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: fred."
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
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100000,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """
        Query the Geo Fred API for regional economic data by series group.
        The series group ID is found by using `fred_search` and the `series_id` parameter.


            Parameters
            ----------
            symbol : Union[str, List[str]]
                Symbol to get data for. Multiple items allowed: fred.
            start_date : Union[datetime.date, None, str]
                Start date of the data, in YYYY-MM-DD format.
            end_date : Union[datetime.date, None, str]
                End date of the data, in YYYY-MM-DD format.
            limit : Optional[int]
                The number of data entries to return.
            provider : Optional[Literal['fred']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'fred' if there is
                no default.
            is_series_group : bool
                When True, the symbol provided is for a series_group, else it is for a series ID. (provider: fred)
            region_type : Optional[Literal['bea', 'msa', 'frb', 'necta', 'state', 'country', 'county', 'censusregion']]
                The type of regional data. Parameter is only valid when `is_series_group` is True. (provider: fred)
            season : Optional[Literal['SA', 'NSA', 'SSA']]
                The seasonal adjustments to the data. Parameter is only valid when `is_series_group` is True. (provider: fred)
            units : Optional[str]
                The units of the data. This should match the units returned from searching by series ID. An incorrect field will not necessarily return an error. Parameter is only valid when `is_series_group` is True. (provider: fred)
            frequency : Optional[Literal['d', 'w', 'bw', 'm', 'q', 'sa', 'a', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                    Frequency aggregation to convert high frequency data to lower frequency.
                    Parameter is only valid when `is_series_group` is True.
                        a = Annual
                        sa= Semiannual
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
                    This parameter has no affect if the frequency parameter is not set.
                    Only valid when `is_series_group` is True.
                        avg = Average
                        sum = Sum
                        eop = End of Period
                     (provider: fred)
            transform : Literal['lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']

                    Transformation type. Only valid when `is_series_group` is True.
                        lin = Levels (No transformation)
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
                results : List[FredRegional]
                    Serializable results.
                provider : Optional[Literal['fred']]
                    Provider name.
                warnings : Optional[List[Warning_]]
                    List of warnings.
                chart : Optional[Chart]
                    Chart object.
                extra: Dict[str, Any]
                    Extra info.

            FredRegional
            ------------
            date : date
                The date of the data.
            region : Optional[str]
                The name of the region. (provider: fred)
            code : Optional[Union[str, int]]
                The code of the region. (provider: fred)
            value : Optional[Union[float, int]]
                The obersvation value. The units are defined in the search results by series ID. (provider: fred)
            series_id : Optional[str]
                The individual series ID for the region. (provider: fred)

            Example
            -------
            >>> from openbb import obb
            >>> #### With no date, the most recent report is returned. ####
            >>> obb.economy.fred_regional("NYICLAIMS")
            >>> #### With a date, time series data is returned. ####
            >>> obb.economy.fred_regional("NYICLAIMS", start_date="2021-01-01")
        """  # noqa: E501

        return self._run(
            "/economy/fred_regional",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/fred_regional",
                        ("fred",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fred"]}},
            )
        )

    @validate
    def fred_search(
        self,
        query: Annotated[
            Optional[str], OpenBBCustomParameter(description="The search word(s).")
        ] = None,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> OBBject:
        """
        Search for FRED series or economic releases by ID or string.
        This does not return the observation values, only the metadata.
        Use this function to find series IDs for `fred_series()`.


            Parameters
            ----------
            query : Optional[str]
                The search word(s).
            provider : Optional[Literal['fred']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'fred' if there is
                no default.
            is_release : Optional[bool]
                Is release?  If True, other search filter variables are ignored. If no query text or release_id is supplied, this defaults to True. (provider: fred)
            release_id : Optional[Union[int, str]]
                A specific release ID to target. (provider: fred)
            limit : Optional[int]
                The number of data entries to return. (1-1000) (provider: fred)
            offset : Optional[Annotated[int, Ge(ge=0)]]
                Offset the results in conjunction with limit. (provider: fred)
            filter_variable : Literal[None, 'frequency', 'units', 'seasonal_adjustment']
                Filter by an attribute. (provider: fred)
            filter_value : Optional[str]
                String value to filter the variable by.  Used in conjunction with filter_variable. (provider: fred)
            tag_names : Optional[str]
                A semicolon delimited list of tag names that series match all of.  Example: 'japan;imports' (provider: fred)
            exclude_tag_names : Optional[str]
                A semicolon delimited list of tag names that series match none of.  Example: 'imports;services'. Requires that variable tag_names also be set to limit the number of matching series. (provider: fred)
            series_id : Optional[str]
                A FRED Series ID to return series group information for. This returns the required information to query for regional data. Not all series that are in FRED have geographical data. Entering a value for series_id will override all other parameters. Multiple series_ids can be separated by commas. (provider: fred)

            Returns
            -------
            OBBject
                results : List[FredSearch]
                    Serializable results.
                provider : Optional[Literal['fred']]
                    Provider name.
                warnings : Optional[List[Warning_]]
                    List of warnings.
                chart : Optional[Chart]
                    Chart object.
                extra: Dict[str, Any]
                    Extra info.

            FredSearch
            ----------
            release_id : Optional[Union[int, str]]
                The release ID for queries.
            series_id : Optional[str]
                The series ID for the item in the release.
            name : Optional[str]
                The name of the release.
            title : Optional[str]
                The title of the series.
            observation_start : Optional[date]
                The date of the first observation in the series.
            observation_end : Optional[date]
                The date of the last observation in the series.
            frequency : Optional[str]
                The frequency of the data.
            frequency_short : Optional[str]
                Short form of the data frequency.
            units : Optional[str]
                The units of the data.
            units_short : Optional[str]
                Short form of the data units.
            seasonal_adjustment : Optional[str]
                The seasonal adjustment of the data.
            seasonal_adjustment_short : Optional[str]
                Short form of the data seasonal adjustment.
            last_updated : Optional[datetime]
                The datetime of the last update to the data.
            notes : Optional[str]
                Description of the release.
            press_release : Optional[bool]
                If the release is a press release.
            url : Optional[str]
                URL to the release.
            popularity : Optional[int]
                Popularity of the series (provider: fred)
            group_popularity : Optional[int]
                Group popularity of the release (provider: fred)
            region_type : Optional[str]
                The region type of the series. (provider: fred)
            series_group : Optional[Union[int, str]]
                The series group ID of the series. This value is used to query for regional data. (provider: fred)

            Example
            -------
            >>> from openbb import obb
            >>> obb.economy.fred_search()
        """  # noqa: E501

        return self._run(
            "/economy/fred_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/fred_search",
                        ("fred",),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def fred_series(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: fred."
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
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100000,
        provider: Optional[Literal["fred", "intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Get data by series ID from FRED.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: fred.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['fred', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fred' if there is
            no default.
        frequency : Literal[None, 'a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']

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
        aggregation_method : Literal[None, 'avg', 'sum', 'eop']

                A key that indicates the aggregation method used for frequency aggregation.
                This parameter has no affect if the frequency parameter is not set.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Literal[None, 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']

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
        all_pages : Optional[bool]
            Returns all pages of data from the API call at once. (provider: intrinio)
        sleep : Optional[float]
            Time to sleep between requests to avoid rate limiting. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[FredSeries]
                Serializable results.
            provider : Optional[Literal['fred', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FredSeries
        ----------
        date : date
            The date of the data.
        value : Optional[float]
            Value of the index. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.fred_series("NFCI").to_df()
        >>> #### Multiple series can be passed in as a list. ####
        >>> obb.economy.fred_series(["NFCI","STLFSI4"]).to_df()
        >>> #### Use the `transform` parameter to transform the data as change, log, or percent change. ####
        >>> obb.economy.fred_series("CBBTCUSD", transform="pc1").to_df()
        """  # noqa: E501

        return self._run(
            "/economy/fred_series",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/fred_series",
                        ("fred", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fred"]}},
            )
        )

    @property
    def gdp(self):
        # pylint: disable=import-outside-toplevel
        from . import economy_gdp

        return economy_gdp.ROUTER_economy_gdp(command_runner=self._command_runner)

    @validate
    def long_term_interest_rate(
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject:
        """
        Long-term interest rates refer to government bonds maturing in ten years.
        Rates are mainly determined by the price charged by the lender, the risk from the borrower and the
        fall in the capital value. Long-term interest rates are generally averages of daily rates,
        measured as a percentage. These interest rates are implied by the prices at which the government bonds are
        traded on financial markets, not the interest rates at which the loans were issued.
        In all cases, they refer to bonds whose capital repayment is guaranteed by governments.
        Long-term interest rates are one of the determinants of business investment.
        Low long-term interest rates encourage investment in new equipment and high interest rates discourage it.
        Investment is, in turn, a major source of economic growth.

            Parameters
            ----------
            start_date : Union[datetime.date, None, str]
                Start date of the data, in YYYY-MM-DD format.
            end_date : Union[datetime.date, None, str]
                End date of the data, in YYYY-MM-DD format.
            provider : Optional[Literal['oecd']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'oecd' if there is
                no default.
            country : Literal['belgium', 'ireland', 'mexico', 'indonesia', 'new_zealand', 'japan', 'united_kingdom', 'france', 'chile', 'canada', 'netherlands', 'united_states', 'south_korea', 'norway', 'austria', 'south_africa', 'denmark', 'switzerland', 'hungary', 'luxembourg', 'australia', 'germany', 'sweden', 'iceland', 'turkey', 'greece', 'israel', 'czech_republic', 'latvia', 'slovenia', 'poland', 'estonia', 'lithuania', 'portugal', 'costa_rica', 'slovakia', 'finland', 'spain', 'russia', 'euro_area19', 'colombia', 'italy', 'india', 'china', 'croatia', 'all']
                Country to get GDP for. (provider: oecd)
            frequency : Literal['monthly', 'quarterly', 'annual']
                Frequency to get interest rate for for. (provider: oecd)

            Returns
            -------
            OBBject
                results : List[LTIR]
                    Serializable results.
                provider : Optional[Literal['oecd']]
                    Provider name.
                warnings : Optional[List[Warning_]]
                    List of warnings.
                chart : Optional[Chart]
                    Chart object.
                extra: Dict[str, Any]
                    Extra info.

            LTIR
            ----
            date : Optional[date]
                The date of the data.
            value : Optional[float]
                Interest rate (given as a whole number, i.e 10=10%)
            country : Optional[str]
                Country for which interest rate is given

            Example
            -------
            >>> from openbb import obb
            >>> obb.economy.long_term_interest_rate(country="all", frequency="quarterly").to_df()
        """  # noqa: E501

        return self._run(
            "/economy/long_term_interest_rate",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/long_term_interest_rate",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def money_measures(
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
        adjusted: Annotated[
            Optional[bool],
            OpenBBCustomParameter(
                description="Whether to return seasonally adjusted data."
            ),
        ] = True,
        provider: Optional[Literal["federal_reserve"]] = None,
        **kwargs
    ) -> OBBject:
        """Money Measures (M1/M2 and components). The Federal Reserve publishes as part of the H.6 Release.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        adjusted : Optional[bool]
            Whether to return seasonally adjusted data.
        provider : Optional[Literal['federal_reserve']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'federal_reserve' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[MoneyMeasures]
                Serializable results.
            provider : Optional[Literal['federal_reserve']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        MoneyMeasures
        -------------
        month : date
            The date of the data.
        M1 : float
            Value of the M1 money supply in billions.
        M2 : float
            Value of the M2 money supply in billions.
        currency : Optional[float]
            Value of currency in circulation in billions.
        demand_deposits : Optional[float]
            Value of demand deposits in billions.
        retail_money_market_funds : Optional[float]
            Value of retail money market funds in billions.
        other_liquid_deposits : Optional[float]
            Value of other liquid deposits in billions.
        small_denomination_time_deposits : Optional[float]
            Value of small denomination time deposits in billions.

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.money_measures(adjusted=False).to_df()
        """  # noqa: E501

        return self._run(
            "/economy/money_measures",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/money_measures",
                        ("federal_reserve",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "adjusted": adjusted,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def risk_premium(
        self, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> OBBject:
        """Market Risk Premium by country.

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
        >>> obb.economy.risk_premium().to_df()
        """  # noqa: E501

        return self._run(
            "/economy/risk_premium",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/risk_premium",
                        ("fmp",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @validate
    def short_term_interest_rate(
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject:
        """
        Short-term interest rates are the rates at which short-term borrowings are effected between
        financial institutions or the rate at which short-term government paper is issued or traded in the market.
        Short-term interest rates are generally averages of daily rates, measured as a percentage.
        Short-term interest rates are based on three-month money market rates where available.
        Typical standardised names are "money market rate" and "treasury bill rate".


            Parameters
            ----------
            start_date : Union[datetime.date, None, str]
                Start date of the data, in YYYY-MM-DD format.
            end_date : Union[datetime.date, None, str]
                End date of the data, in YYYY-MM-DD format.
            provider : Optional[Literal['oecd']]
                The provider to use for the query, by default None.
                If None, the provider specified in defaults is selected or 'oecd' if there is
                no default.
            country : Literal['belgium', 'ireland', 'mexico', 'indonesia', 'new_zealand', 'japan', 'united_kingdom', 'france', 'chile', 'canada', 'netherlands', 'united_states', 'south_korea', 'norway', 'austria', 'south_africa', 'denmark', 'switzerland', 'hungary', 'luxembourg', 'australia', 'germany', 'sweden', 'iceland', 'turkey', 'greece', 'israel', 'czech_republic', 'latvia', 'slovenia', 'poland', 'estonia', 'lithuania', 'portugal', 'costa_rica', 'slovakia', 'finland', 'spain', 'russia', 'euro_area19', 'colombia', 'italy', 'india', 'china', 'croatia', 'all']
                Country to get GDP for. (provider: oecd)
            frequency : Literal['monthly', 'quarterly', 'annual']
                Frequency to get interest rate for for. (provider: oecd)

            Returns
            -------
            OBBject
                results : List[STIR]
                    Serializable results.
                provider : Optional[Literal['oecd']]
                    Provider name.
                warnings : Optional[List[Warning_]]
                    List of warnings.
                chart : Optional[Chart]
                    Chart object.
                extra: Dict[str, Any]
                    Extra info.

            STIR
            ----
            date : Optional[date]
                The date of the data.
            value : Optional[float]
                Interest rate (given as a whole number, i.e 10=10%)
            country : Optional[str]
                Country for which interest rate is given

            Example
            -------
            >>> from openbb import obb
            >>> obb.economy.short_term_interest_rate(country="all", frequency="quarterly").to_df()
        """  # noqa: E501

        return self._run(
            "/economy/short_term_interest_rate",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/short_term_interest_rate",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def unemployment(
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
        provider: Optional[Literal["oecd"]] = None,
        **kwargs
    ) -> OBBject:
        """Global unemployment data.

        Parameters
        ----------
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'oecd' if there is
            no default.
        country : Literal['colombia', 'new_zealand', 'united_kingdom', 'italy', 'luxembourg', 'euro_area19', 'sweden', 'oecd', 'south_africa', 'denmark', 'canada', 'switzerland', 'slovakia', 'hungary', 'portugal', 'spain', 'france', 'czech_republic', 'costa_rica', 'japan', 'slovenia', 'russia', 'austria', 'latvia', 'netherlands', 'israel', 'iceland', 'united_states', 'ireland', 'mexico', 'germany', 'greece', 'turkey', 'australia', 'poland', 'south_korea', 'chile', 'finland', 'european_union27_2020', 'norway', 'lithuania', 'euro_area20', 'estonia', 'belgium', 'brazil', 'indonesia', 'all']
            Country to get GDP for. (provider: oecd)
        sex : Literal['total', 'male', 'female']
            Sex to get unemployment for. (provider: oecd)
        frequency : Literal['monthly', 'quarterly', 'annual']
            Frequency to get unemployment for. (provider: oecd)
        age : Literal['total', '15-24', '15-64', '25-54', '55-64']
            Age group to get unemployment for. Total indicates 15 years or over (provider: oecd)
        seasonal_adjustment : bool
            Whether to get seasonally adjusted unemployment. Defaults to False. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[Unemployment]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        Unemployment
        ------------
        date : Optional[date]
            The date of the data.
        value : Optional[float]
            Unemployment rate (given as a whole number, i.e 10=10%)
        country : Optional[str]
            Country for which unemployment rate is given

        Example
        -------
        >>> from openbb import obb
        >>> obb.economy.unemployment(country="all", frequency="quarterly")
        >>> #### Demographics for the statistics are selected with the `age` and `sex` parameters. ####
        >>> obb.economy.unemployment(
        >>> country="all", frequency="quarterly", age="25-54"
        >>> ).to_df().pivot(columns="country", values="value")
        """  # noqa: E501

        return self._run(
            "/economy/unemployment",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/economy/unemployment",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )
