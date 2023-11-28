### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_equity_darkpool(Container):
    """/equity/darkpool
    otc
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def otc(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
        provider: Optional[Literal["finra"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Weekly aggregate trade data for Over The Counter deals.

            ATS and non-ATS trading data for each ATS/firm
            with trade reporting obligations under FINRA rules.


        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['finra']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'finra' if there is
            no default.
        tier : Literal['T1', 'T2', 'OTCE']
            "T1 - Securities included in the S&P 500, Russell 1000 and selected exchange-traded products;
                T2 - All other NMS stocks; OTC - Over-the-Counter equity securities (provider: finra)
        is_ats : bool
            ATS data if true, NON-ATS otherwise (provider: finra)

        Returns
        -------
        OBBject
            results : List[OTCAggregate]
                Serializable results.
            provider : Optional[Literal['finra']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        OTCAggregate
        ------------
        update_date : date
            Most recent date on which total trades is updated based on data received from each ATS/OTC.
        share_quantity : float
            Aggregate weekly total number of shares reported by each ATS for the Symbol.
        trade_quantity : float
            Aggregate weekly total number of trades reported by each ATS for the Symbol

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.darkpool.otc()
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
            "/equity/darkpool/otc",
            **inputs,
        )
