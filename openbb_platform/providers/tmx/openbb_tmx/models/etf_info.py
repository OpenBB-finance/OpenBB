"""TMX ETF Info fetcher."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field, field_validator


class TmxEtfInfoQueryParams(EtfInfoQueryParams):
    """TMX ETF Info Query Params"""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfInfoData(EtfInfoData):
    """TMX ETF Info Data."""

    __alias_dict__ = {
        "avg_volume": "volume_avg_daily",
        "issuer": "fund_family",
        "avg_volume_30d": "volume_avg_30d",
        "description": "investment_objectives",
    }

    issuer: str | None = Field(description="The issuer of the ETF.", default=None)
    investment_style: str | None = Field(
        description="The investment style of the ETF.", default=None
    )
    asset_class: str | None = Field(
        description="The asset class of the ETF.", default=None
    )
    region: str | None = Field(
        description="The region the ETF invests in.", default=None
    )
    index_fund: str | None = Field(
        description="Whether the ETF tracks an index or is actively managed.",
        default=None,
    )
    esg: bool | None = Field(
        description="Whether the ETF qualifies as an ESG fund.", default=None
    )
    currency: str | None = Field(description="The currency of the ETF.")
    unit_price: float | None = Field(
        description="The unit price of the ETF.", default=None
    )
    close: float | None = Field(description="The closing price of the ETF.")
    prev_close: float | None = Field(
        description="The previous closing price of the ETF.", default=None
    )
    return_1m: float | None = Field(
        description="The one-month return of the ETF, as a normalized percent",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_3m: float | None = Field(
        description="The three-month return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_6m: float | None = Field(
        description="The six-month return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_ytd: float | None = Field(
        description="The year-to-date return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_1y: float | None = Field(
        description="The one-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_3y: float | None = Field(
        description="The three-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_5y: float | None = Field(
        description="The five-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_10y: float | None = Field(
        description="The ten-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_from_inception: float | None = Field(
        description="The return from inception of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_volume: int | None = Field(
        description="The average daily volume of the ETF.",
        default=None,
    )
    avg_volume_30d: int | None = Field(
        description="The 30-day average volume of the ETF.",
        default=None,
    )
    aum: float | None = Field(description="The AUM of the ETF.", default=None)
    pe_ratio: float | None = Field(
        description="The price-to-earnings ratio of the ETF.", default=None
    )
    pb_ratio: float | None = Field(
        description="The price-to-book ratio of the ETF.", default=None
    )
    management_fee: float | None = Field(
        description="The management fee of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    mer: float | None = Field(
        description="The management expense ratio of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    distribution_yield: float | None = Field(
        description="The distribution yield of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_frequency: str | None = Field(
        description="The dividend payment frequency of the ETF.", default=None
    )
    website: str | None = Field(description="The website of the ETF.", default=None)

    @field_validator("website", mode="before", check_fields=False)
    @classmethod
    def url_validate(cls, v):
        """Return the website as an absolute URL."""
        from openbb_tmx.utils.helpers import normalize_url

        return normalize_url(v)

    description: str | None = Field(
        description="The description of the ETF.",
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
        list[TmxEtfInfoData],
    ]
):
    """TMX ETF Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEtfInfoQueryParams:
        """Transform the query."""
        return TmxEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        from openbb_tmx.utils.helpers import get_all_etfs, purge_nulls

        results = []
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        _data = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        COLUMNS = [
            "symbol",
            "inception_date",
            "name",
            "fund_family",
            "investment_style",
            "asset_class",
            "region",
            "index_fund",
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

        published = [c for c in COLUMNS if c in _data.columns]

        for symbol in symbols:
            result = {}
            target = DataFrame()
            s = symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")  # noqa: PLW2901
            target = _data[_data["symbol"] == s][published]
            target = purge_nulls(target)
            if len(target) > 0:
                result = target.reset_index(drop=True).transpose().to_dict()[0]
                results.append(result)
        return results

    @staticmethod
    def transform_data(
        query: TmxEtfInfoQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEtfInfoData]:
        """Return the transformed data."""
        return [TmxEtfInfoData.model_validate(d) for d in data]
