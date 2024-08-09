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
            Union[str, datetime.date, None, List[Union[str, datetime.date, None]]],
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
        date : Union[str, date, None, List[Union[str, date, None]]]
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
