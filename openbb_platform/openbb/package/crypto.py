### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Literal, Optional

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_crypto(Container):
    """/crypto
    /price
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import crypto_price

        return crypto_price.ROUTER_crypto_price(command_runner=self._command_runner)

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[
            Optional[str], OpenBBField(description="Search query.")
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Search available cryptocurrency pairs within a provider.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.
        query : Optional[str]
            Search query.

        Returns
        -------
        OBBject
            results : list[CryptoSearch]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CryptoSearch
        ------------
        symbol : str
            Symbol representing the entity requested in the data. (Crypto)
        name : Optional[str]
            Name of the crypto.
        currency : Optional[str]
            The currency the crypto trades for. (provider: fmp)
        exchange : Optional[str]
            The exchange code the crypto trades on. (provider: fmp)
        exchange_name : Optional[str]
            The short name of the exchange the crypto trades on. (provider: fmp)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.crypto.search(provider='fmp')
        >>> obb.crypto.search(query='BTCUSD', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/crypto/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "crypto.search",
                        ("fmp",),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
            )
        )
