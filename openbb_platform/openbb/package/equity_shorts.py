### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Literal, Optional

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_shorts(Container):
    """/equity/shorts
    fails_to_deliver
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def fails_to_deliver(
        self,
        symbol: Annotated[str, OpenBBField(description="Symbol to get data for.")],
        provider: Annotated[
            Optional[Literal["sec"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'sec' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get reported Fail-to-deliver (FTD) data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.
        limit : Optional[int]

                Limit the number of reports to parse, from most recent.
                Approximately 24 reports per year, going back to 2009.
                 (provider: sec)
        skip_reports : Optional[int]

                Skip N number of reports from current. A value of 1 will skip the most recent report.
                 (provider: sec)
        use_cache : Optional[bool]
            Whether or not to use cache for the request, default is True. Each reporting period is a separate URL, new reports will be added to the cache. (provider: sec)

        Returns
        -------
        OBBject
            results : List[EquityFTD]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityFTD
        ---------
        settlement_date : Optional[date]
            The settlement date of the fail.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        cusip : Optional[str]
            CUSIP of the Security.
        quantity : Optional[int]
            The number of fails on that settlement date.
        price : Optional[float]
            The price at the previous closing price from the settlement date.
        description : Optional[str]
            The description of the Security.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.shorts.fails_to_deliver(symbol='AAPL', provider='sec')
        """  # noqa: E501

        return self._run(
            "/equity/shorts/fails_to_deliver",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/shorts/fails_to_deliver",
                        ("sec",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
