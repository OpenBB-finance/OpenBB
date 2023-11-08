### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_crypto(Container):
    """/crypto
    /price
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def price(self):  # route = "/crypto/price"
        from . import crypto_price

        return crypto_price.ROUTER_crypto_price(command_runner=self._command_runner)

    @validate
    def search(
        self,
        query: typing_extensions.Annotated[
            Union[str, None], OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Cryptocurrency Search. Search available cryptocurrency pairs.

        Parameters
        ----------
        query : Union[str, None]
            Search query.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[CryptoSearch]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CryptoSearch
        ------------
        symbol : str
            Symbol representing the entity requested in the data. (Crypto)
        name : Optional[Union[str]]
            Name of the crypto.
        currency : Optional[Union[str]]
            The currency the crypto trades for. (provider: fmp)
        exchange : Optional[Union[str]]
            The exchange code the crypto trades on. (provider: fmp)
        exchange_name : Optional[Union[str]]
            The short name of the exchange the crypto trades on. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.crypto.search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/crypto/search",
            **inputs,
        )
