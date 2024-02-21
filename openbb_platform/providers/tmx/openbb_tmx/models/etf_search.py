"""TMX ETF Search fetcher."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from openbb_tmx.utils.helpers import get_all_etfs
from pydantic import Field, field_validator


class TmxEtfSearchQueryParams(EtfSearchQueryParams):
    """TMX ETF Search query.

    Source: https://www.tmx.com/
    """

    div_freq: Optional[Literal["monthly", "annually", "quarterly"]] = Field(
        description="The dividend payment frequency.", default=None
    )

    sort_by: Optional[
        Literal[
            "nav",
            "return_1m",
            "return_3m",
            "return_6m",
            "return_1y",
            "return_3y",
            "return_ytd",
            "beta_1y",
            "volume_avg_daily",
            "management_fee",
            "distribution_yield",
            "pb_ratio",
            "pe_ratio",
        ]
    ] = Field(description="The column to sort by.", default=None)

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfSearchData(EtfSearchData):
    """TMX ETF Search Data."""

    short_name: Optional[str] = Field(
        description="The short name of the ETF.", default=None
    )
    inception_date: Optional[str] = Field(
        description="The inception date of the ETF.", default=None
    )
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
        description="The one-month return of the ETF, as a normalized percent.",
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
    beta_1y: Optional[float] = Field(
        description="The one-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_3y: Optional[float] = Field(
        description="The three-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    beta_3y: Optional[float] = Field(
        description="The three-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_5y: Optional[float] = Field(
        description="The five-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    beta_5y: Optional[float] = Field(
        description="The five-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_10y: Optional[float] = Field(
        description="The ten-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    beta_10y: Optional[float] = Field(
        description="The ten-year beta of the ETF.", default=None
    )
    beta_15y: Optional[float] = Field(
        description="The fifteen-year beta of the ETF.", default=None
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
        if v:
            return float(v) / 100
        return None


class TmxEtfSearchFetcher(
    Fetcher[
        TmxEtfSearchQueryParams,
        List[TmxEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfSearchQueryParams:
        """Transform the query."""
        return TmxEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        etfs = pd.DataFrame(await get_all_etfs(use_cache=query.use_cache))

        if query.query:
            etfs = etfs[
                etfs["name"].str.contains(query.query, case=False)
                | etfs["short_name"].str.contains(query.query, case=False)
                | etfs["investment_style"].str.contains(query.query, case=False)
                | etfs["investment_objectives"].str.contains(query.query, case=False)
                | etfs["symbol"].str.contains(query.query, case=False)
            ]

        data = etfs.copy()

        if query.div_freq:
            data = data[data["dividend_frequency"] == query.div_freq.capitalize()]

        if query.sort_by:
            data = data.sort_values(by=query.sort_by, ascending=False)

        data.drop(
            columns=[
                "sectors",
                "regions",
                "holdings_top10_summary",
                "holdings_top10",
                "additional_data",
                "website",
                "asset_class_id",
                "investment_objectives",
            ],
            inplace=True,
        )
        data = data.dropna(how="all")
        return data.fillna("N/A").replace("N/A", None).to_dict("records")

    @staticmethod
    def transform_data(
        query: TmxEtfSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxEtfSearchData]:
        """Transform the data to the standard format."""
        return [TmxEtfSearchData.model_validate(d) for d in data]
