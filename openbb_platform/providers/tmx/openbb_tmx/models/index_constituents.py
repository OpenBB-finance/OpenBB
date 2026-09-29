"""TMX Index Constituents Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

PUBLISHED = ("symbol", "longName", "exchange", "quotedMarketValue", "weight")


class TmxIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """TMX Index Constituents Query Params."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )


class TmxIndexConstituentsData(IndexConstituentsData):
    """TMX Index Constituents Data."""

    __alias_dict__ = {
        "name": "longName",
        "market_value": "quotedMarketValue",
    }

    exchange: str | None = Field(
        default=None,
        description="The exchange the constituent is listed on.",
    )
    market_value: float | None = Field(
        default=None,
        description="The quoted market value of the asset.",
    )
    weight: float | None = Field(
        default=None,
        description="The weight of the constituent in the index.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxIndexConstituentsFetcher(
    Fetcher[
        TmxIndexConstituentsQueryParams,
        list[TmxIndexConstituentsData],
    ]
):
    """TMX Index Constituents Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxIndexConstituentsQueryParams:
        """Transform the query."""
        return TmxIndexConstituentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexConstituentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Read the complete constituent list.

        Raises
        ------
        OpenBBError
            If the symbol is not one of the published indices.
        """
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        response = await amake_gql_request(
            "getIndexConstituents",
            gql.INDEX_CONSTITUENTS,
            {"symbol": query.symbol},
            use_cache=query.use_cache,
        )
        constituents = (response or {}).get("constituents")

        if constituents is None:
            raise OpenBBError(f"Index {query.symbol} was not found. Check the symbol.")

        return constituents

    @staticmethod
    def transform_data(
        query: TmxIndexConstituentsQueryParams, data: list[dict], **kwargs
    ) -> list[TmxIndexConstituentsData]:
        """Return the transformed data.

        Raises
        ------
        EmptyDataError
            If the index publishes no constituents.
        """
        if not data:
            raise EmptyDataError(f"No constituents found for index, {query.symbol}")

        return [
            TmxIndexConstituentsData.model_validate(
                {k: v for k, v in entry.items() if k in PUBLISHED}
            )
            for entry in data
        ]
