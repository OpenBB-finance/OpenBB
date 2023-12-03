### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
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
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[Data]:
        """Price Target Consensus. Price target consensus data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : PriceTargetConsensus
                Serializable results.
            provider : Optional[Literal['fmp']]
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.estimates.consensus(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/estimates/consensus",
            **inputs,
        )

    @validate
    def historical(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
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
    ) -> OBBject[List[Data]]:
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/estimates/historical",
            **inputs,
        )

    @validate
    def price_target(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Price Target. Price target data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_grade : bool
            Include upgrades and downgrades in the response. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[PriceTarget]
                Serializable results.
            provider : Optional[Literal['fmp']]
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
        new_grade : Optional[str]
            New grade (provider: fmp)
        previous_grade : Optional[str]
            Previous grade (provider: fmp)
        grading_company : Optional[str]
            Grading company (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.estimates.price_target(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/estimates/price_target",
            **inputs,
        )
