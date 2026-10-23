"""FRED High Quality Market Corporate Bond Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.high_quality_market import (
    HighQualityMarketCorporateBondData,
    HighQualityMarketCorporateBondQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
CATEGORY_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "category"}}
EXCLUDED_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "excluded"}}
SERIES_PERCENT_COLUMN: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"cellDataType": "number", "chartDataType": "series"},
}


class FredHighQualityMarketCorporateBondQueryParams(
    UseCacheQueryParams, HighQualityMarketCorporateBondQueryParams
):
    """FRED High Quality Market Corporate Bond Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    yield_curve: Literal["spot", "par"] = Field(
        default="spot",
        description="The yield curve type.",
        json_schema_extra={"choices": ["spot", "par"]},
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Normalize the dates entered to comma-separated ISO dates."""
        from openbb_fred.utils.query import join_dates

        return join_dates(v)


class FredHighQualityMarketCorporateBondData(HighQualityMarketCorporateBondData):
    """FRED High Quality Market Corporate Bond Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=EXCLUDED_COLUMN,
    )
    rate: float = Field(
        description="Interest rate.",
        json_schema_extra=SERIES_PERCENT_COLUMN,
    )
    maturity: str = Field(
        description="Maturity.",
        json_schema_extra=CATEGORY_COLUMN,
    )


class FredHighQualityMarketCorporateBondFetcher(
    Fetcher[
        FredHighQualityMarketCorporateBondQueryParams,
        list[FredHighQualityMarketCorporateBondData],
    ]
):
    """FRED High Quality Market Corporate Bond Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FredHighQualityMarketCorporateBondQueryParams:
        """Transform query."""
        return FredHighQualityMarketCorporateBondQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredHighQualityMarketCorporateBondQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        import asyncio  # noqa
        from dateutil import parser  # noqa
        from openbb_fred.utils.api import observation_dates, release_tables_url
        from openbb_fred.utils.rate_limiter import fred_get  # noqa

        api_key = credentials.get("fred_api_key") if credentials else ""

        element_id = "219299" if query.yield_curve == "spot" else "219294"
        URLS = [
            release_tables_url("402", element_id, api_key, date)
            for date in observation_dates(query.date)
        ]
        results = []

        async def get_one(URL):
            """Get the observations for a single date."""
            data = await fred_get(URL, use_cache=query.use_cache)
            if data:
                elements = dict(data.get("elements", {}).items())
                for k, v in elements.items():
                    value = v.get("observation_value")
                    if not value:
                        continue
                    maturity = v.get("name").lower().split("-")
                    results.append(
                        {
                            "date": parser.parse(
                                v.get("observation_date"),
                            ).date(),
                            "rate": float(value),
                            "maturity": (maturity[1] + "_" + maturity[0]).replace(
                                " ", ""
                            ),
                        }
                    )

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        return results

    @staticmethod
    def transform_data(
        query: FredHighQualityMarketCorporateBondQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FredHighQualityMarketCorporateBondData]:
        """Transform data."""
        from pandas import Categorical, DataFrame

        df = DataFrame(data)
        df["maturity_int"] = df["maturity"].str.replace("year_", "").astype(float)
        maturity_categories = sorted(df.maturity_int.unique().tolist())
        df["maturity_int"] = Categorical(
            df["maturity_int"], categories=maturity_categories, ordered=True
        )
        df = df.sort_values(by=["date", "maturity_int"]).reset_index(drop=True)
        df = df.drop(columns=["maturity_int"])
        records = df.to_dict("records")
        return [
            FredHighQualityMarketCorporateBondData.model_validate(d) for d in records
        ]
