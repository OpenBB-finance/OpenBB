"""TMX Historical Splits Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_splits import (
    HistoricalSplitsData,
    HistoricalSplitsQueryParams,
)
from pydantic import Field


class TmxHistoricalSplitsQueryParams(HistoricalSplitsQueryParams):
    """TMX Historical Splits Query."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxHistoricalSplitsData(HistoricalSplitsData):
    """TMX Historical Splits Data."""

    ratio: float | None = Field(
        default=None, description="The split ratio, as published."
    )


class TmxHistoricalSplitsFetcher(
    Fetcher[TmxHistoricalSplitsQueryParams, list[TmxHistoricalSplitsData]]
):
    """TMX Historical Splits Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxHistoricalSplitsQueryParams:
        """Transform the query."""
        return TmxHistoricalSplitsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxHistoricalSplitsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbol = normalize_symbol(query.symbol)

        try:
            response = await amake_gql_request(
                "getSplitsForSymbol",
                gql.SPLITS_FOR_SYMBOL,
                {"symbol": symbol},
                symbol=symbol,
                use_cache=query.use_cache,
            )
        except OpenBBError as error:
            if "Cannot read properties of undefined" not in str(error):
                raise

            response = {}

        results = (response or {}).get("getSplitsForSymbol") or []

        if not results:
            raise EmptyDataError(f"No splits were returned for {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: TmxHistoricalSplitsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxHistoricalSplitsData]:
        """Transform the data and validate the model."""
        return [
            TmxHistoricalSplitsData.model_validate(
                {"date": d.get("splitDate"), "ratio": d.get("ratio")}
            )
            for d in sorted(data, key=lambda d: d.get("splitDate") or "", reverse=True)
        ]
