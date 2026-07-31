"""Receipts model."""

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


class EiaCoalReceiptsQueryParams(EiaApiQueryParams):
    """Receipts. Coal shipment detailed by reciepient data, including transportation type, supplier, mine, coal basin, county, state, rank, contract type, price, quantity, and quality. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/receipts
    """

    __group__ = "coal"
    __dataset__ = "receipts"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "ash_content",
                "heat_content",
                "price",
                "quantity",
                "sulfur_content",
            ],
        },
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": ["all", "anthracite", "bituminous", "lignite", "subbituminous"],
        },
        "coal_supplier": {"multiple_items_allowed": True},
        "contract_type": {
            "multiple_items_allowed": True,
            "choices": [
                "contract_purchase",
                "new_contract",
                "none",
                "spot_market_purchase",
            ],
        },
        "mine": {"multiple_items_allowed": True},
        "mine_basin": {
            "multiple_items_allowed": True,
            "choices": [
                "appalachia_central",
                "appalachia_northern",
                "appalachia_southern",
                "illinois_basin",
                "other_interior",
                "other_western",
                "powder_river_basin",
                "uinta_basin",
            ],
        },
        "mine_county": {
            "multiple_items_allowed": True,
            "choices": [
                "10",
                "101",
                "107",
                "109",
                "115",
                "119",
                "127",
                "129",
                "133",
                "147",
                "149",
                "159",
                "175",
                "177",
                "189",
                "203",
                "225",
                "233",
                "235",
                "237",
                "25",
                "3",
                "33",
                "39",
                "47",
                "49",
                "53",
                "61",
                "63",
                "67",
                "7",
                "71",
                "77",
                "79",
                "81",
                "85",
                "9",
                "91",
                "95",
                "97",
                "99",
                "anderson",
                "atascosa",
                "bourbon",
                "campbell",
                "choctaw",
                "clay",
                "columbiana",
                "coshocton",
                "craig",
                "crawford",
                "cullman",
                "daviess",
                "dickenson",
                "douglas",
                "emery",
                "fayette",
                "freestone",
                "gallatin",
                "jefferson",
                "lawrence",
                "lee",
                "leon",
                "limestone",
                "lincoln",
                "marion",
                "mclean",
                "meigs",
                "montgomery",
                "natchitoches",
                "navajo",
                "noble",
                "none",
                "okmulgee",
                "oliver",
                "perry",
                "richland",
                "rio_blanco",
                "robertson",
                "rogers",
                "rusk",
                "saline",
                "san_juan",
                "shelby",
                "stark",
                "sullivan",
                "tazewell",
                "titus",
                "tuscaloosa",
                "tuscarawas",
                "vermilion",
                "vigo",
                "vinton",
                "warrick",
                "white",
                "williamson",
                "wise",
                "yukon_koyukuk",
            ],
        },
        "mine_state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "colorado",
                "illinois",
                "indiana",
                "kansas",
                "kentucky_east",
                "kentucky_west",
                "louisiana",
                "maryland",
                "mississippi",
                "missouri",
                "montana",
                "new_mexico",
                "north_dakota",
                "ohio",
                "oklahoma",
                "pennsylvania_anthracite",
                "pennsylvania_bituminous",
                "tennessee",
                "texas",
                "utah",
                "virginia",
                "west_virginia_northern",
                "west_virginia_southern",
                "wyoming",
            ],
        },
        "mine_type": {
            "multiple_items_allowed": True,
            "choices": ["surface", "underground"],
        },
        "plant": {"multiple_items_allowed": True},
        "plant_state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "california",
                "colorado",
                "connecticut",
                "delaware",
                "florida",
                "georgia",
                "hawaii",
                "illinois",
                "indiana",
                "iowa",
                "kansas",
                "kentucky",
                "louisiana",
                "maine",
                "maryland",
                "massachusetts",
                "michigan",
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "nebraska",
                "nevada",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pennsylvania",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "utah",
                "virginia",
                "washington",
                "west_virginia",
                "wisconsin",
                "wyoming",
            ],
        },
        "transportation_mode": {
            "multiple_items_allowed": True,
            "choices": [
                "great_lakes",
                "none",
                "pipeline",
                "rail",
                "river",
                "tidewater_piers",
                "tramway_conveyor",
                "truck",
                "water",
            ],
        },
    }

    frequency: Literal["annual", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'annual'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: ash_content (percent by weight); heat_content (Btu per pound); price (average dollars per ton); quantity (tons); sulfur_content (percent by weight).",
    )
    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    coal_supplier: str | None = Field(
        default=None,
        description="Coal Supplier filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    contract_type: (
        Literal["contract_purchase", "new_contract", "none", "spot_market_purchase"]
        | None
    ) = Field(
        default=None,
        description="Contract Type filter.",
    )
    mine: str | None = Field(
        default=None,
        description="Mine filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    mine_basin: (
        Literal[
            "appalachia_central",
            "appalachia_northern",
            "appalachia_southern",
            "illinois_basin",
            "other_interior",
            "other_western",
            "powder_river_basin",
            "uinta_basin",
        ]
        | None
    ) = Field(
        default=None,
        description="Mine Basin filter.",
    )
    mine_county: str | None = Field(
        default=None,
        description="Mine County filter. Accepts a comma-separated list of values.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region filter. Accepts a comma-separated list of values.",
    )
    mine_type: Literal["surface", "underground"] | None = Field(
        default=None,
        description="Mine Type filter.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant filter. Accepts a comma-separated list of values. There are 471 valid values - use the `facet_options` endpoint to list them.",
    )
    plant_state: str | None = Field(
        default=None,
        description="Plant State\\Region filter. Accepts a comma-separated list of values.",
    )
    transportation_mode: (
        Literal[
            "great_lakes",
            "none",
            "pipeline",
            "rail",
            "river",
            "tidewater_piers",
            "tramway_conveyor",
            "truck",
            "water",
        ]
        | None
    ) = Field(
        default=None,
        description="Transportation Mode filter.",
    )


class EiaCoalReceiptsData(EiaApiData):
    """Receipts. Coal shipment detailed by reciepient data, including transportation type, supplier, mine, coal basin, county, state, rank, contract type, price, quantity, and quality. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    coal_supplier: str | None = Field(
        default=None,
        description="Coal Supplier code.",
    )
    coal_supplier_name: str | None = Field(
        default=None,
        description="Coal Supplier name.",
    )
    contract_type: str | None = Field(
        default=None,
        description="Contract Type code.",
    )
    contract_type_name: str | None = Field(
        default=None,
        description="Contract Type name.",
    )
    mine: str | None = Field(
        default=None,
        description="Mine code.",
    )
    mine_name: str | None = Field(
        default=None,
        description="Mine name.",
    )
    mine_basin: str | None = Field(
        default=None,
        description="Mine Basin code.",
    )
    mine_basin_name: str | None = Field(
        default=None,
        description="Mine Basin name.",
    )
    mine_county: str | None = Field(
        default=None,
        description="Mine County code.",
    )
    mine_county_name: str | None = Field(
        default=None,
        description="Mine County name.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region code.",
    )
    mine_state_name: str | None = Field(
        default=None,
        description="Mine State\\Region name.",
    )
    mine_type: str | None = Field(
        default=None,
        description="Mine Type code.",
    )
    mine_type_name: str | None = Field(
        default=None,
        description="Mine Type name.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant code.",
    )
    plant_name: str | None = Field(
        default=None,
        description="Plant name.",
    )
    plant_state: str | None = Field(
        default=None,
        description="Plant State\\Region code.",
    )
    plant_state_name: str | None = Field(
        default=None,
        description="Plant State\\Region name.",
    )
    transportation_mode: str | None = Field(
        default=None,
        description="Transportation Mode code.",
    )
    transportation_mode_name: str | None = Field(
        default=None,
        description="Transportation Mode name.",
    )
    ash_content: float | None = Field(
        default=None,
        description="Ash content (percent by weight). Withheld or unavailable values return as null.",
    )
    heat_content: float | None = Field(
        default=None,
        description="Heat content (Btu per pound). Withheld or unavailable values return as null.",
    )
    price: float | None = Field(
        default=None,
        description="Price (average dollars per ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (tons). Withheld or unavailable values return as null.",
    )
    sulfur_content: float | None = Field(
        default=None,
        description="Sulfur content (percent by weight). Withheld or unavailable values return as null.",
    )


class EiaCoalReceiptsFetcher(
    Fetcher[EiaCoalReceiptsQueryParams, list[EiaCoalReceiptsData]]
):
    """Receipts fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalReceiptsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalReceiptsQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalReceiptsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalReceiptsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalReceiptsData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalReceiptsData, query, data)
