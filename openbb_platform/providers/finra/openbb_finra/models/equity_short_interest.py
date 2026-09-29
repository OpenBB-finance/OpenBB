"""FINRA Equity Short Interest Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_short_interest import (
    ShortInterestData,
    ShortInterestQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

FIELDS = [
    "settlementDate",
    "symbolCode",
    "issueName",
    "marketClassCode",
    "currentShortPositionQuantity",
    "previousShortPositionQuantity",
    "averageDailyVolumeQuantity",
    "daysToCoverQuantity",
    "changePreviousNumber",
    "changePercent",
    "revisionFlag",
    "stockSplitFlag",
]


class FinraShortInterestQueryParams(ShortInterestQueryParams):
    """FINRA Equity Short Interest Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FinraShortInterestData(ShortInterestData):
    """FINRA Equity Short Interest Data."""

    __alias_dict__ = {
        "symbol": "symbolCode",
        "market_class": "marketClassCode",
        "current_short_position": "currentShortPositionQuantity",
        "previous_short_position": "previousShortPositionQuantity",
        "avg_daily_volume": "averageDailyVolumeQuantity",
        "days_to_cover": "daysToCoverQuantity",
        "change": "changePreviousNumber",
        "change_pct": "changePercent",
        "revised": "revisionFlag",
        "stock_split": "stockSplitFlag",
    }

    revised: bool = Field(
        default=False,
        description="Whether FINRA revised the cycle after it was first published.",
    )
    stock_split: bool = Field(
        default=False,
        description="Whether a stock split occurred during the cycle.",
    )


class FinraShortInterestFetcher(
    Fetcher[FinraShortInterestQueryParams, list[FinraShortInterestData]]
):
    """Transform the query, extract and transform the data from the FINRA Query API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraShortInterestQueryParams:
        """Transform the query."""
        return FinraShortInterestQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraShortInterestQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the consolidated short interest rows from the FINRA Query API.

        Raises
        ------
        EmptyDataError
            If FINRA holds no short interest for the symbols.
        """
        from openbb_finra.utils.client import query_api_session
        from openbb_finra.utils.helpers import split_symbols

        symbols = [
            "".join(character for character in symbol if character.isalnum())
            for symbol in split_symbols(query.symbol)
        ]

        async with query_api_session() as api:
            rows = await api.query(
                "otcMarket",
                "consolidatedShortInterest",
                {
                    "fields": FIELDS,
                    "domainFilters": [{"fieldName": "symbolCode", "values": symbols}],
                },
            )

        if not rows:
            raise EmptyDataError(f"FINRA holds no short interest for {query.symbol}.")

        return rows

    @staticmethod
    def transform_data(
        query: FinraShortInterestQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraShortInterestData]:
        """Transform the data to the model."""
        from openbb_finra.utils.constants import MARKET_CLASSES
        from openbb_finra.utils.helpers import decode

        return [
            FinraShortInterestData.model_validate(
                {
                    **row,
                    "marketClassCode": decode(
                        MARKET_CLASSES, row.get("marketClassCode")
                    ),
                    "revisionFlag": bool(row.get("revisionFlag")),
                    "stockSplitFlag": bool(row.get("stockSplitFlag")),
                }
            )
            for row in sorted(
                data,
                key=lambda row: (
                    str(row.get("symbolCode")),
                    str(row.get("settlementDate")),
                ),
            )
        ]
