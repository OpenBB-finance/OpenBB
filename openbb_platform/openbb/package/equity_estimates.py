### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_estimates(Container):
    """/equity/estimates
    analyst_search
    consensus
    forward_eps
    forward_sales
    historical
    price_target
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def analyst_search(
        self,
        analyst_name: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Analyst names to return. Omitting will return all available analysts. Multiple comma separated items allowed for provider(s): benzinga."
            ),
        ] = None,
        firm_name: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Firm names to return. Omitting will return all available firms. Multiple comma separated items allowed for provider(s): benzinga."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["benzinga"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'benzinga' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Search for specific analysts and get their forecast track record.

        Parameters
        ----------
        analyst_name : Union[str, None, List[Optional[str]]]
            Analyst names to return. Omitting will return all available analysts. Multiple comma separated items allowed for provider(s): benzinga.
        firm_name : Union[str, None, List[Optional[str]]]
            Firm names to return. Omitting will return all available firms. Multiple comma separated items allowed for provider(s): benzinga.
        provider : Optional[Literal['benzinga']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        analyst_ids : Optional[str]
            List of analyst IDs to return. Multiple comma separated items allowed. (provider: benzinga)
        firm_ids : Optional[str]
            Firm IDs to return. Multiple comma separated items allowed. (provider: benzinga)
        limit : Optional[int]
            Number of results returned. Limit 1000. (provider: benzinga)
        page : Optional[int]
            Page offset. For optimization, performance and technical reasons, page offsets are limited from 0 - 100000. Limit the query results by other parameters such as date. (provider: benzinga)
        fields : Optional[str]
            Fields to include in the response. See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields. Multiple comma separated items allowed. (provider: benzinga)

        Returns
        -------
        OBBject
            results : List[AnalystSearch]
                Serializable results.
            provider : Optional[Literal['benzinga']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        AnalystSearch
        -------------
        last_updated : Optional[datetime]
            Date of the last update.
        firm_name : Optional[str]
            Firm name of the analyst.
        name_first : Optional[str]
            Analyst first name.
        name_last : Optional[str]
            Analyst last name.
        name_full : str
            Analyst full name.
        analyst_id : Optional[str]
            ID of the analyst. (provider: benzinga)
        firm_id : Optional[str]
            ID of the analyst firm. (provider: benzinga)
        smart_score : Optional[float]
            A weighted average of the total_ratings_percentile, overall_avg_return_percentile, and overall_success_rate (provider: benzinga)
        overall_success_rate : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain overall. (provider: benzinga)
        overall_avg_return_percentile : Optional[float]
            The percentile (normalized) of this analyst's overall average return per rating in comparison to other analysts' overall average returns per rating. (provider: benzinga)
        total_ratings_percentile : Optional[float]
            The percentile (normalized) of this analyst's total number of ratings in comparison to the total number of ratings published by all other analysts (provider: benzinga)
        total_ratings : Optional[int]
            Number of recommendations made by this analyst. (provider: benzinga)
        overall_gain_count : Optional[int]
            The number of ratings that have gained value since the date of recommendation (provider: benzinga)
        overall_loss_count : Optional[int]
            The number of ratings that have lost value since the date of recommendation (provider: benzinga)
        overall_average_return : Optional[float]
            The average percent (normalized) price difference per rating since the date of recommendation (provider: benzinga)
        overall_std_dev : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings since the date of recommendation (provider: benzinga)
        gain_count_1m : Optional[int]
            The number of ratings that have gained value over the last month (provider: benzinga)
        loss_count_1m : Optional[int]
            The number of ratings that have lost value over the last month (provider: benzinga)
        average_return_1m : Optional[float]
            The average percent (normalized) price difference per rating over the last month (provider: benzinga)
        std_dev_1m : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last month (provider: benzinga)
        smart_score_1m : Optional[float]
            A weighted average smart score over the last month. (provider: benzinga)
        success_rate_1m : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last month (provider: benzinga)
        gain_count_3m : Optional[int]
            The number of ratings that have gained value over the last 3 months (provider: benzinga)
        loss_count_3m : Optional[int]
            The number of ratings that have lost value over the last 3 months (provider: benzinga)
        average_return_3m : Optional[float]
            The average percent (normalized) price difference per rating over the last 3 months (provider: benzinga)
        std_dev_3m : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 3 months (provider: benzinga)
        smart_score_3m : Optional[float]
            A weighted average smart score over the last 3 months. (provider: benzinga)
        success_rate_3m : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last 3 months (provider: benzinga)
        gain_count_6m : Optional[int]
            The number of ratings that have gained value over the last 6 months (provider: benzinga)
        loss_count_6m : Optional[int]
            The number of ratings that have lost value over the last 6 months (provider: benzinga)
        average_return_6m : Optional[float]
            The average percent (normalized) price difference per rating over the last 6 months (provider: benzinga)
        std_dev_6m : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 6 months (provider: benzinga)
        gain_count_9m : Optional[int]
            The number of ratings that have gained value over the last 9 months (provider: benzinga)
        loss_count_9m : Optional[int]
            The number of ratings that have lost value over the last 9 months (provider: benzinga)
        average_return_9m : Optional[float]
            The average percent (normalized) price difference per rating over the last 9 months (provider: benzinga)
        std_dev_9m : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 9 months (provider: benzinga)
        smart_score_9m : Optional[float]
            A weighted average smart score over the last 9 months. (provider: benzinga)
        success_rate_9m : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last 9 months (provider: benzinga)
        gain_count_1y : Optional[int]
            The number of ratings that have gained value over the last 1 year (provider: benzinga)
        loss_count_1y : Optional[int]
            The number of ratings that have lost value over the last 1 year (provider: benzinga)
        average_return_1y : Optional[float]
            The average percent (normalized) price difference per rating over the last 1 year (provider: benzinga)
        std_dev_1y : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 1 year (provider: benzinga)
        smart_score_1y : Optional[float]
            A weighted average smart score over the last 1 year. (provider: benzinga)
        success_rate_1y : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last 1 year (provider: benzinga)
        gain_count_2y : Optional[int]
            The number of ratings that have gained value over the last 2 years (provider: benzinga)
        loss_count_2y : Optional[int]
            The number of ratings that have lost value over the last 2 years (provider: benzinga)
        average_return_2y : Optional[float]
            The average percent (normalized) price difference per rating over the last 2 years (provider: benzinga)
        std_dev_2y : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 2 years (provider: benzinga)
        smart_score_2y : Optional[float]
            A weighted average smart score over the last 3 years. (provider: benzinga)
        success_rate_2y : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last 2 years (provider: benzinga)
        gain_count_3y : Optional[int]
            The number of ratings that have gained value over the last 3 years (provider: benzinga)
        loss_count_3y : Optional[int]
            The number of ratings that have lost value over the last 3 years (provider: benzinga)
        average_return_3y : Optional[float]
            The average percent (normalized) price difference per rating over the last 3 years (provider: benzinga)
        std_dev_3y : Optional[float]
            The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 3 years (provider: benzinga)
        smart_score_3y : Optional[float]
            A weighted average smart score over the last 3 years. (provider: benzinga)
        success_rate_3y : Optional[float]
            The percentage (normalized) of gain/loss ratings that resulted in a gain over the last 3 years (provider: benzinga)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.analyst_search(provider='benzinga')
        >>> obb.equity.estimates.analyst_search(firm_name='Wedbush', provider='benzinga')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/analyst_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/analyst_search",
                        ("benzinga",),
                    )
                },
                standard_params={
                    "analyst_name": analyst_name,
                    "firm_name": firm_name,
                },
                extra_params=kwargs,
                info={
                    "analyst_name": {"multiple_items_allowed": ["benzinga"]},
                    "firm_name": {"multiple_items_allowed": ["benzinga"]},
                    "analyst_ids": {"multiple_items_allowed": ["benzinga"]},
                    "firm_ids": {"multiple_items_allowed": ["benzinga"]},
                    "fields": {"multiple_items_allowed": ["benzinga"]},
                },
            )
        )

    @exception_handler
    @validate
    def consensus(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "yfinance"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get consensus price target and recommendation.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio, yfinance.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        industry_group_number : Optional[int]
            The Zacks industry group number. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[PriceTargetConsensus]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PriceTargetConsensus
        --------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            The company name
        target_high : Optional[float]
            High target of the price target consensus.
        target_low : Optional[float]
            Low target of the price target consensus.
        target_consensus : Optional[float]
            Consensus target of the price target consensus.
        target_median : Optional[float]
            Median target of the price target consensus.
        standard_deviation : Optional[float]
            The standard deviation of target price estimates. (provider: intrinio)
        total_anaylsts : Optional[int]
            The total number of target price estimates in consensus. (provider: intrinio)
        raised : Optional[int]
            The number of analysts that have raised their target price estimates. (provider: intrinio)
        lowered : Optional[int]
            The number of analysts that have lowered their target price estimates. (provider: intrinio)
        most_recent_date : Optional[date]
            The date of the most recent estimate. (provider: intrinio)
        industry_group_number : Optional[int]
            The Zacks industry group number. (provider: intrinio)
        recommendation : Optional[str]
            Recommendation - buy, sell, etc. (provider: yfinance)
        recommendation_mean : Optional[float]
            Mean recommendation score where 1 is strong buy and 5 is strong sell. (provider: yfinance)
        number_of_analysts : Optional[int]
            Number of analysts providing opinions. (provider: yfinance)
        current_price : Optional[float]
            Current price of the stock. (provider: yfinance)
        currency : Optional[str]
            Currency the stock is priced in. (provider: yfinance)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.consensus(symbol='AAPL', provider='fmp')
        >>> obb.equity.estimates.consensus(symbol='AAPL,MSFT', provider='yfinance')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/consensus",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/consensus",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "multiple_items_allowed": ["fmp", "intrinio", "yfinance"]
                    }
                },
            )
        )

    @exception_handler
    @validate
    def forward_eps(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get forward EPS estimates.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, intrinio.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        fiscal_period : Optional[Union[Literal['annual', 'quarter'], Literal['fy', 'q1', 'q2', 'q3', 'q4']]]
            The future fiscal period to retrieve estimates for. (provider: fmp, intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: fmp)
        include_historical : bool
            If True, the data will include all past data and the limit will be ignored. (provider: fmp)
        fiscal_year : Optional[int]
            The future fiscal year to retrieve estimates for. When no symbol and year is supplied the current calendar year is used. (provider: intrinio)
        calendar_year : Optional[int]
            The future calendar year to retrieve estimates for. When no symbol and year is supplied the current calendar year is used. (provider: intrinio)
        calendar_period : Optional[Literal['q1', 'q2', 'q3', 'q4']]
            The future calendar period to retrieve estimates for. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[ForwardEpsEstimates]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ForwardEpsEstimates
        -------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        date : date
            The date of the data.
        fiscal_year : Optional[int]
            Fiscal year for the estimate.
        fiscal_period : Optional[str]
            Fiscal quarter for the estimate.
        calendar_year : Optional[int]
            Calendar year for the estimate.
        calendar_period : Optional[str]
            Calendar quarter for the estimate.
        low_estimate : Optional[float]
            Estimated EPS low for the period.
        high_estimate : Optional[float]
            Estimated EPS high for the period.
        mean : Optional[float]
            Estimated EPS mean for the period.
        median : Optional[float]
            Estimated EPS median for the period.
        standard_deviation : Optional[float]
            Estimated EPS standard deviation for the period.
        number_of_analysts : Optional[int]
            Number of analysts providing estimates for the period.
        revisions_change_percent : Optional[float]
            The earnings per share (EPS) percent change in estimate for the period. (provider: intrinio)
        mean_1w : Optional[float]
            The mean estimate for the period one week ago. (provider: intrinio)
        mean_1m : Optional[float]
            The mean estimate for the period one month ago. (provider: intrinio)
        mean_2m : Optional[float]
            The mean estimate for the period two months ago. (provider: intrinio)
        mean_3m : Optional[float]
            The mean estimate for the period three months ago. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.forward_eps(symbol='AAPL', provider='intrinio')
        >>> obb.equity.estimates.forward_eps(fiscal_year=2025, fiscal_period='fy', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/forward_eps",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/forward_eps",
                        ("fmp", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp", "intrinio"]}},
            )
        )

    @exception_handler
    @validate
    def forward_sales(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): intrinio."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'intrinio' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get forward sales estimates.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): intrinio.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        fiscal_year : Optional[int]
            The future fiscal year to retrieve estimates for. When no symbol and year is supplied the current calendar year is used. (provider: intrinio)
        fiscal_period : Optional[Literal['fy', 'q1', 'q2', 'q3', 'q4']]
            The future fiscal period to retrieve estimates for. (provider: intrinio)
        calendar_year : Optional[int]
            The future calendar year to retrieve estimates for. When no symbol and year is supplied the current calendar year is used. (provider: intrinio)
        calendar_period : Optional[Literal['q1', 'q2', 'q3', 'q4']]
            The future calendar period to retrieve estimates for. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[ForwardSalesEstimates]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ForwardSalesEstimates
        ---------------------
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        date : date
            The date of the data.
        fiscal_year : Optional[int]
            Fiscal year for the estimate.
        fiscal_period : Optional[str]
            Fiscal quarter for the estimate.
        calendar_year : Optional[int]
            Calendar year for the estimate.
        calendar_period : Optional[str]
            Calendar quarter for the estimate.
        low_estimate : Optional[int]
            The sales estimate low for the period.
        high_estimate : Optional[int]
            The sales estimate high for the period.
        mean : Optional[int]
            The sales estimate mean for the period.
        median : Optional[int]
            The sales estimate median for the period.
        standard_deviation : Optional[int]
            The sales estimate standard deviation for the period.
        number_of_analysts : Optional[int]
            Number of analysts providing estimates for the period.
        revisions_1w_up : Optional[int]
            Number of revisions up in the last week. (provider: intrinio)
        revisions_1w_down : Optional[int]
            Number of revisions down in the last week. (provider: intrinio)
        revisions_1w_change_percent : Optional[float]
            The analyst revisions percent change in estimate for the period of 1 week. (provider: intrinio)
        revisions_1m_up : Optional[int]
            Number of revisions up in the last month. (provider: intrinio)
        revisions_1m_down : Optional[int]
            Number of revisions down in the last month. (provider: intrinio)
        revisions_1m_change_percent : Optional[float]
            The analyst revisions percent change in estimate for the period of 1 month. (provider: intrinio)
        revisions_3m_up : Optional[int]
            Number of revisions up in the last 3 months. (provider: intrinio)
        revisions_3m_down : Optional[int]
            Number of revisions down in the last 3 months. (provider: intrinio)
        revisions_3m_change_percent : Optional[float]
            The analyst revisions percent change in estimate for the period of 3 months. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.forward_sales(symbol='AAPL', provider='intrinio')
        >>> obb.equity.estimates.forward_sales(fiscal_year=2025, fiscal_period='fy', provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/forward_sales",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/forward_sales",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["intrinio"]}},
            )
        )

    @exception_handler
    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp."
            ),
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get historical analyst estimates for earnings and revenue.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        period : Literal['quarter', 'annual']
            Time period of the data to return. (provider: fmp)
        limit : Optional[int]
            The number of data entries to return. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[AnalystEstimates]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        AnalystEstimates
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        estimated_revenue_low : Optional[int]
            Estimated revenue low.
        estimated_revenue_high : Optional[int]
            Estimated revenue high.
        estimated_revenue_avg : Optional[int]
            Estimated revenue average.
        estimated_sga_expense_low : Optional[int]
            Estimated SGA expense low.
        estimated_sga_expense_high : Optional[int]
            Estimated SGA expense high.
        estimated_sga_expense_avg : Optional[int]
            Estimated SGA expense average.
        estimated_ebitda_low : Optional[int]
            Estimated EBITDA low.
        estimated_ebitda_high : Optional[int]
            Estimated EBITDA high.
        estimated_ebitda_avg : Optional[int]
            Estimated EBITDA average.
        estimated_ebit_low : Optional[int]
            Estimated EBIT low.
        estimated_ebit_high : Optional[int]
            Estimated EBIT high.
        estimated_ebit_avg : Optional[int]
            Estimated EBIT average.
        estimated_net_income_low : Optional[int]
            Estimated net income low.
        estimated_net_income_high : Optional[int]
            Estimated net income high.
        estimated_net_income_avg : Optional[int]
            Estimated net income average.
        estimated_eps_avg : Optional[float]
            Estimated EPS average.
        estimated_eps_high : Optional[float]
            Estimated EPS high.
        estimated_eps_low : Optional[float]
            Estimated EPS low.
        number_analyst_estimated_revenue : Optional[int]
            Number of analysts who estimated revenue.
        number_analysts_estimated_eps : Optional[int]
            Number of analysts who estimated EPS.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.historical(symbol='AAPL', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/historical",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/historical",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def price_target(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp."
            ),
        ] = None,
        limit: Annotated[
            int, OpenBBField(description="The number of data entries to return.")
        ] = 200,
        provider: Annotated[
            Optional[Literal["benzinga", "fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'benzinga' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get analyst price targets by company.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['benzinga', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        page : Optional[int]
            Page offset. For optimization, performance and technical reasons, page offsets are limited from 0 - 100000. Limit the query results by other parameters such as date. Used in conjunction with the limit and date parameters. (provider: benzinga)
        date : Optional[datetime.date]
            Date for calendar data, shorthand for date_from and date_to. (provider: benzinga)
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format. (provider: benzinga)
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format. (provider: benzinga)
        updated : Optional[Union[datetime.date, int]]
            Records last Updated Unix timestamp (UTC). This will force the sort order to be Greater Than or Equal to the timestamp indicated. The date can be a date string or a Unix timestamp. The date string must be in the format of YYYY-MM-DD. (provider: benzinga)
        importance : Optional[int]
            Importance level to filter by. Uses Greater Than or Equal To the importance indicated (provider: benzinga)
        action : Optional[Literal['downgrades', 'maintains', 'reinstates', 'reiterates', 'upgrades', 'assumes', 'initiates', 'terminates', 'removes', 'suspends', 'firm_dissolved']]
            Filter by a specific action_company. (provider: benzinga)
        analyst_ids : Optional[Union[List[str], str]]
            Comma-separated list of analyst (person) IDs. Omitting will bring back all available analysts. (provider: benzinga)
        firm_ids : Optional[Union[List[str], str]]
            Comma-separated list of firm IDs. (provider: benzinga)
        fields : Optional[Union[List[str], str]]
            Comma-separated list of fields to include in the response. See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields. (provider: benzinga)
        with_grade : bool
            Include upgrades and downgrades in the response. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[PriceTarget]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PriceTarget
        -----------
        published_date : Union[date, datetime]
            Published date of the price target.
        published_time : Optional[datetime.time]
            Time of the original rating, UTC.
        symbol : str
            Symbol representing the entity requested in the data.
        exchange : Optional[str]
            Exchange where the company is traded.
        company_name : Optional[str]
            Name of company that is the subject of rating.
        analyst_name : Optional[str]
            Analyst name.
        analyst_firm : Optional[str]
            Name of the analyst firm that published the price target.
        currency : Optional[str]
            Currency the data is denominated in.
        price_target : Optional[float]
            The current price target.
        adj_price_target : Optional[float]
            Adjusted price target for splits and stock dividends.
        price_target_previous : Optional[float]
            Previous price target.
        previous_adj_price_target : Optional[float]
            Previous adjusted price target.
        price_when_posted : Optional[float]
            Price when posted.
        rating_current : Optional[str]
            The analyst's rating for the company.
        rating_previous : Optional[str]
            Previous analyst rating for the company.
        action : Optional[str]
            Description of the change in rating from firm's last rating.
        action_change : Optional[Literal['Announces', 'Maintains', 'Lowers', 'Raises', 'Removes', 'Adjusts']]
            Description of the change in price target from firm's last price target. (provider: benzinga)
        importance : Optional[Literal[0, 1, 2, 3, 4, 5]]
            Subjective Basis of How Important Event is to Market. 5 = High (provider: benzinga)
        notes : Optional[str]
            Notes of the price target. (provider: benzinga)
        analyst_id : Optional[str]
            Id of the analyst. (provider: benzinga)
        url_news : Optional[str]
            URL for analyst ratings news articles for this ticker on Benzinga.com. (provider: benzinga)
        url_analyst : Optional[str]
            URL for analyst ratings page for this ticker on Benzinga.com. (provider: benzinga)
        id : Optional[str]
            Unique ID of this entry. (provider: benzinga)
        last_updated : Optional[datetime]
            Last updated timestamp, UTC. (provider: benzinga)
        news_url : Optional[str]
            News URL of the price target. (provider: fmp)
        news_title : Optional[str]
            News title of the price target. (provider: fmp)
        news_publisher : Optional[str]
            News publisher of the price target. (provider: fmp)
        news_base_url : Optional[str]
            News base URL of the price target. (provider: fmp)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.estimates.price_target(provider='benzinga')
        >>> # Get price targets for Microsoft using 'benzinga' as provider.
        >>> obb.equity.estimates.price_target(start_date='2020-01-01', end_date='2024-02-16', limit=10, symbol='msft', provider='benzinga', action='downgrades')
        """  # noqa: E501

        return self._run(
            "/equity/estimates/price_target",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/price_target",
                        ("benzinga", "fmp"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "limit": limit,
                },
                extra_params=kwargs,
                info={"symbol": {"multiple_items_allowed": ["benzinga", "fmp"]}},
            )
        )
