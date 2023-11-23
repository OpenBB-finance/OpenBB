"""CBOE European Index Constituents Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_cboe.utils.helpers import EUR_INDEX_CONSTITUENTS_COLUMNS, Europe
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.european_index_constituents import (
    EuropeanIndexConstituentsData,
    EuropeanIndexConstituentsQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field, field_validator


class CboeEuropeanIndexConstituentsQueryParams(EuropeanIndexConstituentsQueryParams):
    """CBOE European Index Constituents Query.

    Source: https://www.cboe.com/

    Gets the current price data for all constituents of the CBOE European Index.
    """


class CboeEuropeanIndexConstituentsData(EuropeanIndexConstituentsData):
    """CBOE European Index Constituents Data.

    Current trading day price data for all constituents of the CBOE European Index.
    """

    prev_close: Optional[float] = Field(
        default=None, description="Previous closing  price."
    )
    change: Optional[float] = Field(default=None, description="Change in price.")
    change_percent: Optional[float] = Field(
        default=None, description="Change in price as a percentage."
    )
    tick: Optional[str] = Field(
        default=None, description="Whether the last sale was an up or down tick."
    )
    last_trade_timestamp: Optional[datetime] = Field(
        default=None, description="Last trade timestamp for the symbol."
    )
    exchange_id: Optional[int] = Field(
        default=None, description="The Exchange ID number."
    )
    seqno: Optional[int] = Field(
        default=None, description="Sequence number of the last trade on the tape."
    )
    asset_type: Optional[str] = Field(
        default=None, description="Type of asset.", alias="type"
    )

    @field_validator("last_trade_timestamp", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        return datetime.strftime(v, "%Y-%m-%d %H:%M:%S")


class CboeEuropeanIndexConstituentsFetcher(
    Fetcher[
        CboeEuropeanIndexConstituentsQueryParams,
        List[CboeEuropeanIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> CboeEuropeanIndexConstituentsQueryParams:
        """Transform the query."""
        return CboeEuropeanIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeEuropeanIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        SYMBOLS = pd.DataFrame(Europe.list_indices())["symbol"].to_list()
        query.symbol = query.symbol.upper()

        if query.symbol not in SYMBOLS:
            raise RuntimeError(
                f"The symbol, {query.symbol},"
                "was not found in the CBOE European Index directory. "
                "Use `available_indices(europe=True)` to see the full list of indices."
            )
        url = f"https://cdn.cboe.com/api/global/european_indices/constituent_quotes/{query.symbol}.json"

        r = make_request(url)
        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        r_json = r.json()

        data = (
            pd.DataFrame.from_records(r_json["data"])[
                list(EUR_INDEX_CONSTITUENTS_COLUMNS.keys())
            ]
            .rename(columns=EUR_INDEX_CONSTITUENTS_COLUMNS)
            .round(2)
        )
        data["last_trade_timestamp"] = pd.to_datetime(data["last_trade_timestamp"])

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeEuropeanIndexConstituentsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeEuropeanIndexConstituentsData]:
        """Transform the data to the standard format."""
        return [CboeEuropeanIndexConstituentsData.model_validate(d) for d in data]
