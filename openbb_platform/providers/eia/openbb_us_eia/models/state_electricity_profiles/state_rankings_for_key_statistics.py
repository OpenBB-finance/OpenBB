"""State Rankings for Key Statistics model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams(
    EiaApiQueryParams
):
    """State Rankings for Key Statistics. State rankings for key electricity statistics by state Source: Forms EIA-860, EIA-861, EIA-923 Product: State Electricity Profiles, Table 1

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/summary
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "state_rankings_for_key_statistics"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "average_retail_price",
                "average_retail_price_rank",
                "capacity_elec_utilities",
                "capacity_elect_utilities_rank",
                "capacity_ipp",
                "capacity_ipp_rank",
                "carbon_dioxide",
                "carbon_dioxide_lbs",
                "carbon_dioxide_rank",
                "carbon_dioxide_rank_lbs",
                "direct_use",
                "direct_use_rank",
                "eop_sales",
                "eop_sales_rank",
                "fsp_sales_rank",
                "fsp_service_provider_sales",
                "generation_elect_utils",
                "generation_elect_utils_rank",
                "generation_ipp",
                "generation_ipp_rank",
                "net_generation",
                "net_generation_rank",
                "net_summer_capacity",
                "net_summer_capacity_rank",
                "nitrogen_oxide",
                "nitrogen_oxide_lbs",
                "nitrogen_oxide_rank",
                "nitrogen_oxide_rank_lbs",
                "prime_source",
                "sulfer_dioxide",
                "sulfer_dioxide_lbs",
                "sulfer_dioxide_rank",
                "sulfer_dioxide_rank_lbs",
                "total_retail_sales",
                "total_retail_sales_rank",
            ],
        },
        "state": {
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
                "district_of_columbia",
                "florida",
                "georgia",
                "hawaii",
                "idaho",
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
                "rhode_island",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "united_states",
                "utah",
                "vermont",
                "virginia",
                "washington",
                "west_virginia",
                "wisconsin",
                "wyoming",
            ],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_retail_price = Average Retail Price of Electricity (cents per kilowatthour); average_retail_price_rank = Average Retail Price of Electricity (U.S. Rank) (rank); capacity_elec_utilities = Net Summer Capacity, Electric Power Sector (megawatts); capacity_elect_utilities_rank = Average Retail Price of Electricity (U.S. Rank) (rank); capacity_ipp = Net Summer Capacity, Independent Power Producers and Industrial / Commercial Sectors (megawatts); capacity_ipp_rank = Net Summer Capacity, Independent Power Producers and Industrial / Commercial Sectors (U.S. Rank) (rank); carbon_dioxide = CO2 Emissions (thousand metric tons); carbon_dioxide_lbs = CO2 Emissions Rate per MWh (pounds per megawatthour); carbon_dioxide_rank = CO2 Emissions (U.S. Rank) (rank); carbon_dioxide_rank_lbs = CO2 Emissions Rate per MWh (U.S. Rank) (rank); direct_use = Direct Use of Generation by Commercial and Industrial Facilities (megawatthours); direct_use_rank = Direct Use of Generation by Commercial and Industrial Facilities (U.S. Rank) (rank); eop_sales = Retail Sales of Electrcity by Energy-Only Providers (megawatthours); eop_sales_rank = Retail Sales of Electrcity by Energy-Only Providers (U.S. Rank) (rank); fsp_sales_rank = Retail Sales of Electrcity by Full Service Providers and Electricity Sold Directly by Commercial and Industrial Facilities (U.S. Rank) (rank); fsp_service_provider_sales = Retail Sales of Electrcity by Full Service Providers and Electricity Sold Directly by Commercial and Industrial  Facilities (megawatthours); generation_elect_utils = Net Generation, Electric Power Sector (megawatthours); generation_elect_utils_rank = Net Generation, Electric Power Sector (U.S. Rank) (rank); generation_ipp = Net Generation, Independent Power Producers and Industrial / Commercial Sectors (megawatthours); generation_ipp_rank = Net Generation, Independent Power Producers and Industrial / Commercial Sectors (U.S. Rank) (rank); net_generation = Net Generation, All Sectors (megawatthours); net_generation_rank = Net Generation, All Sectors (U.S. Rank) (rank); net_summer_capacity = Net Summer Capacity, All Sectors (megawatts); net_summer_capacity_rank = Net Summer Capacity, All Sectors (U.S. Rank) (rank); nitrogen_oxide = NOx Emissions (short tons); nitrogen_oxide_lbs = NOx Emissions Rate per MWh (pounds per megawatthour); nitrogen_oxide_rank = NOx Emissions (U.S. Rank) (rank); nitrogen_oxide_rank_lbs = NOx Emissions Rate per MWh (U.S. Rank) (rank); prime_source; sulfer_dioxide = SO2 Emissions (short tons); sulfer_dioxide_lbs = SO2 Emissions Rate per MWh (pounds per megawatthour); sulfer_dioxide_rank = SO2 Emissions (U.S. Rank) (rank); sulfer_dioxide_rank_lbs = SO2 Emissions Rate per MWh (U.S. Rank) (rank); total_retail_sales = Retail Sales of Electricity, Total Electric Industry  (megawatthours); total_retail_sales_rank = Retail Sales of Electricity, Total Electric Industry (U.S. Rank) (rank).",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )


class EiaStateElectricityProfilesStateRankingsForKeyStatisticsData(EiaApiData):
    """State Rankings for Key Statistics. State rankings for key electricity statistics by state Source: Forms EIA-860, EIA-861, EIA-923 Product: State Electricity Profiles, Table 1"""

    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    average_retail_price: float | None = Field(
        default=None,
        description="Average Retail Price of Electricity (cents per kilowatthour). Withheld or unavailable values return as null.",
    )
    average_retail_price_rank: float | None = Field(
        default=None,
        description="Average Retail Price of Electricity (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    capacity_elec_utilities: float | None = Field(
        default=None,
        description="Net Summer Capacity, Electric Power Sector (megawatts). Withheld or unavailable values return as null.",
    )
    capacity_elect_utilities_rank: float | None = Field(
        default=None,
        description="Average Retail Price of Electricity (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    capacity_ipp: float | None = Field(
        default=None,
        description="Net Summer Capacity, Independent Power Producers and Industrial / Commercial Sectors (megawatts). Withheld or unavailable values return as null.",
    )
    capacity_ipp_rank: float | None = Field(
        default=None,
        description="Net Summer Capacity, Independent Power Producers and Industrial / Commercial Sectors (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    carbon_dioxide: float | None = Field(
        default=None,
        description="CO2 Emissions (thousand metric tons). Withheld or unavailable values return as null.",
    )
    carbon_dioxide_lbs: float | None = Field(
        default=None,
        description="CO2 Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    carbon_dioxide_rank: float | None = Field(
        default=None,
        description="CO2 Emissions (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    carbon_dioxide_rank_lbs: float | None = Field(
        default=None,
        description="CO2 Emissions Rate per MWh (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    direct_use: float | None = Field(
        default=None,
        description="Direct Use of Generation by Commercial and Industrial Facilities (megawatthours). Withheld or unavailable values return as null.",
    )
    direct_use_rank: float | None = Field(
        default=None,
        description="Direct Use of Generation by Commercial and Industrial Facilities (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    eop_sales: float | None = Field(
        default=None,
        description="Retail Sales of Electrcity by Energy-Only Providers (megawatthours). Withheld or unavailable values return as null.",
    )
    eop_sales_rank: float | None = Field(
        default=None,
        description="Retail Sales of Electrcity by Energy-Only Providers (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    fsp_sales_rank: float | None = Field(
        default=None,
        description="Retail Sales of Electrcity by Full Service Providers and Electricity Sold Directly by Commercial and Industrial Facilities (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    fsp_service_provider_sales: float | None = Field(
        default=None,
        description="Retail Sales of Electrcity by Full Service Providers and Electricity Sold Directly by Commercial and Industrial  Facilities (megawatthours). Withheld or unavailable values return as null.",
    )
    generation_elect_utils: float | None = Field(
        default=None,
        description="Net Generation, Electric Power Sector (megawatthours). Withheld or unavailable values return as null.",
    )
    generation_elect_utils_rank: float | None = Field(
        default=None,
        description="Net Generation, Electric Power Sector (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    generation_ipp: float | None = Field(
        default=None,
        description="Net Generation, Independent Power Producers and Industrial / Commercial Sectors (megawatthours). Withheld or unavailable values return as null.",
    )
    generation_ipp_rank: float | None = Field(
        default=None,
        description="Net Generation, Independent Power Producers and Industrial / Commercial Sectors (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    net_generation: float | None = Field(
        default=None,
        description="Net Generation, All Sectors (megawatthours). Withheld or unavailable values return as null.",
    )
    net_generation_rank: float | None = Field(
        default=None,
        description="Net Generation, All Sectors (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    net_summer_capacity: float | None = Field(
        default=None,
        description="Net Summer Capacity, All Sectors (megawatts). Withheld or unavailable values return as null.",
    )
    net_summer_capacity_rank: float | None = Field(
        default=None,
        description="Net Summer Capacity, All Sectors (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    nitrogen_oxide: float | None = Field(
        default=None,
        description="NOx Emissions (short tons). Withheld or unavailable values return as null.",
    )
    nitrogen_oxide_lbs: float | None = Field(
        default=None,
        description="NOx Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    nitrogen_oxide_rank: float | None = Field(
        default=None,
        description="NOx Emissions (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    nitrogen_oxide_rank_lbs: float | None = Field(
        default=None,
        description="NOx Emissions Rate per MWh (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    prime_source: str | None = Field(
        default=None,
        description="Prime Source",
    )
    sulfer_dioxide: float | None = Field(
        default=None,
        description="SO2 Emissions (short tons). Withheld or unavailable values return as null.",
    )
    sulfer_dioxide_lbs: float | None = Field(
        default=None,
        description="SO2 Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    sulfer_dioxide_rank: float | None = Field(
        default=None,
        description="SO2 Emissions (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    sulfer_dioxide_rank_lbs: float | None = Field(
        default=None,
        description="SO2 Emissions Rate per MWh (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )
    total_retail_sales: float | None = Field(
        default=None,
        description="Retail Sales of Electricity, Total Electric Industry  (megawatthours). Withheld or unavailable values return as null.",
    )
    total_retail_sales_rank: float | None = Field(
        default=None,
        description="Retail Sales of Electricity, Total Electric Industry (U.S. Rank) (rank). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesStateRankingsForKeyStatisticsFetcher(
    Fetcher[
        EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams,
        list[EiaStateElectricityProfilesStateRankingsForKeyStatisticsData],
    ]
):
    """State Rankings for Key Statistics fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesStateRankingsForKeyStatisticsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaStateElectricityProfilesStateRankingsForKeyStatisticsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesStateRankingsForKeyStatisticsData, query, data
        )
