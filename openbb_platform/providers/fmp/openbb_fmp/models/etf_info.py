"""FMP ETF Info Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator


class FMPEtfInfoQueryParams(EtfInfoQueryParams):
    """FMP ETF Info Query."""


class FMPEtfInfoData(EtfInfoData):
    """FMP ETF Info Data."""

    cusip: Optional[str] = Field(description="CUSIP of the ETF.", default=None)
    isin: Optional[str] = Field(description="ISIN of the ETF.", default=None)
    issuer: Optional[str] = Field(alias="etfCompany", description="Company of the ETF.", default=None)
    domicile: Optional[str] = Field(description="Domicile of the ETF.", default=None)
    asset_class: Optional[str] = Field(
        alias="assetClass", description="Asset class of the ETF.", default=None
    )
    holdings_count: Optional[int] = Field(
        alias="holdingsCount", description="Number of holdings in the ETF.", default=None
    )
    aum: Optional[float] = Field(description="Assets under management.", default=None)
    expense_ratio: Optional[float] = Field(
        alias="expenseRatio", description="Expense ratio of the ETF.", default=None
    )
    nav: Optional[float] = Field(description="Net asset value of the ETF.", default=None)
    currency: Optional[str] = Field(
        alias="navCurrency", description="Currency of the ETF's net asset value.", default=None
    )
    expense_ratio: Optional[float] = Field(
        default=None,
        alias="expenseRatio",
        description="Expense ratio of the ETF.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    volume_avg: Optional[float] = Field(
        alias="avgVolume", description="Average daily trading volume of the ETF.", default=None
    )
    website: Optional[str] = Field(description="Website link of the ETF.", default=None)
    description: Optional[str] = Field(description="Description of the ETF.", default=None)

    @field_validator("expense_ratio", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):  # pylint: disable=E0213
        """Normalize percent."""
        return float(v) / 100 if v else None


class FMPEtfInfoFetcher(
    Fetcher[
        FMPEtfInfoQueryParams,
        List[FMPEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfInfoQueryParams:
        """Transform the query."""
        return FMPEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(version=4, endpoint="etf-info", api_key=api_key, query=query)

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfInfoQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfInfoData]:
        """Return the transformed data."""
        # remove "sectorList" key from data. it's handled by the sectors
        results: List[FMPEtfInfoData] = []
        for d in data:
            d.pop("sectorsList", None)
            d["website"] = None if d["website"] == "" else d["website"]
            results.append(FMPEtfInfoData.model_validate(d))
        return results
