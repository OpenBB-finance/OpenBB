"""Federal Reserve Primary Dealer Positioning Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.primary_dealer_positioning import (
    PrimaryDealerPositioningQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

PdsCategories = Literal[
    "treasuries",
    "bills",
    "coupons",
    "notes",
    "tips",
    "mbs",
    "cmbs",
    "municipal",
    "corporate",
    "commercial_paper",
    "corporate_ig",
    "corporate_junk",
    "abs",
]

PDS_CATEGORY_CHOICES = [
    "treasuries",
    "bills",
    "coupons",
    "notes",
    "tips",
    "mbs",
    "cmbs",
    "municipal",
    "corporate",
    "commercial_paper",
    "corporate_ig",
    "corporate_junk",
    "abs",
]


class FederalReservePrimaryDealerPositioningQueryParams(
    PrimaryDealerPositioningQueryParams
):
    """Federal Reserve Primary Dealer Positioning Query Params."""

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "options": [
                    {"label": "U.S. Treasury securities", "value": "treasuries"},
                    {"label": "Treasury bills", "value": "bills"},
                    {"label": "Treasury coupons", "value": "coupons"},
                    {"label": "Treasury notes and bonds", "value": "notes"},
                    {
                        "label": "Treasury inflation-protected securities (TIPS)",
                        "value": "tips",
                    },
                    {"label": "Mortgage-backed securities (MBS)", "value": "mbs"},
                    {
                        "label": "Commercial mortgage-backed securities (CMBS)",
                        "value": "cmbs",
                    },
                    {"label": "Municipal securities", "value": "municipal"},
                    {"label": "Corporate securities", "value": "corporate"},
                    {"label": "Commercial paper", "value": "commercial_paper"},
                    {
                        "label": "Investment-grade corporate bonds",
                        "value": "corporate_ig",
                    },
                    {
                        "label": "Below-investment-grade corporate bonds",
                        "value": "corporate_junk",
                    },
                    {"label": "Asset-backed securities (ABS)", "value": "abs"},
                ]
            }
        }
    }

    category: PdsCategories = Field(
        default="treasuries",
        description="The category of asset to return, defaults to 'treasuries'.",
        json_schema_extra={"choices": PDS_CATEGORY_CHOICES},
    )


class FederalReservePrimaryDealerPositioningData(Data):
    """Federal Reserve Primary Dealer Positioning Data."""

    date: dateType = Field(description="The observation date.")


class FederalReservePrimaryDealerPositioningFetcher(
    Fetcher[
        FederalReservePrimaryDealerPositioningQueryParams,
        list[FederalReservePrimaryDealerPositioningData],
    ]
):
    """Federal Reserve Primary Dealer Positioning Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePrimaryDealerPositioningQueryParams:
        """Transform the query params."""
        return FederalReservePrimaryDealerPositioningQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FederalReservePrimaryDealerPositioningQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FederalReserve endpoint."""
        import asyncio

        from openbb_core.provider.utils.helpers import amake_request

        from openbb_federal_reserve.utils.primary_dealer_statistics import (
            POSITION_GROUPS_TO_SERIES,
        )

        symbols = POSITION_GROUPS_TO_SERIES.get(query.category, [])
        results: list[dict] = []

        base_url = "https://markets.newyorkfed.org/api/pd/get/"
        urls = [base_url + symbol + ".json" for symbol in symbols]

        async def get_one(url):
            """Get data for a single URL."""
            result = await amake_request(url)
            if isinstance(result, dict):
                data = result.get("pd", {}).get("timeseries")
                if data:
                    results.extend(data)

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: FederalReservePrimaryDealerPositioningQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePrimaryDealerPositioningData]:
        """Pivot the per-series positions to one wide row per date."""
        from pandas import DataFrame

        from openbb_federal_reserve.utils.primary_dealer_statistics import (
            POSITION_SERIES_TO_FIELD,
        )
        from openbb_federal_reserve.utils.workbook import pivot_wide

        df = DataFrame(data)
        df = df.rename(columns={"keyid": "symbol", "asofdate": "date"})
        df["name"] = df.symbol.map(POSITION_SERIES_TO_FIELD["dealer_position"].get)
        df["value"] = df["value"].astype(int)
        df["date"] = df["date"].astype("datetime64[ns]").dt.date

        if query.start_date:
            df = df[df["date"] >= query.start_date]
        if query.end_date:
            df = df[df["date"] <= query.end_date]

        records = pivot_wide(
            df.sort_values("date")[["date", "name", "value"]].to_dict(orient="records"),
            index="date",
            column="name",
            value="value",
        )
        return [
            FederalReservePrimaryDealerPositioningData.model_validate(r)
            for r in records
        ]
