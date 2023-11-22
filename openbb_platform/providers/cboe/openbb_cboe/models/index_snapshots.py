"""CBOE Index Snapshots Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_cboe.utils.helpers import (
    EUR_INDEX_COLUMNS,
    US_INDEX_COLUMNS,
    Europe,
    get_cboe_directory,
    get_cboe_index_directory,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_snapshots import (
    IndexSnapshotsData,
    IndexSnapshotsQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field


class CboeIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """CBOE Index Snapshots Query.

    Source: https://www.cboe.com/
    """


class CboeIndexSnapshotsData(IndexSnapshotsData):
    """CBOE Index Snapshots Data."""

    isin: Optional[str] = Field(
        default=None,
        description="ISIN code for the index. Valid only for European indices.",
    )
    last_trade_timestamp: Optional[datetime] = Field(
        default=None, description="Last trade timestamp for the index."
    )


class CboeIndexSnapshotsFetcher(
    Fetcher[
        CboeIndexSnapshotsQueryParams,
        List[CboeIndexSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeIndexSnapshotsQueryParams:
        """Transform the query."""
        return CboeIndexSnapshotsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeIndexSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint"""
        data = pd.DataFrame()

        if query.region == "US":
            r = make_request(
                "https://cdn.cboe.com/api/global/delayed_quotes/quotes/all_us_indices.json"
            )

            if r.status_code != 200:
                raise RuntimeError(r.status_code)

            INDEXES = pd.concat(
                [get_cboe_index_directory(), get_cboe_directory()], axis=0
            )
            data = pd.DataFrame.from_records(r.json()["data"])

            data.rename(columns=US_INDEX_COLUMNS, inplace=True)
            data["symbol"] = data["symbol"].str.replace("^", "")
            data["name"] = ""
            data = data.set_index("symbol")
            for i in data.index:
                if i in INDEXES.index:
                    data.at[i, "name"] = INDEXES.at[i, "name"]

            data["name"] = data["name"].astype(str)
            data["currency"] = "USD"
            data = data[
                [
                    "name",
                    "price",
                    "prev_close",
                    "change",
                    "change_percent",
                    "open",
                    "high",
                    "low",
                    "close",
                    "currency",
                    "last_trade_timestamp",
                ]
            ]

        if query.region == "EU":
            r = make_request(
                "https://cdn.cboe.com/api/global/european_indices/index_quotes/all-indices.json"
            )

            if r.status_code != 200:
                raise RuntimeError(r.status_code)

            data = (
                pd.DataFrame.from_records(r.json()["data"])
                .drop(columns=["symbol"])
                .rename(columns={"index": "symbol"})
                .set_index("symbol")
                .round(2)
            )

            INDEXES = pd.DataFrame(Europe.list_indices()).set_index("symbol")

            for i in data.index:
                data.loc[i, ("isin")] = INDEXES.at[i, "isin"]
                data.loc[i, ("name")] = INDEXES.at[i, "name"]
                data.loc[i, ("currency")] = INDEXES.at[i, "currency"]

            data = data[list(EUR_INDEX_COLUMNS.keys())]
            data.columns = list(EUR_INDEX_COLUMNS.values())

        data["change_percent"] = data["change_percent"].fillna(0.0)

        return data.reset_index().to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeIndexSnapshotsQueryParams, data: dict, **kwargs: Any
    ) -> List[CboeIndexSnapshotsData]:
        """Transform the data to the standard format"""
        for item in data:
            item["name"] = item["name"].replace("/", "-")

        return [CboeIndexSnapshotsData.model_validate(d) for d in data]
