"""FINRA OTC Aggregate Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.otc_aggregate import (
    OTCAggregateData,
    OTCAggregateQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_finra.utils.constants import OTC_TIERS

FIELDS = [
    "weekStartDate",
    "issueSymbolIdentifier",
    "issueName",
    "tierDescription",
    "productTypeCode",
    "totalWeeklyShareQuantity",
    "totalWeeklyTradeCount",
    "totalNotionalSum",
    "initialPublishedDate",
    "lastUpdateDate",
    "lastReportedDate",
]


class FinraOTCAggregateQueryParams(OTCAggregateQueryParams):
    """FINRA OTC Aggregate Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    tier: OTC_TIERS = Field(
        default="T1",
        description="T1 - NMS stocks in the S&P 500, Russell 1000, and selected ETPs;"
        + " T2 - all other NMS stocks; OTCE - OTC equity securities.",
    )
    is_ats: bool = Field(
        default=True,
        description="Alternative Trading System (ATS) volume when True,"
        + " other OTC (non-ATS) volume when False.",
    )


class FinraOTCAggregateData(OTCAggregateData):
    """FINRA OTC Aggregate Data."""

    __alias_dict__ = {
        "symbol": "issueSymbolIdentifier",
        "share_quantity": "totalWeeklyShareQuantity",
        "trade_quantity": "totalWeeklyTradeCount",
        "update_date": "lastUpdateDate",
        "week_start_date": "weekStartDate",
        "tier": "tierDescription",
        "product_type": "productTypeCode",
        "total_notional": "totalNotionalSum",
    }

    week_start_date: dateType = Field(
        description="The first business day (Monday) of the reported week.",
    )
    issue_name: str | None = Field(
        default=None, description="The name of the security."
    )
    tier: str | None = Field(
        default=None, description="The tier the security was reported under."
    )
    product_type: str | None = Field(
        default=None,
        description="The product type - Nasdaq-listed, NYSE and regional"
        + " exchange-listed, or OTC equity.",
    )
    total_notional: float | None = Field(
        default=None,
        description="The aggregate weekly notional value of the reported trades.",
    )
    initial_published_date: dateType | None = Field(
        default=None, description="The date the week was first published."
    )
    last_reported_date: dateType | None = Field(
        default=None, description="The most recent date a trade was reported."
    )


class FinraOTCAggregateFetcher(
    Fetcher[FinraOTCAggregateQueryParams, list[FinraOTCAggregateData]]
):
    """Transform the query, extract and transform the data from the FINRA Query API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraOTCAggregateQueryParams:
        """Transform the query."""
        return FinraOTCAggregateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraOTCAggregateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the weekly summary rows from the FINRA Query API.

        Raises
        ------
        EmptyDataError
            If FINRA reported no volume for the query.
        """
        import asyncio

        from openbb_finra.utils.client import query_api_session
        from openbb_finra.utils.helpers import split_symbols

        summary_type = "ATS_W_SMBL" if query.is_ats else "OTC_W_SMBL"
        base = [
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": summary_type,
            },
            {
                "compareType": "EQUAL",
                "fieldName": "tierIdentifier",
                "fieldValue": query.tier,
            },
        ]

        async with query_api_session() as api:
            if query.symbol:
                symbols = [
                    symbol.replace("-", ".").replace("/", ".")
                    for symbol in split_symbols(query.symbol)
                ]
                pages = await asyncio.gather(
                    *(
                        api.query(
                            "otcMarket",
                            "weeklySummary",
                            {
                                "fields": FIELDS,
                                "compareFilters": [
                                    *base,
                                    {
                                        "compareType": "EQUAL",
                                        "fieldName": "issueSymbolIdentifier",
                                        "fieldValue": symbol,
                                    },
                                ],
                            },
                        )
                        for symbol in symbols
                    )
                )
                rows = [row for page in pages for row in page]
            else:
                weeks = sorted(
                    partition[0]
                    for partition in await api.partitions("otcMarket", "weeklySummary")
                    if len(partition) > 1 and partition[1] == query.tier
                )

                if not weeks:
                    raise EmptyDataError(f"FINRA holds no weeks for tier {query.tier}.")

                rows = await api.query(
                    "otcMarket",
                    "weeklySummary",
                    {
                        "fields": FIELDS,
                        "compareFilters": [
                            *base,
                            {
                                "compareType": "EQUAL",
                                "fieldName": "weekStartDate",
                                "fieldValue": weeks[-1],
                            },
                        ],
                        "sortFields": ["-totalWeeklyShareQuantity"],
                    },
                )

        rows = [row for row in rows if row.get("issueSymbolIdentifier")]

        if not rows:
            raise EmptyDataError("FINRA reported no OTC volume for the query.")

        return rows

    @staticmethod
    def transform_data(
        query: FinraOTCAggregateQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraOTCAggregateData]:
        """Transform the data to the model."""
        from openbb_finra.utils.constants import EQUITY_PRODUCT_TYPES
        from openbb_finra.utils.helpers import decode

        records = (
            sorted(
                data,
                key=lambda row: (
                    str(row.get("issueSymbolIdentifier")),
                    str(row.get("weekStartDate")),
                ),
            )
            if query.symbol
            else data
        )

        return [
            FinraOTCAggregateData.model_validate(
                {
                    **record,
                    "productTypeCode": decode(
                        EQUITY_PRODUCT_TYPES, record.get("productTypeCode")
                    ),
                }
            )
            for record in records
        ]
