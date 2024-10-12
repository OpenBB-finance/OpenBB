### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_economy_survey(Container):
    """/economy/survey
    bls_search
    bls_series
    economic_conditions_chicago
    manufacturing_outlook_texas
    nonfarm_payrolls
    sloos
    university_of_michigan
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def bls_search(
        self,
        query: Annotated[
            str,
            OpenBBField(
                description="The search word(s). Use semi-colon to separate multiple queries as an & operator."
            ),
        ] = "",
        provider: Annotated[
            Optional[Literal["bls"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: bls."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Search BLS surveys by category and keyword or phrase to identify BLS series IDs.

        Parameters
        ----------
        query : str
            The search word(s). Use semi-colon to separate multiple queries as an & operator.
        provider : Optional[Literal['bls']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: bls.
        category : Optional[Literal['cpi', 'pce', 'ppi', 'ip', 'jolts', 'nfp', 'cps', 'lfs', 'wages', 'ec', 'sla', 'bed', 'tu']]
            The category of BLS survey to search within.
                An empty search query will return all series within the category. Options are:

            cpi - Consumer Price Index

            pce - Personal Consumption Expenditure

            ppi - Producer Price Index

            ip - Industry Productivity

            jolts - Job Openings and Labor Turnover Survey

            nfp - Nonfarm Payrolls

            cps - Current Population Survey

            lfs - Labor Force Statistics

            wages - Wages

            ec - Employer Costs

            sla - State and Local Area Employment

            bed - Business Employment Dynamics

            tu - Time Use
                 (provider: bls)
        include_extras : bool
            Include additional information in the search results. Extra fields returned are metadata and vary by survey. Fields are undefined strings that typically have names ending with '_code'. (provider: bls)
        include_code_map : bool
            When True, includes the complete code map for eaçh survey in the category, returned separately as a nested JSON to the `extras['results_metadata']` property of the response. Example content is the NAICS industry map for PPI surveys. Each code is a value within the 'symbol' of the time series. (provider: bls)

        Returns
        -------
        OBBject
            results : List[BlsSearch]
                Serializable results.
            provider : Optional[Literal['bls']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BlsSearch
        ---------
        symbol : str
            Symbol representing the entity requested in the data.
        title : Optional[str]
            The title of the series.
        survey_name : Optional[str]
            The name of the survey.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.bls_search(provider='bls', category='cpi')
        >>> # Use semi-colon to separate multiple queries as an & operator.
        >>> obb.economy.survey.bls_search(provider='bls', category='cpi', query='seattle;gasoline')
        """  # noqa: E501

        return self._run(
            "/economy/survey/bls_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.bls_search",
                        ("bls",),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
                info={
                    "category": {
                        "bls": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "cpi",
                                "pce",
                                "ppi",
                                "ip",
                                "jolts",
                                "nfp",
                                "cps",
                                "lfs",
                                "wages",
                                "ec",
                                "sla",
                                "bed",
                                "tu",
                            ],
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def bls_series(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): bls."
            ),
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        chart: Annotated[
            bool,
            OpenBBField(
                description="Whether to create a chart or not, by default False."
            ),
        ] = False,
        provider: Annotated[
            Optional[Literal["bls"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: bls."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get time series data for one, or more, BLS series IDs.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): bls.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['bls']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: bls.
        calculations : bool
            Include calculations in the response, if available. Default is True. (provider: bls)
        annual_average : bool
            Include annual averages in the response, if available. Default is False. (provider: bls)
        aspects : bool
            Include all aspects associated with a data point for a given BLS series ID, if available. Returned with the series metadata, under `extras` of the response object. Default is False. (provider: bls)

        Returns
        -------
        OBBject
            results : List[BlsSeries]
                Serializable results.
            provider : Optional[Literal['bls']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BlsSeries
        ---------
        date : date
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        title : Optional[str]
            Title of the series.
        value : Optional[float]
            Observation value for the symbol and date.
        change_1_m : Optional[float]
            One month change in value. (provider: bls)
        change_3_m : Optional[float]
            Three month change in value. (provider: bls)
        change_6_m : Optional[float]
            Six month change in value. (provider: bls)
        change_12_m : Optional[float]
            One year change in value. (provider: bls)
        change_percent_1_m : Optional[float]
            One month change in percent. (provider: bls)
        change_percent_3_m : Optional[float]
            Three month change in percent. (provider: bls)
        change_percent_6_m : Optional[float]
            Six month change in percent. (provider: bls)
        change_percent_12_m : Optional[float]
            One year change in percent. (provider: bls)
        latest : Optional[bool]
            Latest value indicator. (provider: bls)
        footnotes : Optional[str]
            Footnotes accompanying the value. (provider: bls)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.bls_series(provider='bls', symbol='CES0000000001')
        """  # noqa: E501

        return self._run(
            "/economy/survey/bls_series",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.bls_series",
                        ("bls",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                chart=chart,
                info={
                    "symbol": {"bls": {"multiple_items_allowed": True, "choices": None}}
                },
            )
        )

    @exception_handler
    @validate
    def economic_conditions_chicago(
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
        """Get The Survey Of Economic Conditions For The Chicago Region.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        frequency : Optional[Literal['annual', 'quarter']]
            Frequency aggregation to convert monthly data to lower frequency. None is monthly. (provider: fred)
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
            results : List[SurveyOfEconomicConditionsChicago]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SurveyOfEconomicConditionsChicago
        ---------------------------------
        date : date
            The date of the data.
        activity_index : Optional[float]
            Activity Index.
        one_year_outlook : Optional[float]
            One Year Outlook Index.
        manufacturing_activity : Optional[float]
            Manufacturing Activity Index.
        non_manufacturing_activity : Optional[float]
            Non-Manufacturing Activity Index.
        capital_expenditures_expectations : Optional[float]
            Capital Expenditures Expectations Index.
        hiring_expectations : Optional[float]
            Hiring Expectations Index.
        current_hiring : Optional[float]
            Current Hiring Index.
        labor_costs : Optional[float]
            Labor Costs Index.
        non_labor_costs : Optional[float]
            Non-Labor Costs Index.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.economic_conditions_chicago(provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/survey/economic_conditions_chicago",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.economic_conditions_chicago",
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
    def manufacturing_outlook_texas(
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
        """Get The Manufacturing Outlook Survey For The Texas Region.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        topic : Union[Literal['business_activity', 'business_outlook', 'capex', 'prices_paid', 'production', 'inventory', 'new_orders', 'new_orders_growth', 'unfilled_orders', 'shipments', 'delivery_time', 'employment', 'wages', 'hours_worked'], str]
            The topic for the survey response. Multiple comma separated items allowed. (provider: fred)
        frequency : Optional[Literal['annual', 'quarter']]

                Frequency aggregation to convert monthly data to lower frequency. None is monthly.
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
            results : List[ManufacturingOutlookTexas]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ManufacturingOutlookTexas
        -------------------------
        date : date
            The date of the data.
        topic : Optional[str]
            Topic of the survey response.
        diffusion_index : Optional[float]
            Diffusion Index.
        percent_reporting_increase : Optional[float]
            Percent of respondents reporting an increase over the last month.
        percent_reporting_decrease : Optional[float]
            Percent of respondents reporting a decrease over the last month.
        percent_reporting_no_change : Optional[float]
            Percent of respondents reporting no change over the last month.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.manufacturing_outlook_texas(provider='fred')
        >>> obb.economy.survey.manufacturing_outlook_texas(topic='business_outlook,new_orders', transform='pc1', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/survey/manufacturing_outlook_texas",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.manufacturing_outlook_texas",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "topic": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "business_activity",
                                "business_outlook",
                                "capex",
                                "prices_paid",
                                "production",
                                "inventory",
                                "new_orders",
                                "new_orders_growth",
                                "unfilled_orders",
                                "shipments",
                                "delivery_time",
                                "employment",
                                "wages",
                                "hours_worked",
                            ],
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def nonfarm_payrolls(
        self,
        date: Annotated[
            Union[datetime.date, str, None, List[Union[datetime.date, str, None]]],
            OpenBBField(
                description="A specific date to get data for. Default is the latest report. Multiple comma separated items allowed for provider(s): fred."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get Nonfarm Payrolls Survey.

        Parameters
        ----------
        date : Union[date, str, None, List[Union[date, str, None]]]
            A specific date to get data for. Default is the latest report. Multiple comma separated items allowed for provider(s): fred.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        category : Literal['employees_nsa', 'employees_sa', 'employees_production_and_nonsupervisory', 'employees_women', 'employees_women_percent', 'avg_hours', 'avg_hours_production_and_nonsupervisory', 'avg_hours_overtime', 'avg_hours_overtime_production_and_nonsupervisory', 'avg_earnings_hourly', 'avg_earnings_hourly_production_and_nonsupervisory', 'avg_earnings_weekly', 'avg_earnings_weekly_production_and_nonsupervisory', 'index_weekly_hours', 'index_weekly_hours_production_and_nonsupervisory', 'index_weekly_payrolls', 'index_weekly_payrolls_production_and_nonsupervisory']
            The category to query. (provider: fred)

        Returns
        -------
        OBBject
            results : List[NonFarmPayrolls]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        NonFarmPayrolls
        ---------------
        date : date
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        value : float

        name : Optional[str]
            The name of the series. (provider: fred)
        element_id : Optional[str]
            The element id in the parent/child relationship. (provider: fred)
        parent_id : Optional[str]
            The parent id in the parent/child relationship. (provider: fred)
        children : Optional[str]
            The element_id of each child, as a comma-separated string. (provider: fred)
        level : Optional[int]
            The indentation level of the element. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.nonfarm_payrolls(provider='fred')
        >>> obb.economy.survey.nonfarm_payrolls(category='avg_hours', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/survey/nonfarm_payrolls",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.nonfarm_payrolls",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                info={
                    "date": {"fred": {"multiple_items_allowed": True, "choices": None}}
                },
            )
        )

    @exception_handler
    @validate
    def sloos(
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
        """Get Senior Loan Officers Opinion Survey.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        category : Literal['spreads', 'consumer', 'auto', 'credit_card', 'firms', 'mortgage', 'commercial_real_estate', 'standards', 'demand', 'foreign_banks']
            Category of survey response. (provider: fred)
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
            results : List[SeniorLoanOfficerSurvey]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SeniorLoanOfficerSurvey
        -----------------------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        value : float
            Survey value.
        title : Optional[str]
            Survey title.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.sloos(provider='fred')
        >>> obb.economy.survey.sloos(category='credit_card', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/survey/sloos",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.sloos",
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
    def university_of_michigan(
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
        """Get University of Michigan Consumer Sentiment and Inflation Expectations Surveys.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        frequency : Optional[Literal['annual', 'quarter']]
            Frequency aggregation to convert monthly data to lower frequency. None is monthly. (provider: fred)
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
            results : List[UniversityOfMichigan]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        UniversityOfMichigan
        --------------------
        date : date
            The date of the data.
        consumer_sentiment : Optional[float]
            Index of the results of the University of Michigan's monthly Survey of Consumers, which is used to estimate future spending and saving.  (1966:Q1=100).
        inflation_expectation : Optional[float]
            Median expected price change next 12 months, Surveys of Consumers.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.survey.university_of_michigan(provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/survey/university_of_michigan",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.survey.university_of_michigan",
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
