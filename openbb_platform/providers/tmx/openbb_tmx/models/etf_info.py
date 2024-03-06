"""TMX ETF Info fetcher."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from openbb_tmx.utils.helpers import get_all_etfs
from pydantic import Field, field_validator


class TmxEtfInfoQueryParams(EtfInfoQueryParams):
    """TMX ETF Info Query Params"""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfInfoData(EtfInfoData):
    """TMX ETF Info Data."""

    issuer: Optional[str] = Field(
        description="The issuer of the ETF.", alias="fund_family", default=None
    )
    investment_style: Optional[str] = Field(
        description="The investment style of the ETF.", default=None
    )
    esg: Optional[bool] = Field(
        description="Whether the ETF qualifies as an ESG fund.", default=None
    )
    currency: Optional[str] = Field(description="The currency of the ETF.")
    unit_price: Optional[float] = Field(
        description="The unit price of the ETF.", default=None
    )
    close: Optional[float] = Field(description="The closing price of the ETF.")
    prev_close: Optional[float] = Field(
        description="The previous closing price of the ETF.", default=None
    )
    return_1m: Optional[float] = Field(
        description="The one-month return of the ETF, as a normalized percent",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_3m: Optional[float] = Field(
        description="The three-month return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_6m: Optional[float] = Field(
        description="The six-month return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_ytd: Optional[float] = Field(
        description="The year-to-date return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_1y: Optional[float] = Field(
        description="The one-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_3y: Optional[float] = Field(
        description="The three-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_5y: Optional[float] = Field(
        description="The five-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_10y: Optional[float] = Field(
        description="The ten-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_from_inception: Optional[float] = Field(
        description="The return from inception of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    avg_volume: Optional[int] = Field(
        description="The average daily volume of the ETF.",
        alias="volume_avg_daily",
        default=None,
    )
    avg_volume_30d: Optional[int] = Field(
        description="The 30-day average volume of the ETF.",
        alias="volume_avg_30d",
        default=None,
    )
    aum: Optional[float] = Field(description="The AUM of the ETF.", default=None)
    pe_ratio: Optional[float] = Field(
        description="The price-to-earnings ratio of the ETF.", default=None
    )
    pb_ratio: Optional[float] = Field(
        description="The price-to-book ratio of the ETF.", default=None
    )
    management_fee: Optional[float] = Field(
        description="The management fee of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    mer: Optional[float] = Field(
        description="The management expense ratio of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    distribution_yield: Optional[float] = Field(
        description="The distribution yield of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    dividend_frequency: Optional[str] = Field(
        description="The dividend payment frequency of the ETF.", default=None
    )
    website: Optional[str] = Field(description="The website of the ETF.", default=None)
    description: Optional[str] = Field(
        description="The description of the ETF.",
        alias="investment_objectives",
        default=None,
    )

    @field_validator(
        "distribution_yield",
        "return_1m",
        "return_3m",
        "return_6m",
        "return_ytd",
        "return_1y",
        "return_3y",
        "return_5y",
        "return_10y",
        "return_from_inception",
        "mer",
        "management_fee",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxEtfInfoFetcher(
    Fetcher[
        TmxEtfInfoQueryParams,
        List[TmxEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfInfoQueryParams:
        """Transform the query."""
        return TmxEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = []
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        _data = pd.DataFrame(await get_all_etfs(use_cache=query.use_cache))
        COLUMNS = [
            "symbol",
            "inception_date",
            "name",
            "fund_family",
            "investment_style",
            "esg",
            "currency",
            "unit_price",
            "close",
            "prev_close",
            "return_1m",
            "return_3m",
            "return_6m",
            "return_ytd",
            "return_1y",
            "return_3y",
            "return_5y",
            "return_from_inception",
            "volume_avg_daily",
            "volume_avg_30d",
            "aum",
            "pe_ratio",
            "pb_ratio",
            "management_fee",
            "mer",
            "distribution_yield",
            "dividend_frequency",
            "website",
            "investment_objectives",
        ]

        for symbol in symbols:
            result = {}
            target = pd.DataFrame()
            symbol = (  # noqa: PLW2901
                symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")
            )
            target = _data[_data["symbol"] == symbol][COLUMNS]
            target = target.fillna("N/A").replace("N/A", None)
            if len(target) > 0:
                result = target.reset_index(drop=True).transpose().to_dict()[0]
                results.append(result)
        return results

    @staticmethod
    def transform_data(
        query: TmxEtfInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxEtfInfoData]:
        """Return the transformed data."""
        return [TmxEtfInfoData.model_validate(d) for d in data]
