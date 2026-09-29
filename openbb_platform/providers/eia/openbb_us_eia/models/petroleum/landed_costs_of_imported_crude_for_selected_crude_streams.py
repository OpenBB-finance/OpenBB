"""Landed Costs of Imported Crude for Selected Crude Streams model."""

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


class EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams(
    EiaApiQueryParams
):
    """Landed Costs of Imported Crude for Selected Crude Streams. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/land2
    """

    __group__ = "petroleum"
    __dataset__ = "landed_costs_of_imported_crude_for_selected_crude_streams"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "algerian_saharan_blend_crude_oil",
                "angolan_cabinda_crude_oil",
                "brazilian_marlim_crude_oil",
                "canadian_bow_river_heavy_crude_oil",
                "canadian_lloydminster_crude_oil",
                "canadian_light_sour_blend_crude_oil",
                "ecuadorian_napo_crude_oil",
                "ecuadorian_oriente_crude_oil",
                "gabon_rabi_kouanga_crude_oil",
                "iraqi_basrah_light_crude_oil",
                "mexican_mayan_crude_oil",
                "mexican_olmeca_crude_oil",
                "nigerian_bonny_light_crude_oil",
                "nigerian_forcados_blend_crude_oil",
                "nigerian_qua_iboe",
                "saudi_arabian_berri_crude_oil",
                "saudi_arab_light_crude_oil",
                "saudi_arab_medium_crude_oil",
                "uk_brent_crude_oil",
                "venezuelan_furial_crude_oil",
                "venezuelan_leona_crude_oil",
                "venezuelan_merey",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "ago",
                "bra",
                "can",
                "dza",
                "ecu",
                "gab",
                "gbr",
                "irq",
                "mex",
                "nga",
                "sau",
                "ven",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_landed_costs_of_algerian_saharan_blend_crude_oil",
                "us_landed_costs_of_angolan_cabinda_crude_oil",
                "us_landed_costs_of_brazilian_marlim_crude_oil",
                "us_landed_costs_of_canadian_bow_river_heavy_crude_oil",
                "us_landed_costs_of_canadian_lloydminster_crude_oil",
                "us_landed_costs_of_canadian_light_sour_blend_crude_oil",
                "us_landed_costs_of_ecuadorian_napo_crude_oil",
                "us_landed_costs_of_ecuadorian_oriente_crude_oil",
                "us_landed_costs_of_gabon_rabi_kouanga_crude_oil",
                "us_landed_costs_of_iraqi_basrah_light_crude_oil",
                "us_landed_costs_of_mexican_mayan_crude_oil",
                "us_landed_costs_of_mexican_olmeca_crude_oil",
                "us_landed_costs_of_nigerian_bonny_light_crude_oil",
                "us_landed_costs_of_nigerian_forcados_blend_crude_oil",
                "us_landed_costs_of_nigerian_qua_iboe_crude_oil",
                "us_landed_costs_of_saudi_arabian_berri_crude_oil",
                "us_landed_costs_of_saudi_arabian_light_crude_oil",
                "us_landed_costs_of_saudi_arabian_medium_crude_oil",
                "us_landed_costs_of_united_kingdom_brent_crude_oil",
                "us_landed_costs_of_venezuelan_furrial_crude_oil",
                "us_landed_costs_of_venezuelan_leona_crude_oil",
                "us_landed_costs_of_venezuelan_merey_crude_oil",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsData(EiaApiData):
    """Landed Costs of Imported Crude for Selected Crude Streams. EIA petroleum gas survey data"""

    process: str | None = Field(
        default=None,
        description="Process code.",
    )
    process_name: str | None = Field(
        default=None,
        description="Process name.",
    )
    product: str | None = Field(
        default=None,
        description="Product code.",
    )
    product_name: str | None = Field(
        default=None,
        description="Product name.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea code.",
    )
    region_name: str | None = Field(
        default=None,
        description="DuoArea name.",
    )
    series: str | None = Field(
        default=None,
        description="Series code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Series name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    units: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsFetcher(
    Fetcher[
        EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams,
        list[EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsData],
    ]
):
    """Landed Costs of Imported Crude for Selected Crude Streams fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsData,
            query,
            data,
        )
