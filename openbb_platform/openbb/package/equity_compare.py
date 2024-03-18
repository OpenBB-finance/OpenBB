### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Literal, Optional

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_compare(Container):
    """/equity/compare
    groups
    peers
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def groups(
        self,
        group: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider."
            ),
        ] = None,
        metric: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["finviz"]],
            OpenBBCustomParameter(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'finviz' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get company data grouped by sector, industry or country and display either performance or valuation metrics.

        Valuation metrics include price to earnings, price to book, price to sales ratios and price to cash flow.
        Performance metrics include the stock price change for different time periods.

        Parameters
        ----------
        group : Optional[str]
            The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider.
        metric : Optional[str]
            The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider.
        provider : Optional[Literal['finviz']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'finviz' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[CompareGroups]
                Serializable results.
            provider : Optional[Literal['finviz']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompareGroups
        -------------
        name : str
            Name or label of the group.
        stocks : Optional[int]
            The number of stocks in the group. (provider: finviz)
        market_cap : Optional[int]
            The market cap of the group. (provider: finviz)
        performance_1_d : Optional[float]
            The performance in the last day, as a normalized percent. (provider: finviz)
        performance_1_w : Optional[float]
            The performance in the last week, as a normalized percent. (provider: finviz)
        performance_1_m : Optional[float]
            The performance in the last month, as a normalized percent. (provider: finviz)
        performance_3_m : Optional[float]
            The performance in the last quarter, as a normalized percent. (provider: finviz)
        performance_6_m : Optional[float]
            The performance in the last half year, as a normalized percent. (provider: finviz)
        performance_1_y : Optional[float]
            The performance in the last year, as a normalized percent. (provider: finviz)
        performance_ytd : Optional[float]
            The performance in the year to date, as a normalized percent. (provider: finviz)
        dividend_yield : Optional[float]
            The dividend yield of the group, as a normalized percent. (provider: finviz)
        pe : Optional[float]
            The P/E ratio of the group. (provider: finviz)
        forward_pe : Optional[float]
            The forward P/E ratio of the group. (provider: finviz)
        peg : Optional[float]
            The PEG ratio of the group. (provider: finviz)
        eps_growth_past_5_years : Optional[float]
            The EPS growth of the group for the past 5 years, as a normalized percent. (provider: finviz)
        eps_growth_next_5_years : Optional[float]
            The estimated EPS growth of the groupo for the next 5 years, as a normalized percent. (provider: finviz)
        sales_growth_past_5_years : Optional[float]
            The sales growth of the group for the past 5 years, as a normalized percent. (provider: finviz)
        float_short : Optional[float]
            The percent of the float shorted for the group, as a normalized value. (provider: finviz)
        analyst_recommendation : Optional[float]
            The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell. (provider: finviz)
        volume : Optional[int]
            The trading volume. (provider: finviz)
        volume_average : Optional[int]
            The 3-month average volume of the group. (provider: finviz)
        volume_relative : Optional[float]
            The relative volume compared to the 3-month average volume. (provider: finviz)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.compare.groups(provider='finviz')
        >>> # Group by sector and analyze valuation.
        >>> obb.equity.compare.groups(group='sector', metric='valuation', provider='finviz')
        >>> # Group by industry and analyze performance.
        >>> obb.equity.compare.groups(group='industry', metric='performance', provider='finviz')
        >>> # Group by country and analyze valuation.
        >>> obb.equity.compare.groups(group='country', metric='valuation', provider='finviz')
        """  # noqa: E501

        return self._run(
            "/equity/compare/groups",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/compare/groups",
                        ("finviz",),
                    )
                },
                standard_params={
                    "group": group,
                    "metric": metric,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def peers(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBCustomParameter(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the closest peers for a given company.

        Peers consist of companies trading on the same exchange, operating within the same sector
        and with comparable market capitalizations.

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
            results : EquityPeers
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityPeers
        -----------
        peers_list : List[str]
            A list of equity peers based on sector, exchange and market cap.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.compare.peers(symbol='AAPL', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/compare/peers",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/compare/peers",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
