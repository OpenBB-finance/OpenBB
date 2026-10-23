"""Hourly Demand, Demand Forecast, Generation, and Interchange model."""

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


class EiaElectricityGridDemandQueryParams(EiaApiQueryParams):
    """Hourly Demand, Demand Forecast, Generation, and Interchange. Hourly demand, day-ahead demand forecast, net generation, and interchange by balancing authority. Source: Form EIA-930 Product: Hourly Electric Grid Monitor

    Source: https://www.eia.gov/opendata/browser/electricity/rto/region-data
    """

    __group__ = "electricity_grid"
    __dataset__ = "demand"
    __json_schema_extra__ = {
        "respondent": {
            "multiple_items_allowed": True,
            "choices": [
                "alcoa_power_generating_yadkin_division",
                "arizona_public_service_company",
                "arlington_valley",
                "associated_electric_cooperative",
                "avangrid_renewables",
                "avista_corporation",
                "balancing_authority_of_northern_california",
                "bonneville_power_administration",
                "california",
                "california_independent_system_operator",
                "carolinas",
                "central",
                "city_of_homestead",
                "city_of_tacoma_department_of_public_utilities_light_division",
                "city_of_tallahassee",
                "dominion_energy_south_carolina",
                "duke_energy_carolinas",
                "duke_energy_florida",
                "duke_energy_progress_east",
                "duke_energy_progress_west",
                "el_paso_electric_company",
                "electric_energy",
                "electric_reliability_council_of_texas",
                "florida",
                "florida_municipal_power_pool",
                "florida_power_and_light_co",
                "gainesville_regional_utilities",
                "gridliance",
                "gridforce_energy_management",
                "griffith_energy",
                "iso_new_england",
                "idaho_power_company",
                "imperial_irrigation_district",
                "jea",
                "lg_and_e_and_ku_services_company_as_agent_for_louisville",
                "los_angeles_department_of_water_and_power",
                "mid_atlantic",
                "midcontinent_independent_system_operator",
                "midwest",
                "naturener_power_watch",
                "naturener_wind_watch",
                "nevada_power_company",
                "new_england",
                "new_harquahala_generating_company",
                "new_york",
                "new_york_independent_system_operator",
                "northwestern_corporation",
                "northwest",
                "pjm_interconnection",
                "pud_no_1_of_douglas_county",
                "pacificorp_east",
                "pacificorp_west",
                "portland_general_electric_company",
                "powersouth_energy_cooperative",
                "public_service_company_of_colorado",
                "public_service_company_of_new_mexico",
                "public_utility_district_no_1_of_chelan_county",
                "public_utility_district_no_2_of_grant_county_washington",
                "puget_sound_energy",
                "salt_river_project_agricultural_improvement_and_power",
                "seattle_city_light",
                "seminole_electric_cooperative",
                "sikeston_board_of_municipal_utilities",
                "south_carolina_public_service_authority",
                "southeast",
                "southeastern_power_administration",
                "southern_company_services_trans",
                "southwest",
                "southwest_power_pool",
                "southwestern_power_administration",
                "tampa_electric_company",
                "tennessee",
                "tennessee_valley_authority",
                "texas",
                "tucson_electric_power",
                "turlock_irrigation_district",
                "united_states_lower_48",
                "utilities_commission_of_new_smyrna_beach",
                "western_area_power_administration_desert_southwest_region",
                "western_area_power_administration_rocky_mountain_region",
                "western_area_power_administration_upper_great_plains_west",
            ],
        },
        "series_type": {
            "multiple_items_allowed": True,
            "choices": [
                "day_ahead_demand_forecast",
                "demand",
                "net_generation",
                "total_interchange",
            ],
        },
        "timezone": {
            "multiple_items_allowed": True,
            "choices": ["arizona", "central", "eastern", "mountain", "pacific"],
        },
    }

    frequency: Literal["daily", "hourly", "local-hourly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'hourly'.",
    )
    respondent: str | None = Field(
        default=None,
        description="Balancing Authority / Region filter. Accepts a comma-separated list of values.",
    )
    series_type: (
        Literal[
            "day_ahead_demand_forecast", "demand", "net_generation", "total_interchange"
        ]
        | None
    ) = Field(
        default=None,
        description="Metric filter.",
    )
    timezone: Literal["arizona", "central", "eastern", "mountain", "pacific"] | None = (
        Field(
            default=None,
            description="Time Zone for Determining Date filter. Only applies to frequency: daily.",
        )
    )


class EiaElectricityGridDemandData(EiaApiData):
    """Hourly Demand, Demand Forecast, Generation, and Interchange. Hourly demand, day-ahead demand forecast, net generation, and interchange by balancing authority. Source: Form EIA-930 Product: Hourly Electric Grid Monitor"""

    respondent: str | None = Field(
        default=None,
        description="Balancing Authority / Region code.",
    )
    respondent_name: str | None = Field(
        default=None,
        description="Balancing Authority / Region name.",
    )
    series_type: str | None = Field(
        default=None,
        description="Metric code.",
    )
    series_type_name: str | None = Field(
        default=None,
        description="Metric name.",
    )
    timezone: str | None = Field(
        default=None,
        description="Time Zone for Determining Date code.",
    )
    timezone_name: str | None = Field(
        default=None,
        description="Time Zone for Determining Date name.",
    )
    value: float | None = Field(
        default=None,
        description="Demand, Demand Forecast, Net Generation, or Interchange (megawatthours). Withheld or unavailable values return as null.",
    )


class EiaElectricityGridDemandFetcher(
    Fetcher[EiaElectricityGridDemandQueryParams, list[EiaElectricityGridDemandData]]
):
    """Hourly Demand, Demand Forecast, Generation, and Interchange fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaElectricityGridDemandQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaElectricityGridDemandQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaElectricityGridDemandQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityGridDemandQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityGridDemandData]:
        """Transform the data."""
        return transform_dataset_data(EiaElectricityGridDemandData, query, data)
