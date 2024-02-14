### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_estimates(Container):
    """/equity/estimates
    consensus
    historical
    price_target
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def consensus(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: yfinance."
            ),
        ],
        provider: Optional[Literal["fmp", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Price Target Consensus. Price target consensus data.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: yfinance.
        provider : Optional[Literal['fmp', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[PriceTargetConsensus], PriceTargetConsensus]
                Serializable results.
            provider : Optional[Literal['fmp', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PriceTargetConsensus
        --------------------
        symbol : str
            Symbol representing the entity requested in the data.
        target_high : Optional[float]
            High target of the price target consensus.
        target_low : Optional[float]
            Low target of the price target consensus.
        target_consensus : Optional[float]
            Consensus target of the price target consensus.
        target_median : Optional[float]
            Median target of the price target consensus.
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.estimates.consensus(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/estimates/consensus",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/estimates/consensus",
                        ("fmp", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["yfinance"]}},
            )
        )

    @validate
    def historical(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 30,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Historical Analyst Estimates. Analyst stock recommendations.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Literal['quarter', 'annual']
            Time period of the data to return.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

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
            extra: Dict[str, Any]
                Extra info.

        AnalystEstimates
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        estimated_revenue_low : int
            Estimated revenue low.
        estimated_revenue_high : int
            Estimated revenue high.
        estimated_revenue_avg : int
            Estimated revenue average.
        estimated_ebitda_low : int
            Estimated EBITDA low.
        estimated_ebitda_high : int
            Estimated EBITDA high.
        estimated_ebitda_avg : int
            Estimated EBITDA average.
        estimated_ebit_low : int
            Estimated EBIT low.
        estimated_ebit_high : int
            Estimated EBIT high.
        estimated_ebit_avg : int
            Estimated EBIT average.
        estimated_net_income_low : int
            Estimated net income low.
        estimated_net_income_high : int
            Estimated net income high.
        estimated_net_income_avg : int
            Estimated net income average.
        estimated_sga_expense_low : int
            Estimated SGA expense low.
        estimated_sga_expense_high : int
            Estimated SGA expense high.
        estimated_sga_expense_avg : int
            Estimated SGA expense average.
        estimated_eps_avg : float
            Estimated EPS average.
        estimated_eps_high : float
            Estimated EPS high.
        estimated_eps_low : float
            Estimated EPS low.
        number_analyst_estimated_revenue : int
            Number of analysts who estimated revenue.
        number_analysts_estimated_eps : int
            Number of analysts who estimated EPS.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.estimates.historical(symbol="AAPL", period="annual", limit=30)
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
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def price_target(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: benzinga."
            ),
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["benzinga", "fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Price Target. Price target data.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: benzinga.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['benzinga', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        fields : Optional[str]
            Comma-separated list of fields to include in the response. See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields. (provider: benzinga)
        date : Optional[str]
            Date for calendar data, shorthand for date_from and date_to. (provider: benzinga)
        date_from : Optional[str]
            Date to query from point in time. (provider: benzinga)
        date_to : Optional[str]
            Date to query to point in time. (provider: benzinga)
        importance : Optional[int]
            Importance level to filter by. (provider: benzinga)
        updated : Optional[int]
            Records last updated Unix timestamp (UTC). (provider: benzinga)
        action : Optional[Literal['Downgrades', 'Maintains', 'Reinstates', 'Reiterates', 'Upgrades', 'Assumes', 'Initiates Coverage On', 'Terminates Coverage On', 'Removes', 'Suspends', 'Firm Dissolved']]
            Filter by a specific action_company. (provider: benzinga)
        analyst : Optional[str]
            Comma-separated list of analyst (person) IDs. (provider: benzinga)
        firm : Optional[str]
            Comma-separated list of analyst firm IDs. (provider: benzinga)
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
            extra: Dict[str, Any]
                Extra info.

        PriceTarget
        -----------
        symbol : str
            Symbol representing the entity requested in the data.
        published_date : datetime
            Published date of the price target.
        news_url : Optional[str]
            News URL of the price target.
        news_title : Optional[str]
            News title of the price target.
        analyst_name : Optional[str]
            Analyst name.
        analyst_company : Optional[str]
            Analyst company.
        price_target : Optional[float]
            Price target.
        adj_price_target : Optional[float]
            Adjusted price target.
        price_when_posted : Optional[float]
            Price when posted.
        news_publisher : Optional[str]
            News publisher of the price target.
        news_base_url : Optional[str]
            News base URL of the price target.
        action_company : Optional[Literal['Downgrades', 'Maintains', 'Reinstates', 'Reiterates', 'Upgrades', 'Assumes', 'Initiates Coverage On', 'Terminates Coverage On', 'Removes', 'Suspends', 'Firm Dissolved', '']]
            Description of the change in rating from firm's last rating.Note that all of these terms are precisely defined. (provider: benzinga)
        action_pt : Optional[Literal['Announces', 'Maintains', 'Lowers', 'Raises', 'Removes', 'Adjusts', '']]
            Description of the change in price target from firm's last price target. (provider: benzinga)
        adjusted_pt_prior : Optional[str]
            Analyst's prior price target, adjusted to account for stock splits and stock dividends. If none are applicable, the pt_prior value is used. (provider: benzinga)
        analyst_id : Optional[str]
            Id of the analyst. (provider: benzinga)
        currency : Optional[str]
            Currency the data is denominated in. (provider: benzinga)
        exchange : Optional[str]
            Exchange of the price target. (provider: benzinga)
        id : Optional[str]
            Unique ID of this entry. (provider: benzinga)
        importance : Optional[Literal[0, 1, 2, 3, 4, 5]]
            Subjective Basis of How Important Event is to Market. 5 = High (provider: benzinga)
        notes : Optional[str]
            Notes of the price target. (provider: benzinga)
        pt_prior : Optional[str]
            Analyst's prior price target. (provider: benzinga)
        rating_current : Optional[str]
            The analyst's rating for the company. (provider: benzinga)
        rating_prior : Optional[str]
            Prior analyst rating for the company. (provider: benzinga)
        ratings_accuracy : Optional[str]
            Ratings accuracy of the price target. (provider: benzinga)
        time : Optional[str]
            Last updated timestamp, UTC. (provider: benzinga)
        updated : Optional[int]
            Last updated timestamp, UTC. (provider: benzinga)
        url : Optional[str]
            URL for analyst ratings page for this ticker on Benzinga.com. (provider: benzinga)
        url_calendar : Optional[str]
            URL for analyst ratings page for this ticker on Benzinga.com. (provider: benzinga)
        name : Optional[str]
            Name of company that is subject of rating. (provider: benzinga)
        new_grade : Optional[str]
            New grade (provider: fmp)
        previous_grade : Optional[str]
            Previous grade (provider: fmp)
        grading_company : Optional[str]
            Grading company (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.estimates.price_target(symbol="AAPL", limit=100)
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
                extra_info={"symbol": {"multiple_items_allowed": ["benzinga"]}},
            )
        )
