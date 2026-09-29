"""FINRA Bond List Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_finra.models.bond_prices import FinraBondPricesData
from openbb_finra.utils.constants import BondTypes


class FinraBondListQueryParams(QueryParams):
    """FINRA Bond List Query."""

    bond_type: BondTypes = Field(
        default="CA",
        description="The TRACE product - CA (corporate and agency), TS (U.S. Treasury),"
        + " TBA, MBS, ABS, or CMO.",
    )
    include_matured: bool = Field(
        default=False, description="Include the bonds that have matured."
    )


class FinraBondListData(FinraBondPricesData):
    """FINRA Bond List Data."""


class FinraBondListFetcher(Fetcher[FinraBondListQueryParams, list[FinraBondListData]]):
    """Transform the query, extract and transform the data from FINRA TRACE."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraBondListQueryParams:
        """Transform the query."""
        return FinraBondListQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraBondListQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return every TRACE-reported bond of one type.

        Raises
        ------
        EmptyDataError
            If TRACE holds no bond of the type.
        """
        from openbb_finra.models.bond_prices import (
            FinraBondPricesQueryParams,
            distinct_bonds,
            read_bonds,
        )
        from openbb_finra.utils.client import trace_session

        filters = FinraBondPricesQueryParams(
            bond_type=query.bond_type, include_matured=query.include_matured
        )

        async with trace_session() as trace:
            rows = await read_bonds(trace, filters, query.bond_type, [])

        values = distinct_bonds([rows])

        if not values:
            raise EmptyDataError(f"TRACE holds no {query.bond_type} bonds.")

        return values

    @staticmethod
    def transform_data(
        query: FinraBondListQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraBondListData]:
        """Transform the data to the model."""
        return [FinraBondListData.model_validate(record) for record in data]
