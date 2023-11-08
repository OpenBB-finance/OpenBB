"""SEC Company Filings fetcher."""

import sqlite3
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.equity_short_interest import (
    ShortInterestData,
    ShortInterestQueryParams,
)
from openbb_sec.utils.data_storage import DB_PATH, prepare_data


class SecShortInterestQueryParams(ShortInterestQueryParams):
    """SEC Company Filings Query Params."""


class SecShortInterestData(ShortInterestData):
    """SEC Short Interest Data."""

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


class SecShortInterestFetcher(
    Fetcher[SecShortInterestQueryParams, List[SecShortInterestData]]
):
    """SEC Short Interest Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecShortInterestQueryParams:
        """Transform query params."""
        return SecShortInterestQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecShortInterestQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extracts the data from the SEC endpoint."""

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
    def transform_data(data: List[Dict], **kwargs: Any) -> List[SecShortInterestData]:
        """Transforms the data."""
        return [SecShortInterestData.model_validate(d) for d in data]
