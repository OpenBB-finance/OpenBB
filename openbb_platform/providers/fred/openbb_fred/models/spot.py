"""FRED Spot Rate Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.spot import (
    SpotRateData,
    SpotRateQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_fred.utils.query import UseCacheQueryParams

CATEGORY_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "category"}}
EXCLUDED_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "excluded"}}
SERIES_PERCENT_COLUMN: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"cellDataType": "number", "chartDataType": "series"},
}


class FREDSpotRateQueryParams(UseCacheQueryParams, SpotRateQueryParams):
    """FRED Spot Rate Query."""

    __json_schema_extra__ = {
        "maturity": {"multiple_items_allowed": True},
        "category": {
            "multiple_items_allowed": True,
            "choices": ["par_yield", "spot_rate"],
        },
    }


class FREDSpotRateData(SpotRateData):
    """FRED Spot Rate Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=EXCLUDED_COLUMN,
    )
    maturity: str = Field(
        description="Maturity length of the security.",
        json_schema_extra=CATEGORY_COLUMN,
    )
    rate: float | None = Field(
        default=None,
        description="Spot Rate.",
        json_schema_extra=SERIES_PERCENT_COLUMN,
    )


class FREDSpotRateFetcher(
    Fetcher[
        FREDSpotRateQueryParams,
        list[FREDSpotRateData],
    ]
):
    """FRED Spot Rate Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDSpotRateQueryParams:
        """Transform query."""
        return FREDSpotRateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDSpotRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint.

        Raises
        ------
        OpenBBError
            If a category publishes nothing, or a maturity is not published
            for the categories asked for.
        """
        from openbb_fred.utils.api import get_observations_many, published_value
        from openbb_fred.utils.fred_helpers import (
            comma_to_float_list,
            get_spot_maturities,
            get_spot_series_id,
        )

        api_key = credentials.get("fred_api_key") if credentials else None
        categories = [c.strip() for c in query.category.split(",") if c.strip()]
        maturities = (
            comma_to_float_list(query.maturity)
            if isinstance(query.maturity, str)
            else [query.maturity]
        )
        published = get_spot_maturities(categories)

        if not published:
            raise OpenBBError(
                f"No spot rates are published for: {', '.join(categories)}."
                + " Choose from: par_yield, spot_rate."
            )

        unknown = [m for m in maturities if m not in published]

        if unknown:
            raise OpenBBError(
                f"Maturity not published for {', '.join(categories)}:"
                + f" {', '.join(str(m) for m in unknown)}."
                + f" Choose from: {', '.join(str(m) for m in published)}."
            )

        series = get_spot_series_id(maturity=maturities, category=categories)
        observations = await get_observations_many(
            [item["FRED Series ID"] for item in series],
            api_key,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )
        data: list = []

        for item, rows in zip(series, observations):
            tenor = float(item["Maturity"].removesuffix("y"))

            for row in rows:
                data.append(
                    {
                        "date": row["date"],
                        "maturity": f"year_{item['Maturity'].removesuffix('y')}",
                        "rate": published_value(row["value"]),
                        "_tenor": tenor,
                    }
                )

        return sorted(data, key=lambda r: (r["date"], r["_tenor"]))

    @staticmethod
    def transform_data(
        query: FREDSpotRateQueryParams, data: list, **kwargs: Any
    ) -> list[FREDSpotRateData]:
        """Transform data.

        Raises
        ------
        EmptyDataError
            If the request was returned empty.
        """
        if not data:
            raise EmptyDataError("The request was returned empty.")

        return [
            FREDSpotRateData.model_validate(
                {k: v for k, v in row.items() if k != "_tenor"}
            )
            for row in data
        ]
