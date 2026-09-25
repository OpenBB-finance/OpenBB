"""TMX ETF Search fetcher."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import etf_value, etf_widget_config, literal_choices
from openbb_tmx.utils.screener_types import (
    ETF_ASSET_CLASS,
    ETF_FUND_FAMILY,
    ETF_INVESTMENT_STYLE,
    ETF_REGION,
)


class TmxEtfSearchQueryParams(EtfSearchQueryParams):
    """TMX ETF Search query."""

    __json_schema_extra__ = etf_widget_config() | {
        "div_freq": {
            "x-widget_config": {
                "options": literal_choices(
                    ("monthly", "quarterly", "annually", "semi-annually", "unspecified")
                )
            }
        },
        "currency": {"x-widget_config": {"options": literal_choices(("CAD", "USD"))}},
        "sort_by": {
            "x-widget_config": {
                "options": literal_choices(
                    (
                        "aum",
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
                    ),
                    return_1m="Return 1M",
                    return_3m="Return 3M",
                    return_6m="Return 6M",
                    return_1y="Return 1Y",
                    return_3y="Return 3Y",
                    beta_1y="Beta 1Y",
                    volume_avg_daily="Average Daily Volume",
                )
            }
        },
    }

    div_freq: (
        Literal["monthly", "quarterly", "annually", "semi-annually", "unspecified"]
        | None
    ) = Field(description="The dividend payment frequency.", default=None)

    asset_class: ETF_ASSET_CLASS | None = Field(
        description="Filter by asset class.",
        default=None,
    )
    region: ETF_REGION | None = Field(
        description="Filter by region.",
        default=None,
    )
    fund_family: ETF_FUND_FAMILY | None = Field(
        description="Filter by fund family.",
        default=None,
    )
    investment_style: ETF_INVESTMENT_STYLE | None = Field(
        description="Filter by investment style.",
        default=None,
    )
    currency: Literal["CAD", "USD"] | None = Field(
        description="Filter by the currency the fund trades in.",
        default=None,
    )
    esg: bool | None = Field(
        description="Restrict to funds flagged as ESG.",
        default=None,
    )

    sort_by: (
        Literal[
            "aum",
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
        | None
    ) = Field(description="The column to sort by.", default=None)

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfSearchData(EtfSearchData):
    """TMX ETF Search Data."""

    __alias_dict__ = {
        "issuer": "fund_family",
        "avg_volume": "volume_avg_daily",
        "avg_volume_30d": "volume_avg_30d",
    }

    short_name: str | None = Field(
        description="The short name of the ETF.", default=None
    )
    inception_date: str | None = Field(
        description="The inception date of the ETF.", default=None
    )
    issuer: str | None = Field(description="The issuer of the ETF.", default=None)
    investment_style: str | None = Field(
        description="The investment style of the ETF.", default=None
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
        description="The one-month return of the ETF, as a normalized percent.",
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
    beta_1y: float | None = Field(
        description="The one-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_3y: float | None = Field(
        description="The three-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta_3y: float | None = Field(
        description="The three-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_5y: float | None = Field(
        description="The five-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta_5y: float | None = Field(
        description="The five-year beta of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_10y: float | None = Field(
        description="The ten-year return of the ETF, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta_10y: float | None = Field(
        description="The ten-year beta of the ETF.", default=None
    )
    beta_15y: float | None = Field(
        description="The fifteen-year beta of the ETF.", default=None
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
        list[TmxEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEtfSearchQueryParams:
        """Transform the query."""
        return TmxEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        from openbb_tmx.utils.helpers import get_all_etfs, purge_nulls

        etfs = DataFrame(await get_all_etfs(use_cache=query.use_cache))

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
            data = data[
                data["dividend_frequency"].astype(str).str.casefold()
                == query.div_freq.casefold()
            ]

        if query.currency:
            data = data[data["currency"].astype(str) == query.currency]

        if query.esg is not None:
            data = data[data["esg"].astype(bool) == query.esg]

        for field in ("asset_class", "region", "fund_family", "investment_style"):
            value = etf_value(field, getattr(query, field, None))

            if value and field in data.columns:
                data = data[data[field].astype(str) == value]

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
        return purge_nulls(data).to_dict("records")

    @staticmethod
    def transform_data(
        query: TmxEtfSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEtfSearchData]:
        """Transform the data to the standard format."""
        # pylint: disable=import-outside-toplevel
        from math import isnan

        def clean_nan(d: dict) -> dict:
            """Replace nan values with None for Pydantic validation."""
            return {
                k: None if isinstance(v, float) and isnan(v) else v
                for k, v in d.items()
            }

        return [TmxEtfSearchData.model_validate(clean_nan(d)) for d in data]
