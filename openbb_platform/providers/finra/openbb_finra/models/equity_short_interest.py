"""FINRA Equity Short Interest Model."""

import sqlite3
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_short_interest import (
    ShortInterestData,
    ShortInterestQueryParams,
)
from openbb_finra.utils.data_storage import DB_PATH, prepare_data


class FinraShortInterestQueryParams(ShortInterestQueryParams):
    """FINRA Equity Short Interest Query."""


class FinraShortInterestData(ShortInterestData):
    """FINRA Equity Short Interest Data."""

    __alias_dict__ = {
        "symbol": "symbolCode",
        "issue_name": "issueName",
        "market_class": "marketClassCode",
        "current_short_position": "currentShortPositionQuantity",
        "previous_short_position": "previousShortPositionQuantity",
        "avg_daily_volume": "averageDailyVolumeQuantity",
        "days_to_cover": "daysToCoverQuantity",
        "change": "changePreviousNumber",
        "change_pct": "changePercent",
        "settlement_date": "settlementDate",
    }


class FinraShortInterestFetcher(
    Fetcher[FinraShortInterestQueryParams, List[FinraShortInterestData]]
):
    """Transform the query, extract and transform the data from the FINRA endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinraShortInterestQueryParams:
        """Transform query params."""
        return FinraShortInterestQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinraShortInterestQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Finra endpoint."""
        # Put the data in the cache
        prepare_data()
        # Get the data from the cache
        cnx = sqlite3.connect(DB_PATH)
        cursor = cnx.cursor()
        if query.symbol:
            cursor.execute(
                "SELECT * FROM short_interest where symbolCode = ?", (query.symbol,)
            )
        else:
            cursor.execute("SELECT * FROM short_interest")
        result = cursor.fetchall()

        titles = [
            "symbolCode",
            "issueName",
            "marketClassCode",
            "currentShortPositionQuantity",
            "previousShortPositionQuantity",
            "averageDailyVolumeQuantity",
            "daysToCoverQuantity",
            "changePercent",
            "changePreviousNumber",
            "settlementDate",
        ]
        return [
            {title: value for title, value in zip(titles, list(row)[1:])}
            for row in result
        ]

    @staticmethod
    def transform_data(
        query: FinraShortInterestQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FinraShortInterestData]:
        """Transform the data."""
        return [FinraShortInterestData.model_validate(d) for d in data]
