### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_etf_discovery(Container):
    """/etf/discovery
    active
    gainers
    losers
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def active(
        self,
        sort: Annotated[
            str,
            OpenBBCustomParameter(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Optional[Literal["wsj"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the most active ETFs.

        Parameters
        ----------
        sort : str
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['wsj']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'wsj' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[ETFActive]
                Serializable results.
            provider : Optional[Literal['wsj']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ETFActive
        ---------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the entity.
        last_price : float
            Last price.
        percent_change : float
            Percent change.
        net_change : float
            Net change.
        volume : float
            The trading volume.
        date : date
            The date of the data.
        country : Optional[str]
            Country of the entity. (provider: wsj)
        mantissa : Optional[int]
            Mantissa. (provider: wsj)
        type : Optional[str]
            Type of the entity. (provider: wsj)
        formatted_price : Optional[str]
            Formatted price. (provider: wsj)
        formatted_volume : Optional[str]
            Formatted volume. (provider: wsj)
        formatted_price_change : Optional[str]
            Formatted price change. (provider: wsj)
        formatted_percent_change : Optional[str]
            Formatted percent change. (provider: wsj)
        url : Optional[str]
            The source url. (provider: wsj)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.discovery.active(sort="desc", limit=10)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "sort": sort,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/etf/discovery/active",
            **inputs,
        )

    @validate
    def gainers(
        self,
        sort: Annotated[
            str,
            OpenBBCustomParameter(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Optional[Literal["wsj"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the top ETF gainers.

        Parameters
        ----------
        sort : str
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['wsj']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'wsj' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[ETFGainers]
                Serializable results.
            provider : Optional[Literal['wsj']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ETFGainers
        ----------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the entity.
        last_price : float
            Last price.
        percent_change : float
            Percent change.
        net_change : float
            Net change.
        volume : float
            The trading volume.
        date : date
            The date of the data.
        bluegrass_channel : Optional[str]
            Bluegrass channel. (provider: wsj)
        country : Optional[str]
            Country of the entity. (provider: wsj)
        mantissa : Optional[int]
            Mantissa. (provider: wsj)
        type : Optional[str]
            Type of the entity. (provider: wsj)
        formatted_price : Optional[str]
            Formatted price. (provider: wsj)
        formatted_volume : Optional[str]
            Formatted volume. (provider: wsj)
        formatted_price_change : Optional[str]
            Formatted price change. (provider: wsj)
        formatted_percent_change : Optional[str]
            Formatted percent change. (provider: wsj)
        url : Optional[str]
            The source url. (provider: wsj)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.discovery.gainers(sort="desc", limit=10)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "sort": sort,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/etf/discovery/gainers",
            **inputs,
        )

    @validate
    def losers(
        self,
        sort: Annotated[
            str,
            OpenBBCustomParameter(
                description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'."
            ),
        ] = "desc",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Optional[Literal["wsj"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get the top ETF losers.

        Parameters
        ----------
        sort : str
            Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['wsj']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'wsj' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[ETFLosers]
                Serializable results.
            provider : Optional[Literal['wsj']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ETFLosers
        ---------
        symbol : str
            Symbol representing the entity requested in the data.
        name : str
            Name of the entity.
        last_price : float
            Last price.
        percent_change : float
            Percent change.
        net_change : float
            Net change.
        volume : float
            The trading volume.
        date : date
            The date of the data.
        bluegrass_channel : Optional[str]
            Bluegrass channel. (provider: wsj)
        country : Optional[str]
            Country of the entity. (provider: wsj)
        mantissa : Optional[int]
            Mantissa. (provider: wsj)
        type : Optional[str]
            Type of the entity. (provider: wsj)
        formatted_price : Optional[str]
            Formatted price. (provider: wsj)
        formatted_volume : Optional[str]
            Formatted volume. (provider: wsj)
        formatted_price_change : Optional[str]
            Formatted price change. (provider: wsj)
        formatted_percent_change : Optional[str]
            Formatted percent change. (provider: wsj)
        url : Optional[str]
            The source url. (provider: wsj)

        Example
        -------
        >>> from openbb import obb
        >>> obb.etf.discovery.losers(sort="desc", limit=10)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "sort": sort,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/etf/discovery/losers",
            **inputs,
        )
