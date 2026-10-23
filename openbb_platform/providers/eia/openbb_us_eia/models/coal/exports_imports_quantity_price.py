"""Exports/Imports Quantity/Price model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaCoalExportsImportsQuantityPriceQueryParams(EiaApiQueryParams):
    """Exports/Imports Quantity/Price. Coal import/export data, including price, quantity, country, rank, and customs district. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/exports-imports-quantity-price
    """

    __group__ = "coal"
    __dataset__ = "exports_imports_quantity_price"
    __json_schema_extra__ = {
        "data_type": {"multiple_items_allowed": True, "choices": ["price", "quantity"]},
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": ["all", "coke", "metallurgical", "steam_coal"],
        },
        "country": {"multiple_items_allowed": True},
        "customs_district": {
            "multiple_items_allowed": True,
            "choices": [
                "anchorage_ak",
                "baltimore_md",
                "boston_ma",
                "buffalo_ny",
                "charleston_sc",
                "charlotte_nc",
                "chicago_il",
                "cleveland_oh",
                "columbia_snake_or",
                "dallas_fort_worth_tx",
                "detroit_mi",
                "duluth_mn",
                "el_paso_tx",
                "great_falls_mt",
                "honolulu_hi",
                "houston_galveston_tx",
                "laredo_tx",
                "los_angeles_ca",
                "miami_fl",
                "milwaukee_wi",
                "minneapolis_mn",
                "mobile_al",
                "new_orleans_la",
                "new_york_city_ny",
                "nogales_az",
                "norfolk_va",
                "ogdensburg_ny",
                "other_ports",
                "pembina_nd",
                "philadelphia_pa",
                "port_arthur_tx",
                "portland_me",
                "portland_or",
                "providence_ri",
                "san_diego_ca",
                "san_francisco_ca",
                "san_juan_pr",
                "savannah_ga",
                "seattle_wa",
                "st_albans_vt",
                "tampa_fl",
                "total",
                "virgin_islands_of_the_united_states",
                "wilmington_nc",
            ],
        },
        "export_import_type": {
            "multiple_items_allowed": True,
            "choices": ["exports", "imports"],
        },
    }

    frequency: Literal["annual", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'annual'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: price (dollars per short ton); quantity (short tons).",
    )
    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    country: str | None = Field(
        default=None,
        description="Country filter. Accepts a comma-separated list of values. There are 141 valid values - use the `facet_options` endpoint to list them.",
    )
    customs_district: str | None = Field(
        default=None,
        description="Customs District filter. Accepts a comma-separated list of values.",
    )
    export_import_type: Literal["exports", "imports"] | None = Field(
        default=None,
        description="Export\\Import Type filter.",
    )


class EiaCoalExportsImportsQuantityPriceData(EiaApiData):
    """Exports/Imports Quantity/Price. Coal import/export data, including price, quantity, country, rank, and customs district. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    country: str | None = Field(
        default=None,
        description="Country code.",
    )
    country_name: str | None = Field(
        default=None,
        description="Country name.",
    )
    customs_district: str | None = Field(
        default=None,
        description="Customs District code.",
    )
    customs_district_name: str | None = Field(
        default=None,
        description="Customs District name.",
    )
    export_import_type: str | None = Field(
        default=None,
        description="Export\\Import Type code.",
    )
    export_import_type_name: str | None = Field(
        default=None,
        description="Export\\Import Type name.",
    )
    price: float | None = Field(
        default=None,
        description="Price (dollars per short ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (short tons). Withheld or unavailable values return as null.",
    )


class EiaCoalExportsImportsQuantityPriceFetcher(
    Fetcher[
        EiaCoalExportsImportsQuantityPriceQueryParams,
        list[EiaCoalExportsImportsQuantityPriceData],
    ]
):
    """Exports/Imports Quantity/Price fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaCoalExportsImportsQuantityPriceQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaCoalExportsImportsQuantityPriceQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaCoalExportsImportsQuantityPriceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalExportsImportsQuantityPriceQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalExportsImportsQuantityPriceData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaCoalExportsImportsQuantityPriceData, query, data
        )
