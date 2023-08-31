### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class CLASS_futures(Container):
    """/futures
    curve
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def curve(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(description="Historical date to search curve for."),
        ] = None,
        chart: bool = False,
        provider: Optional[Literal["yfinance"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Futures Historical Price.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        date : Optional[datetime.date]
            Historical date to search curve for.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'yfinance' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[FuturesCurve]
                Serializable results.
            provider : Optional[Literal['yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        FuturesCurve
        ------------
        expiration : Optional[str]
            Futures expiration month.
        price : Optional[float]
            The close price of the symbol."""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "date": date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/futures/curve",
            **inputs,
        )
