"""Cboe  Index Constituents Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

ConstituentsEu = Literal[  # pylint: disable=invalid-name
    "BAT20P",
    "BBE20P",
    "BCH20P",
    "BCHM30P",
    "BDE40P",
    "BDEM50P",
    "BDES50P",
    "BDK25P",
    "BEP50P",
    "BEPACP",
    "BEPBUS",
    "BEPCNC",
    "BEPCONC",
    "BEPCONS",
    "BEPENGY",
    "BEPFIN",
    "BEPHLTH",
    "BEPIND",
    "BEPNEM",
    "BEPTEC",
    "BEPTEL",
    "BEPUTL",
    "BEPXUKP",
    "BES35P",
    "BEZ50P",
    "BEZACP",
    "BFI25P",
    "BFR40P",
    "BFRM20P",
    "BIE20P",
    "BIT40P",
    "BNL25P",
    "BNLM25P",
    "BNO25G",
    "BNORD40P",
    "BPT20P",
    "BSE30P",
    "BUK100P",
    "BUK250P",
    "BUK350P",
    "BUKAC",
    "BUKBISP",
    "BUKBUS",
    "BUKCNC",
    "BUKCONC",
    "BUKCONS",
    "BUKENGY",
    "BUKFIN",
    "BUKHI50P",
    "BUKHLTH",
    "BUKIND",
    "BUKLO50P",
    "BUKMINP",
    "BUKNEM",
    "BUKSC",
    "BUKTEC",
    "BUKTEL",
    "BUKUTL",
]


class CboeIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """Cboe  Index Constituents Query.

    Source: https://www.cboe.com/

    Gets the current price data for all constituents of the CBOE European Index.
    """

    symbol: ConstituentsEu = Field(default="BUK100P")


class CboeIndexConstituentsData(IndexConstituentsData):
    """Cboe  Index Constituents Data.

    Current trading day price data for all constituents of the Cboe proprietary index.
    """

    __alias_dict__ = {
        "prev_close": "prev_day_close",
        "change": "price_change",
        "change_percent": "price_change_percent",
        "last_price": "current_price",
        "asset_type": "type",
    }

    security_type: Optional[str] = Field(
        default=None, description="The type of security represented."
    )
    last_price: Optional[float] = Field(
        default=None, description="Last price for the symbol."
    )
    open: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: Optional[int] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    prev_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: Optional[float] = Field(default=None, description="Change in price.")
    change_percent: Optional[float] = Field(
        default=None, description="Change in price as a normalized percentage."
    )
    tick: Optional[str] = Field(
        default=None, description="Whether the last sale was an up or down tick."
    )
    last_trade_time: Optional[datetime] = Field(
        default=None, description="Last trade timestamp for the symbol."
    )
    asset_type: Optional[str] = Field(
        default=None,
        description="Type of asset.",
    )

    @field_validator("last_trade_time", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")


class CboeIndexConstituentsFetcher(
    Fetcher[
        CboeIndexConstituentsQueryParams,
        List[CboeIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeIndexConstituentsQueryParams:
        """Transform the query."""
        return CboeIndexConstituentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Cboe endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        url = (
            "https://cdn.cboe.com/api/global/european_indices"
            f"/constituent_quotes/{query.symbol}.json"
        )
        data = await amake_request(url)
        return data.get("data")  # type: ignore

    @staticmethod
    def transform_data(
        query: CboeIndexConstituentsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeIndexConstituentsData]:
        """Transform the data to the standard format."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError()
        df = DataFrame(data)
        df["price_change_percent"] = df["price_change_percent"] / 100
        df = df.replace(0, None).dropna(how="all", axis=1)
        df = df.drop(columns=["exchange_id"])
        return [
            CboeIndexConstituentsData.model_validate(d)
            for d in df.to_dict(orient="records")
        ]
