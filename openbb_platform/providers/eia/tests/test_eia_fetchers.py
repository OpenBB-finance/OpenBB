"""EIA Fetcher Tests."""

import re
from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_us_eia.models.data_browser import EiaDataBrowserFetcher
from openbb_us_eia.models.petroleum_status_report import EiaPetroleumStatusReportFetcher
from openbb_us_eia.models.registry import DATASET_FETCHERS
from openbb_us_eia.models.short_term_energy_outlook import (
    EiaShortTermEnergyOutlookFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def scrub_string(key):
    """Scrub a string from the response."""

    def before_record_response(response):
        response["headers"][key] = response["headers"].update({key: "MOCK_VALUE"})
        return response

    return before_record_response


def scrub_api_key(response):
    """Scrub the API key echoed inside the response body."""
    body = response["body"]["string"]
    is_bytes = isinstance(body, bytes)
    if is_bytes:
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            return response
    else:
        text = body
    text = re.sub(r'"api_key":\s*"[^"]*"', '"api_key":"MOCK_API_KEY"', text)
    response["body"]["string"] = text.encode("utf-8") if is_bytes else text
    return response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
        "decode_compressed_response": True,
        "before_record_response": [
            scrub_api_key,
            scrub_string("X-Amz-Cf-Id"),
            scrub_string("Etag"),
            scrub_string("Via"),
            scrub_string("X-Amz-Cf-Pop"),
            scrub_string("X-Cache"),
            scrub_string("X-Api-Umbrella-Request-Id"),
            scrub_string("X-Vcap-Request-Id"),
        ],
    }


@pytest.mark.record_http
def test_eia_petroleum_status_report_fetcher(credentials=None):
    """Test the EIA petroleum status report fetcher."""
    params = {
        "category": "crude_petroleum_stocks",
        "table": "all",
        "start_date": date(2024, 1, 5),
        "end_date": date(2024, 3, 29),
    }

    fetcher = EiaPetroleumStatusReportFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_short_term_energy_outlook_fetcher(credentials=test_credentials):
    """Test the EIA short term energy outlook fetcher."""
    params = {
        "table": "10b",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 4, 1),
        "frequency": "quarter",
    }

    fetcher = EiaShortTermEnergyOutlookFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_data_browser_fetcher(credentials=test_credentials):
    """Test the EIA data browser fetcher."""
    params = {
        "route": "petroleum/pri/spt",
        "frequency": "monthly",
        "facets": "product:EPCBRENT",
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 3, 1),
    }

    fetcher = EiaDataBrowserFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_aeo_fetcher(credentials=test_credentials):
    """Test the EIA aeo fetcher."""
    params = {
        "release": "2026",
        "history": "projection",
        "region": "united_states",
        "scenario": "alternative_electricity",
        "series": "NA_NA_NA_NA_NA_NA_NA_NA",
        "table": "73",
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaAeo"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_aggregate_production_fetcher(credentials=test_credentials):
    """Test the EIA coal aggregate production fetcher."""
    params = {
        "coal_rank": "subbituminous",
        "mine_type": "all",
        "state_region": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalAggregateProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_by_mine_by_plant_fetcher(credentials=test_credentials):
    """Test the EIA coal by mine by plant fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "all",
        "coal_supplier": "TWENTY MILE",
        "mine": "100114",
        "mine_state": "alabama",
        "plant": "genoa",
        "plant_state": "wisconsin",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalByMineByPlant"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_consumption_and_quality_fetcher(credentials=test_credentials):
    """Test the EIA coal consumption and quality fetcher."""
    params = {
        "frequency": "annual",
        "sector": "other_industrial",
        "state_region": "alaska",
        "start_date": date(2000, 1, 1),
        "end_date": date(2000, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalConsumptionAndQuality"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_exports_imports_quantity_price_fetcher(credentials=test_credentials):
    """Test the EIA coal exports imports quantity price fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "coke",
        "country": "mexico",
        "customs_district": "baltimore_md",
        "export_import_type": "exports",
        "start_date": date(2000, 1, 1),
        "end_date": date(2000, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalExportsImportsQuantityPrice"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_market_sales_price_fetcher(credentials=test_credentials):
    """Test the EIA coal market sales price fetcher."""
    params = {
        "market_type": "open_market",
        "state_region": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalMarketSalesPrice"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_mine_aggregates_fetcher(credentials=test_credentials):
    """Test the EIA coal mine aggregates fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "bituminous",
        "mine": "100114",
        "mine_state": "alabama",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalMineAggregates"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_mine_production_fetcher(credentials=test_credentials):
    """Test the EIA coal mine production fetcher."""
    params = {
        "census_region": "east_south_central",
        "coal_rank": "preparation_plant",
        "mine": "100329",
        "mine_county": "jefferson",
        "mine_region": "south",
        "mine_status": "active",
        "mine_type": "surface",
        "mississippi_region": "east_of_mississippi_river",
        "state_region": "alabama",
        "supply_region": "appalachia_southern",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalMineProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_mine_state_aggregates_fetcher(credentials=test_credentials):
    """Test the EIA coal mine state aggregates fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "subbituminous",
        "mine_state": "alaska",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalMineStateAggregates"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_plant_aggregates_fetcher(credentials=test_credentials):
    """Test the EIA coal plant aggregates fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "bituminous",
        "plant": "barry",
        "state_region": "overseas",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalPlantAggregates"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_plant_state_aggregates_fetcher(credentials=test_credentials):
    """Test the EIA coal plant state aggregates fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "subbituminous",
        "plant_state": "alaska",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalPlantStateAggregates"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_price_by_rank_fetcher(credentials=test_credentials):
    """Test the EIA coal price by rank fetcher."""
    params = {
        "coal_rank": "subbituminous",
        "state_region": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalPriceByRank"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_receipts_fetcher(credentials=test_credentials):
    """Test the EIA coal receipts fetcher."""
    params = {
        "frequency": "annual",
        "coal_rank": "bituminous",
        "coal_supplier": "TWENTY MILE",
        "contract_type": "spot_market_purchase",
        "mine": "100114",
        "mine_basin": "appalachia_southern",
        "mine_county": "127",
        "mine_state": "alabama",
        "mine_type": "surface",
        "plant": "genoa",
        "plant_state": "wisconsin",
        "transportation_mode": "rail",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalReceipts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_coal_reserves_capacity_fetcher(credentials=test_credentials):
    """Test the EIA coal reserves capacity fetcher."""
    params = {
        "mine_type": "surface",
        "state_region": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCoalReservesCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_crude_oil_imports_fetcher(credentials=test_credentials):
    """Test the EIA crude oil imports fetcher."""
    params = {
        "frequency": "monthly",
        "destination": "padd5",
        "destination_type": "port_padd",
        "grade": "light_sour",
        "origin": "united_arab_emirates",
        "origin_type": "country",
        "start_date": date(2009, 1, 1),
        "end_date": date(2009, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaCrudeOilImports"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_capacity_by_region_fetcher(credentials=test_credentials):
    """Test the EIA densified biomass capacity by region fetcher."""
    params = {
        "region": "east",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassCapacityByRegion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_characteristics_by_region_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass characteristics by region fetcher."""
    params = {
        "fuel_type": "wood_pellets_premium_standard",
        "region": "east",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassCharacteristicsByRegion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_export_sales_and_price_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass export sales and price fetcher."""
    params = {
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassExportSalesAndPrice"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_feedstocks_and_costs_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass feedstocks and costs fetcher."""
    params = {
        "fuel_type": "other_residuals",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassFeedstocksAndCosts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_inventories_by_region_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass inventories by region fetcher."""
    params = {
        "fuel_type": "compressed_bricks_log",
        "region": "east",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassInventoriesByRegion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_production_by_region_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass production by region fetcher."""
    params = {
        "fuel_type": "compressed_bricks_log",
        "region": "east",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassProductionByRegion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_sales_and_price_by_region_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass sales and price by region fetcher."""
    params = {
        "region": "east",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassSalesAndPriceByRegion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_densified_biomass_wood_pellet_plant_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA densified biomass wood pellet plant capacity fetcher."""
    params = {
        "region": "east",
        "respondent": "allegheny_pellet_corporation",
        "state": "pennsylvania",
        "status": "currently_operating",
        "start_date": date(2016, 1, 1),
        "end_date": date(2016, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaDensifiedBiomassWoodPelletPlantCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_electric_power_operations_fetcher(
    credentials=test_credentials,
):
    """Test the EIA electricity electric power operations fetcher."""
    params = {
        "frequency": "monthly",
        "fuel": "all_fuels",
        "sector": "electric_utility",
        "state": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityElectricPowerOperations"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_electric_power_operations_for_individual_power_plants_fetcher(
    credentials=test_credentials,
):
    """Test the EIA electricity electric power operations for individual power plants fetcher."""
    params = {
        "frequency": "monthly",
        "fuel": "total",
        "fuel_type": "total",
        "plant": "2",
        "prime_mover": "all",
        "state": "alabama",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaElectricityElectricPowerOperationsForIndividualPowerPlants"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_electricity_sales_to_ultimate_customers_fetcher(
    credentials=test_credentials,
):
    """Test the EIA electricity electricity sales to ultimate customers fetcher."""
    params = {
        "frequency": "monthly",
        "sector": "all_sectors",
        "state": "alaska",
        "start_date": date(2001, 1, 1),
        "end_date": date(2001, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityElectricitySalesToUltimateCustomers"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_grid_demand_fetcher(credentials=test_credentials):
    """Test the EIA electricity grid demand fetcher."""
    params = {
        "frequency": "hourly",
        "respondent": "powersouth_energy_cooperative",
        "series_type": "demand",
        "start_date": date(2019, 1, 2),
        "end_date": date(2019, 1, 2),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityGridDemand"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_grid_demand_by_subregion_fetcher(credentials=test_credentials):
    """Test the EIA electricity grid demand by subregion fetcher."""
    params = {
        "frequency": "hourly",
        "parent": "california_independent_system_operator",
        "subregion": "pacific_gas_and_electric",
        "start_date": date(2019, 1, 2),
        "end_date": date(2019, 1, 2),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityGridDemandBySubregion"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_grid_generation_by_fuel_fetcher(credentials=test_credentials):
    """Test the EIA electricity grid generation by fuel fetcher."""
    params = {
        "frequency": "hourly",
        "fuel_type": "coal",
        "respondent": "powersouth_energy_cooperative",
        "start_date": date(2019, 1, 2),
        "end_date": date(2019, 1, 2),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityGridGenerationByFuel"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_grid_interchange_fetcher(credentials=test_credentials):
    """Test the EIA electricity grid interchange fetcher."""
    params = {
        "frequency": "hourly",
        "from_ba": "powersouth_energy_cooperative",
        "to_ba": "midcontinent_independent_system_operator",
        "start_date": date(2019, 1, 2),
        "end_date": date(2019, 1, 2),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityGridInterchange"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_electricity_inventory_of_operable_generators_fetcher(
    credentials=test_credentials,
):
    """Test the EIA electricity inventory of operable generators fetcher."""
    params = {
        "energy_source": "water",
        "generator": "1",
        "plant": "2",
        "prime_mover": "hy",
        "sector": "electric_utility",
        "state": "alabama",
        "status": "operating",
        "technology": "conventional_hydroelectric",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaElectricityInventoryOfOperableGenerators"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_ieo_fetcher(credentials=test_credentials):
    """Test the EIA ieo fetcher."""
    params = {
        "release": "2023",
        "history": "historic",
        "region": "middle_east",
        "scenario": "high_economic_growth",
        "series": "cnsm_bl_cm_cl_qbtu",
        "table": "buildings_delivered_energy_consumption_by_end_use_sector",
        "start_date": date(2020, 1, 1),
        "end_date": date(2020, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaIeo"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_international_fetcher(credentials=test_credentials):
    """Test the EIA international fetcher."""
    params = {
        "frequency": "monthly",
        "activity": "production",
        "country": "angola",
        "country_type": "country",
        "product": "crude_oil_including_lease_condensate",
        "unit": "thousand_barrels_per_day",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaInternational"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_associated_dissolved_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas associated dissolved proved reserves fetcher."""
    params = {
        "process": "associated_dissolved_proved_reserves",
        "region": "us",
        "series": "us_associated_dissolved_natural_gas_wet_after_lease_separation_proved_reserves_billion_cubic_feet",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasAssociatedDissolvedProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_average_depth_of_crude_oil_and_natural_gas_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas average depth of crude oil and natural gas wells fetcher."""
    params = {
        "process": "average_depth_of_exploratory_and_developmental_wells_drilled",
        "product": "wells_total",
        "series": "us_average_depth_of_crude_oil_natural_gas_and_dry_exploratory_and_developmental_wells_drilled_feet_per_well",
        "start_date": date(1949, 1, 1),
        "end_date": date(1949, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWells"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_coalbed_methane_fetcher(credentials=test_credentials):
    """Test the EIA natural gas coalbed methane fetcher."""
    params = {
        "process": "coalbed_methane_proved_reserves",
        "region": "us",
        "series": "us_coalbed_methane_proved_reserves",
        "start_date": date(1989, 1, 1),
        "end_date": date(1989, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasCoalbedMethane"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_coalbed_methane_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas coalbed methane production fetcher."""
    params = {
        "region": "us",
        "series": "us_coalbed_methane_production",
        "start_date": date(1989, 1, 1),
        "end_date": date(1989, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasCoalbedMethaneProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_costs_of_crude_oil_and_natural_gas_wells_drilled_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas costs of crude oil and natural gas wells drilled fetcher."""
    params = {
        "process": "real_cost_per_foot",
        "product": "wells_total",
        "series": "us_real_cost_per_foot_of_crude_oil_natural_gas_and_dry",
        "start_date": date(1960, 1, 1),
        "end_date": date(1960, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasCostsOfCrudeOilAndNaturalGasWellsDrilled"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_crude_oil_and_natural_gas_drilling_activity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas crude oil and natural gas drilling activity fetcher."""
    params = {
        "frequency": "monthly",
        "process": "active_well_service_rigs_in_operation",
        "product": "crude_oil_and_natural_gas",
        "region": "us",
        "series": "us_crude_oil_and_natural_gas_active_well_service_rigs_in",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasCrudeOilAndNaturalGasDrillingActivity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_crude_oil_and_natural_gas_exploratory_and_development_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas crude oil and natural gas exploratory and development wells fetcher."""
    params = {
        "frequency": "monthly",
        "process": "exploratory_and_developmental_wells_drilled",
        "product": "wells_total",
        "series": "us_crude_oil_natural_gas_and_dry_exploratory_and",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasCrudeOilAndNaturalGasExploratoryAndDevelopmentWells"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_crude_oil_plus_lease_condensate_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas crude oil plus lease condensate fetcher."""
    params = {
        "process": "proved_reserves",
        "region": "us",
        "series": "us_crude_oil_lease_condensate_proved_reserves",
        "start_date": date(2009, 1, 1),
        "end_date": date(2009, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasCrudeOilPlusLeaseCondensate"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_dry_natural_gas_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas dry natural gas proved reserves fetcher."""
    params = {
        "process": "dry_expected_future_production",
        "region": "us",
        "series": "us_dry_natural_gas_expected_future_production",
        "start_date": date(1925, 1, 1),
        "end_date": date(1925, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasDryNaturalGasProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_federal_offshore_gulf_of_america_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas federal offshore gulf of america proved reserves fetcher."""
    params = {
        "process": "proved_reserves",
        "product": "crude_oil",
        "series": "gulf_of_america_federal_offshore_crude_oil_proved_reserves_million_barrels",
        "start_date": date(1992, 1, 1),
        "end_date": date(1992, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReserves"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_footage_drilled_for_crude_oil_and_natural_gas_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas footage drilled for crude oil and natural gas wells fetcher."""
    params = {
        "process": "footage_drilled_for_developmental_wells",
        "product": "wells_total",
        "series": "us_footage_drilled_for_crude_oil_natural_gas_and_dry_developmental_wells_thousand_feet",
        "start_date": date(1949, 1, 1),
        "end_date": date(1949, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWells"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_gulf_of_america_federal_offshore_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas gulf of america federal offshore production fetcher."""
    params = {
        "process": "production_from_reserves",
        "product": "crude_oil",
        "series": "gulf_of_america_federal_offshore_crude_oil_production",
        "start_date": date(1992, 1, 1),
        "end_date": date(1992, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasGulfOfAmericaFederalOffshoreProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_heat_content_of_natural_gas_consumed_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas heat content of natural gas consumed fetcher."""
    params = {
        "frequency": "monthly",
        "region": "us",
        "series": "us_heat_content_of_natural_gas_deliveries_to_consumers",
        "start_date": date(2012, 1, 1),
        "end_date": date(2012, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasHeatContentOfNaturalGasConsumed"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_international_interstate_movements_of_natural_gas_by_state_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas international interstate movements of natural gas by state fetcher."""
    params = {
        "process": "exports_intransit",
        "region": "us",
        "series": "NA1280_NUS_2",
        "start_date": date(1930, 1, 1),
        "end_date": date(1930, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByState"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_lease_condensate_fetcher(credentials=test_credentials):
    """Test the EIA natural gas lease condensate fetcher."""
    params = {
        "process": "lease_condensate_proved_reserves",
        "region": "us",
        "series": "us_natural_gas_liquids_lease_condensate_proved_reserves_million_barrels",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasLeaseCondensate"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_lease_condensate_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas lease condensate production fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_liquids_lease_condensate_reserves_based",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasLeaseCondensateProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_lng_storage_additions_and_withdrawals_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas lng storage additions and withdrawals fetcher."""
    params = {
        "process": "lng_storage_net_withdrawals",
        "region": "us",
        "series": "us_natural_gas_lng_storage_net_withdrawals",
        "start_date": date(1969, 1, 1),
        "end_date": date(1969, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasLngStorageAdditionsAndWithdrawals"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_maximum_us_active_seismic_crew_counts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas maximum us active seismic crew counts fetcher."""
    params = {
        "process": "maximum_number_of_active_crews_engaged_in_sismic_surveying",
        "region": "us",
        "series": "us_maximum_number_of_active_crews_engaged_in_seismic",
        "start_date": date(2000, 1, 1),
        "end_date": date(2000, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasMaximumUsActiveSeismicCrewCounts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_annual_supply_disposition_by_state_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas annual supply disposition by state fetcher."""
    params = {
        "frequency": "monthly",
        "process": "underground_storage_injections",
        "region": "us",
        "series": "us_total_natural_gas_injections_into_underground_storage",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasNaturalGasAnnualSupplyDispositionByState"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_consumption_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas consumption by end use fetcher."""
    params = {
        "frequency": "monthly",
        "process": "commercial_consumption",
        "region": "us",
        "series": "natural_gas_deliveries_to_commercial_consumers_in_the_us",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasConsumptionByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_delivered_for_the_account_of_others_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas delivered for the account of others fetcher."""
    params = {
        "process": "delivered_to_industrial_consumers_for_the_account_of_others",
        "region": "us",
        "series": "us_natural_gas_delivered_to_industrial_consumers_for_the",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthers"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_gross_withdrawals_and_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas gross withdrawals and production fetcher."""
    params = {
        "frequency": "monthly",
        "process": "removed_from_natural_gas",
        "region": "us",
        "series": "us_nonhydrocarbon_gases_removed_from_natural_gas",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasGrossWithdrawalsAndProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_liquids_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas liquids proved reserves fetcher."""
    params = {
        "process": "proved_reserves",
        "region": "us",
        "series": "us_natural_gas_plant_liquids_proved_reserves",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasLiquidsProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_plant_liquids_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas plant liquids production fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_plant_liquids_reserves_based_production",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasPlantLiquidsProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_plant_processing_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas plant processing fetcher."""
    params = {
        "frequency": "monthly",
        "region": "us",
        "series": "us_natural_gas_plant_liquids_production",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasPlantProcessing"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_prices_fetcher(credentials=test_credentials):
    """Test the EIA natural gas natural gas prices fetcher."""
    params = {
        "frequency": "monthly",
        "process": "price_delivered_to_residential_consumers",
        "region": "us",
        "series": "us_price_of_natural_gas_delivered_to_residential_consumers",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasPrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_proved_reserves_wet_after_lease_separation_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas proved reserves wet after lease separation fetcher."""
    params = {
        "process": "wet_after_lease_separation_reserves_revision_increases",
        "region": "us",
        "series": "us_natural_gas_wet_after_lease_separation_reserves_revision_increases_billion_cubic_feet",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparation"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_reserves_summary_as_of_dec31_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas reserves summary as of dec31 fetcher."""
    params = {
        "process": "dry_expected_future_production",
        "product": "natural_gas",
        "region": "us",
        "series": "us_dry_natural_gas_expected_future_production",
        "start_date": date(1925, 1, 1),
        "end_date": date(1925, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasReservesSummaryAsOfDec31"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_spot_and_futures_prices_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas spot and futures prices fetcher."""
    params = {
        "frequency": "weekly",
        "process": "future_contract_4",
        "region": "new_york_city",
        "series": "natural_gas_futures_contract_4",
        "start_date": date(1993, 12, 24),
        "end_date": date(1993, 12, 24),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasSpotAndFuturesPrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_summary_fetcher(credentials=test_credentials):
    """Test the EIA natural gas natural gas summary fetcher."""
    params = {
        "frequency": "monthly",
        "process": "price_delivered_to_residential_consumers",
        "region": "us",
        "series": "N3010US3",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNaturalGasSummary"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_natural_gas_wellhead_value_and_marketed_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas natural gas wellhead value and marketed production fetcher."""
    params = {
        "frequency": "monthly",
        "process": "marketed_production",
        "region": "us",
        "series": "us_natural_gas_marketed_production",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasNaturalGasWellheadValueAndMarketedProduction"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_nonassociated_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas nonassociated proved reserves fetcher."""
    params = {
        "process": "nonassociated_proved_reserves",
        "region": "us",
        "series": "us_nonassociated_natural_gas_wet_after_lease_separation_proved_reserves_billion_cubic_feet",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNonassociatedProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_number_of_gas_producing_oil_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas number of gas producing oil wells fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_number_of_oil_wells",
        "start_date": date(2011, 1, 1),
        "end_date": date(2011, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNumberOfGasProducingOilWells"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_number_of_natural_gas_consumers_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas number of natural gas consumers fetcher."""
    params = {
        "process": "average_annual_consumption_per_commercial_consumer",
        "region": "us",
        "series": "us_natural_gas_average_annual_consumption_per_commercial",
        "start_date": date(1967, 1, 1),
        "end_date": date(1967, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNumberOfNaturalGasConsumers"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_number_of_producing_gas_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas number of producing gas wells fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_number_of_gas_and_gas_condensate_wells",
        "start_date": date(1989, 1, 1),
        "end_date": date(1989, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasNumberOfProducingGasWells"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_offshore_gross_withdrawals_of_natural_gas_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas offshore gross withdrawals of natural gas fetcher."""
    params = {
        "frequency": "monthly",
        "process": "withdrawals_from_gas_wells",
        "series": "federal_offshore_gulf_of_america_natural_gas_gross_withdrawals_from_gas_wells_mmcf",
        "start_date": date(1997, 1, 1),
        "end_date": date(1997, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGas"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_plant_liquids_in_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas plant liquids in proved reserves fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_plant_liquids_expected_future_production",
        "start_date": date(1979, 1, 1),
        "end_date": date(1979, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasPlantLiquidsInProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_proved_nonproducing_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas proved nonproducing reserves fetcher."""
    params = {
        "process": "associated_dissolved_reserves_in_nonproducing_reservoirs",
        "product": "natural_gas",
        "region": "na",
        "series": "gulf_of_america_federal_offshore_western_associated_dissolved_natural_gas_reserves_in_nonproducing_reservoirs_wet_bcf",
        "start_date": date(1996, 1, 1),
        "end_date": date(1996, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasProvedNonproducingReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_residential_and_commercial_prices_selected_states_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas residential and commercial prices selected states fetcher."""
    params = {
        "frequency": "monthly",
        "process": "price_delivered_to_residential_consumers",
        "region": "usa_dc",
        "series": "district_of_columbia_price_of_natural_gas_delivered_to",
        "start_date": date(1989, 1, 1),
        "end_date": date(1989, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasResidentialAndCommercialPricesSelectedStates"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_shale_gas_fetcher(credentials=test_credentials):
    """Test the EIA natural gas shale gas fetcher."""
    params = {
        "process": "shale_proved_reserves",
        "region": "us",
        "series": "us_shale_proved_reserves",
        "start_date": date(2007, 1, 1),
        "end_date": date(2007, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasShaleGas"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_shale_gas_production_fetcher(credentials=test_credentials):
    """Test the EIA natural gas shale gas production fetcher."""
    params = {
        "region": "us",
        "series": "us_shale_production",
        "start_date": date(2007, 1, 1),
        "end_date": date(2007, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasShaleGasProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_share_of_total_us_natural_gas_delivered_to_consumers_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas share of total us natural gas delivered to consumers fetcher."""
    params = {
        "process": "of_total_residential_deliveries",
        "region": "us",
        "series": "us_natural_gas_of_total_residential_deliveries",
        "start_date": date(1993, 1, 1),
        "end_date": date(1993, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasShareOfTotalUsNaturalGasDeliveredToConsumers"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_supplemental_gas_supplies_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas supplemental gas supplies fetcher."""
    params = {
        "frequency": "monthly",
        "start_date": date(1980, 1, 1),
        "end_date": date(1980, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasSupplementalGasSupplies"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_underground_natural_gas_storage_by_all_operators_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas underground natural gas storage by all operators fetcher."""
    params = {
        "frequency": "monthly",
        "process": "underground_storage_base_gas",
        "region": "us",
        "series": "us_total_natural_gas_in_underground_storage_base_gas_mmcf",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasUndergroundNaturalGasStorageByAllOperators"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_underground_natural_gas_storage_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas underground natural gas storage capacity fetcher."""
    params = {
        "frequency": "monthly",
        "process": "total_underground_storage_capacity",
        "region": "us",
        "series": "us_total_natural_gas_underground_storage_capacity",
        "start_date": date(1989, 1, 1),
        "end_date": date(1989, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasUndergroundNaturalGasStorageCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_exports_and_re_exports_by_country_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas exports and re exports by country fetcher."""
    params = {
        "frequency": "monthly",
        "process": "exports",
        "region": "us",
        "series": "us_natural_gas_exports",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasUsNaturalGasExportsAndReExportsByCountry"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_exports_and_re_exports_by_point_of_exit_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas exports and re exports by point of exit fetcher."""
    params = {
        "frequency": "monthly",
        "process": "liquefied_natural_gas_exports_price",
        "region": "jpn",
        "series": "price_of_liquefied_us_natural_gas_exports_to_japan",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExit"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_imports_by_country_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas imports by country fetcher."""
    params = {
        "frequency": "monthly",
        "process": "imports",
        "region": "us",
        "series": "us_natural_gas_imports",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasUsNaturalGasImportsByCountry"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_imports_by_point_of_entry_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas imports by point of entry fetcher."""
    params = {
        "frequency": "monthly",
        "process": "liquefied_natural_gas_imports",
        "region": "dza",
        "series": "us_liquefied_natural_gas_imports_from_algeria",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasUsNaturalGasImportsByPointOfEntry"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_imports_exports_by_state_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas imports exports by state fetcher."""
    params = {
        "frequency": "monthly",
        "process": "exports",
        "series": "us_natural_gas_exports",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasUsNaturalGasImportsExportsByState"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_natural_gas_monthly_supply_and_disposition_balance_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us natural gas monthly supply and disposition balance fetcher."""
    params = {
        "process": "net_imports",
        "region": "us",
        "series": "us_natural_gas_net_imports",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalance"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_us_underground_natural_gas_storage_by_storage_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas us underground natural gas storage by storage type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "underground_storage_base_gas",
        "series": "us_total_natural_gas_in_underground_storage_base_gas_mmcf",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaNaturalGasUsUndergroundNaturalGasStorageByStorageType"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_natural_gas_weekly_working_gas_in_underground_storage_fetcher(
    credentials=test_credentials,
):
    """Test the EIA natural gas weekly working gas in underground storage fetcher."""
    params = {
        "process": "non_salt_underground_storage_working_gas",
        "region": "na",
        "series": "weekly_nonsalt_region_natural_gas_working_underground",
        "start_date": date(2010, 1, 1),
        "end_date": date(2010, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNaturalGasWeeklyWorkingGasInUndergroundStorage"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_nuclear_outages_facility_level_nuclear_outages_fetcher(
    credentials=test_credentials,
):
    """Test the EIA nuclear outages facility level nuclear outages fetcher."""
    params = {
        "facility": "browns_ferry",
        "start_date": date(2007, 1, 1),
        "end_date": date(2007, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNuclearOutagesFacilityLevelNuclearOutages"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_nuclear_outages_generator_level_nuclear_outages_fetcher(
    credentials=test_credentials,
):
    """Test the EIA nuclear outages generator level nuclear outages fetcher."""
    params = {
        "facility": "browns_ferry",
        "generator": "1",
        "start_date": date(2007, 1, 1),
        "end_date": date(2007, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNuclearOutagesGeneratorLevelNuclearOutages"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_nuclear_outages_us_nuclear_outages_fetcher(credentials=test_credentials):
    """Test the EIA nuclear outages us nuclear outages fetcher."""
    params = {
        "start_date": date(2007, 1, 1),
        "end_date": date(2007, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaNuclearOutagesUsNuclearOutages"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_adjusted_distillate_fuel_oil_and_kerosene_sales_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum adjusted distillate fuel oil and kerosene sales by end use fetcher."""
    params = {
        "process": "adj_sales_deliveries_to_farm_consumers",
        "product": "no_2_diesel",
        "region": "us",
        "series": "K2DVAFNUS1",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumAdjustedDistillateFuelOilAndKeroseneSalesByEndUse"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_adjusted_sales_of_distillate_fuel_oil_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum adjusted sales of distillate fuel oil by end use fetcher."""
    params = {
        "process": "adj_sales_deliveries_total_to_end_users",
        "product": "distillate_fuel_oil",
        "region": "us",
        "series": "us_total_distillate_adj_sales_deliveries_total_to_end_users",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumAdjustedSalesOfDistillateFuelOilByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_adjusted_sales_of_kerosene_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum adjusted sales of kerosene by end use fetcher."""
    params = {
        "process": "adj_sales_deliveries_total_to_end_users",
        "region": "us",
        "series": "us_kerosene_adj_sales_deliveries_total_to_end_users",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumAdjustedSalesOfKeroseneByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_adjusted_sales_of_residual_fuel_oil_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum adjusted sales of residual fuel oil by end use fetcher."""
    params = {
        "process": "adj_sales_deliveries_total_to_end_users",
        "region": "us",
        "series": "us_residual_fuel_oil_adj_sales_deliveries_total_to_end_users",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_average_depth_of_crude_oil_and_natural_gas_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum average depth of crude oil and natural gas wells fetcher."""
    params = {
        "process": "average_depth_of_exploratory_and_developmental_wells_drilled",
        "product": "wells_total",
        "series": "us_average_depth_of_crude_oil_natural_gas_and_dry_exploratory_and_developmental_wells_drilled_feet_per_well",
        "start_date": date(1949, 1, 1),
        "end_date": date(1949, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumAverageDepthOfCrudeOilAndNaturalGasWells"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_biofuels_operable_production_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum biofuels operable production capacity fetcher."""
    params = {
        "product": "biodiesel",
        "series": "us_biodiesel_production_capacity",
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumBiofuelsOperableProductionCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_blender_net_input_fetcher(credentials=test_credentials):
    """Test the EIA petroleum blender net input fetcher."""
    params = {
        "frequency": "monthly",
        "product": "gasoline_blending_components",
        "region": "us",
        "series": "us_blender_net_input_of_gasoline_blending_components_thousand_barrels",
        "start_date": date(2005, 1, 1),
        "end_date": date(2005, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumBlenderNetInput"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_blender_net_production_fetcher(credentials=test_credentials):
    """Test the EIA petroleum blender net production fetcher."""
    params = {
        "frequency": "monthly",
        "product": "reformulated_motor_gasoline_with_alcohol",
        "region": "us",
        "series": "us_blender_net_production_of_reformulated_motor_gasoline_with_fuel_alcohol_thousand_barrels",
        "start_date": date(2005, 1, 1),
        "end_date": date(2005, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumBlenderNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_costs_of_crude_oil_and_natural_gas_wells_drilled_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum costs of crude oil and natural gas wells drilled fetcher."""
    params = {
        "process": "real_cost_per_foot",
        "product": "wells_total",
        "series": "us_real_cost_per_foot_of_crude_oil_natural_gas_and_dry",
        "start_date": date(1960, 1, 1),
        "end_date": date(1960, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilled"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_first_purchase_prices_selected_streams_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude first purchase prices selected streams fetcher."""
    params = {
        "frequency": "monthly",
        "product": "ans_crude_oil",
        "region": "usa_ak",
        "series": "alaska_north_slope_first_purchase_price",
        "start_date": date(1977, 7, 1),
        "end_date": date(1977, 7, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudeFirstPurchasePricesSelectedStreams"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_and_lease_condensate_production_by_api_gravity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude oil and lease condensate production by api gravity fetcher."""
    params = {
        "product": "crude_gravity_of_unkown",
        "region": "na",
        "series": "lower_48_states_crude_oil_and_lease_condensate_production_for_unknown_api_gravity_thousand_barrels_per_day",
        "start_date": date(2015, 1, 1),
        "end_date": date(2015, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravity"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_and_natural_gas_drilling_activity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude oil and natural gas drilling activity fetcher."""
    params = {
        "frequency": "monthly",
        "process": "active_well_service_rigs_in_operation",
        "product": "crude_oil_and_natural_gas",
        "region": "us",
        "series": "us_crude_oil_and_natural_gas_active_well_service_rigs_in",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudeOilAndNaturalGasDrillingActivity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_and_natural_gas_exploratory_and_development_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude oil and natural gas exploratory and development wells fetcher."""
    params = {
        "frequency": "monthly",
        "process": "exploratory_and_developmental_wells_drilled",
        "product": "wells_total",
        "series": "us_crude_oil_natural_gas_and_dry_exploratory_and",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumCrudeOilAndNaturalGasExploratoryAndDevelopmentWells"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_input_qualities_fetcher(credentials=test_credentials):
    """Test the EIA petroleum crude oil input qualities fetcher."""
    params = {
        "frequency": "monthly",
        "process": "refinery_inputs_average_api_gravity",
        "region": "na",
        "series": "indiana_illinois_kentucky_refinery_district_api_gravity_of",
        "start_date": date(1985, 1, 1),
        "end_date": date(1985, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudeOilInputQualities"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_production_fetcher(credentials=test_credentials):
    """Test the EIA petroleum crude oil production fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "us_field_production_of_crude_oil_thousand_barrels",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudeOilProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_proved_reserves_reserves_changes_and_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude oil proved reserves reserves changes and production fetcher."""
    params = {
        "process": "proved_reserves",
        "region": "us",
        "series": "us_crude_oil_proved_reserves",
        "start_date": date(1899, 1, 1),
        "end_date": date(1899, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumCrudeOilProvedReservesReservesChangesAndProduction"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_oil_stocks_at_tank_farms_pipelines_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude oil stocks at tank farms pipelines fetcher."""
    params = {
        "frequency": "monthly",
        "process": "stocks_at_tank_farms",
        "region": "padd_1",
        "series": "east_coast_crude_oil_stocks_at_tank_farms_and_pipelines",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudeOilStocksAtTankFarmsPipelines"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_crude_plus_lease_condensate_proved_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum crude plus lease condensate proved reserves fetcher."""
    params = {
        "process": "proved_reserves",
        "region": "us",
        "series": "us_crude_oil_lease_condensate_proved_reserves",
        "start_date": date(2009, 1, 1),
        "end_date": date(2009, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumCrudePlusLeaseCondensateProvedReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_distillate_fuel_oil_and_kerosene_sales_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum distillate fuel oil and kerosene sales by end use fetcher."""
    params = {
        "process": "commercial_consumption",
        "product": "no_2_fuel_oil_heating_oil",
        "region": "us",
        "series": "K2FVCSNUS1",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumDistillateFuelOilAndKeroseneSalesByEndUse"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_domestic_crude_oil_first_purchase_prices_by_api_gravity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum domestic crude oil first purchase prices by api gravity fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_gravity_20_0_percent_or_less",
        "series": "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_20_0_degrees_or_less_dollars_per_barrel",
        "start_date": date(1993, 10, 1),
        "end_date": date(1993, 10, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravity"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_domestic_crude_oil_first_purchase_prices_by_area_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum domestic crude oil first purchase prices by area fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "us_crude_oil_first_purchase_price",
        "start_date": date(1974, 1, 1),
        "end_date": date(1974, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumDomesticCrudeOilFirstPurchasePricesByArea"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_downstream_charge_capacity_of_operable_petroleum_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum downstream charge capacity of operable petroleum refineries fetcher."""
    params = {
        "process": "refinery_catalytic_cracking_fresh_feed_downstream_charge",
        "region": "pri",
        "series": "8_NA_8CCF_NPZ_5",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumDownstreamChargeCapacityOfOperablePetroleumRefineries"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_downstream_processing_of_fresh_feed_input_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum downstream processing of fresh feed input fetcher."""
    params = {
        "frequency": "monthly",
        "process": "downstream_delayed_fluid_coking",
        "region": "na",
        "series": "refining_district_indiana_illinois_kentucky_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
        "start_date": date(1987, 1, 1),
        "end_date": date(1987, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumDownstreamProcessingOfFreshFeedInput"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_exports_fetcher(credentials=test_credentials):
    """Test the EIA petroleum exports fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "us_exports_of_crude_oil_thousand_barrels",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumExports"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_exports_by_destination_fetcher(credentials=test_credentials):
    """Test the EIA petroleum exports by destination fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "MCREXUS1",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumExportsByDestination"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_feedstocks_consumed_for_production_of_biofuels_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum feedstocks consumed for production of biofuels fetcher."""
    params = {
        "product": "other_animal_fats_inputs_to_biodiesel_production",
        "series": "other_waste_oil_fat_and_grease_inputs_to_biofuels_production",
        "start_date": date(2019, 1, 1),
        "end_date": date(2019, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumFeedstocksConsumedForProductionOfBiofuels"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_fob_costs_of_imported_crude_oil_by_api_gravity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum fob costs of imported crude oil by api gravity fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_gravity_20_0_percent_or_less",
        "series": "us_fob_costs_of_crude_with_api_gravity_20_0_degrees_or_less",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumFobCostsOfImportedCrudeOilByApiGravity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_fob_costs_of_imported_crude_oil_by_area_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum fob costs of imported crude oil by area fetcher."""
    params = {
        "frequency": "monthly",
        "region": "na",
        "series": "us_fob_costs_of_crude_oil",
        "start_date": date(1973, 10, 1),
        "end_date": date(1973, 10, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumFobCostsOfImportedCrudeOilByArea"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_fob_costs_of_imported_crude_oil_for_selected_crude_streams_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum fob costs of imported crude oil for selected crude streams fetcher."""
    params = {
        "frequency": "monthly",
        "product": "angolan_cabinda_crude_oil",
        "region": "ago",
        "series": "us_fob_costs_of_angolan_cabinda_crude_oil",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumFobCostsOfImportedCrudeOilForSelectedCrudeStreams"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_footage_drilled_for_crude_oil_and_natural_gas_wells_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum footage drilled for crude oil and natural gas wells fetcher."""
    params = {
        "process": "footage_drilled_for_developmental_wells",
        "product": "wells_total",
        "series": "us_footage_drilled_for_crude_oil_natural_gas_and_dry_developmental_wells_thousand_feet",
        "start_date": date(1949, 1, 1),
        "end_date": date(1949, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumFootageDrilledForCrudeOilAndNaturalGasWells"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_fuel_consumed_at_biofuels_plants_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum fuel consumed at biofuels plants fetcher."""
    params = {
        "process": "biogas_consumed_at_biofuels_plants",
        "series": "us_biogas_consumed_at_biofuels_plants",
        "start_date": date(2021, 1, 1),
        "end_date": date(2021, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumFuelConsumedAtBiofuelsPlants"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_fuel_consumed_at_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum fuel consumed at refineries fetcher."""
    params = {
        "process": "coal_consumed_at_refineries",
        "region": "us",
        "series": "us_coal_consumed_at_refineries",
        "start_date": date(1985, 1, 1),
        "end_date": date(1985, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumFuelConsumedAtRefineries"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_gasoline_prices_by_formulation_grade_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum gasoline prices by formulation grade sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "bulk_sales",
        "product": "reformulated_motor_gasoline",
        "region": "us",
        "series": "EMA_EPM0R_PBS_NUS_DPG",
        "start_date": date(1994, 1, 1),
        "end_date": date(1994, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumGasolinePricesByFormulationGradeSalesType"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_gulf_of_america_federal_offshore_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum gulf of america federal offshore production fetcher."""
    params = {
        "process": "production_from_reserves",
        "product": "crude_oil",
        "series": "gulf_of_america_federal_offshore_crude_oil_production",
        "start_date": date(1992, 1, 1),
        "end_date": date(1992, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumGulfOfAmericaFederalOffshoreProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_imports_by_area_of_entry_fetcher(credentials=test_credentials):
    """Test the EIA petroleum imports by area of entry fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "us_imports_of_crude_oil_thousand_barrels",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumImportsByAreaOfEntry"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_imports_by_processing_area_fetcher(credentials=test_credentials):
    """Test the EIA petroleum imports by processing area fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "padd_1",
        "series": "east_coast_padd_1_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumImportsByProcessingArea"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_imports_of_residual_fuel_fetcher(credentials=test_credentials):
    """Test the EIA petroleum imports of residual fuel fetcher."""
    params = {
        "frequency": "monthly",
        "product": "residual_fuel_oil",
        "region": "us",
        "series": "us_imports_of_residual_fuel_oil_thousand_barrels",
        "start_date": date(1936, 1, 1),
        "end_date": date(1936, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumImportsOfResidualFuel"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_landed_costs_of_imported_crude_by_api_gravity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum landed costs of imported crude by api gravity fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_gravity_20_0_percent_or_less",
        "series": "us_landed_costs_of_crude_with_api_gravity_20_0_degrees_or",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumLandedCostsOfImportedCrudeByApiGravity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_landed_costs_of_imported_crude_by_area_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum landed costs of imported crude by area fetcher."""
    params = {
        "frequency": "monthly",
        "region": "na",
        "series": "us_landed_costs_of_non_opec_countries_crude_oil",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumLandedCostsOfImportedCrudeByArea"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_landed_costs_of_imported_crude_for_selected_crude_streams_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum landed costs of imported crude for selected crude streams fetcher."""
    params = {
        "frequency": "monthly",
        "product": "angolan_cabinda_crude_oil",
        "region": "ago",
        "series": "us_landed_costs_of_angolan_cabinda_crude_oil",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreams"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_maximum_us_active_seismic_crew_counts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum maximum us active seismic crew counts fetcher."""
    params = {
        "process": "maximum_number_of_active_crews_engaged_in_sismic_surveying",
        "region": "us",
        "series": "us_maximum_number_of_active_crews_engaged_in_seismic",
        "start_date": date(2000, 1, 1),
        "end_date": date(2000, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumMaximumUsActiveSeismicCrewCounts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_movements_between_pad_districts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum movements between pad districts fetcher."""
    params = {
        "frequency": "monthly",
        "product": "asphalt_and_road_oil",
        "region": "padd_2",
        "series": "east_coast_padd_1_receipts_by_pipeline_tanker_barge_and_rail_from_midwest_padd_2_of_asphalt_and_road_oil_thousand_barrels",
        "start_date": date(1986, 1, 1),
        "end_date": date(1986, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumMovementsBetweenPadDistricts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_movements_by_pipeline_between_pad_districts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum movements by pipeline between pad districts fetcher."""
    params = {
        "frequency": "monthly",
        "product": "gasoline_blending_components",
        "region": "padd_2",
        "series": "east_coast_receipts_by_pipeline_from_midwest_of_gasoline",
        "start_date": date(1986, 1, 1),
        "end_date": date(1986, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumMovementsByPipelineBetweenPadDistricts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_movements_by_rail_between_pad_districts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum movements by rail between pad districts fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "padd_2",
        "series": "east_coast_receipts_by_rail_from_midwest_of_crude_oil",
        "start_date": date(2010, 1, 1),
        "end_date": date(2010, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumMovementsByRailBetweenPadDistricts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_movements_by_tanker_and_barge_between_pad_districts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum movements by tanker and barge between pad districts fetcher."""
    params = {
        "frequency": "monthly",
        "product": "asphalt_and_road_oil",
        "region": "padd_1a",
        "series": "new_england_padd_1a_receipts_by_tanker_and_barge_from_gulf_coast_padd_3_of_asphalt_and_road_oil_thousand_barrels",
        "start_date": date(1986, 1, 1),
        "end_date": date(1986, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumMovementsByTankerAndBargeBetweenPadDistricts"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_movements_of_crude_oil_and_selected_products_by_rail_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum movements of crude oil and selected products by rail fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "us_crude_oil_by_rail",
        "start_date": date(2010, 1, 1),
        "end_date": date(2010, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRail"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_natural_gas_feedstock_for_hydrogen_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum natural gas feedstock for hydrogen fetcher."""
    params = {
        "region": "us",
        "series": "us_natural_gas_used_as_feedstock_for_hydrogen_production",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNaturalGasFeedstockForHydrogen"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_natural_gas_plant_field_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum natural gas plant field production fetcher."""
    params = {
        "frequency": "monthly",
        "product": "natural_gas_plant_liquids",
        "region": "us",
        "series": "us_field_production_of_natural_gas_liquids_thousand_barrels_per_day",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNaturalGasPlantFieldProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_natural_gas_plant_stocks_fetcher(credentials=test_credentials):
    """Test the EIA petroleum natural gas plant stocks fetcher."""
    params = {
        "frequency": "monthly",
        "product": "isobutane_isobutylene",
        "region": "na",
        "series": "refining_district_indiana_illinois_kentucky_isobutane",
        "start_date": date(1993, 1, 1),
        "end_date": date(1993, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNaturalGasPlantStocks"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_net_receipts_between_pad_districts_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum net receipts between pad districts fetcher."""
    params = {
        "frequency": "monthly",
        "process": "net_receipts_by_pipeline_tanker_barge_and_rail",
        "product": "asphalt_and_road_oil",
        "region": "padd_1",
        "series": "east_coast_padd_1_net_receipts_by_pipeline_tanker_barge_and_rail_from_other_padds_of_asphalt_and_road_oil_thousand_barrels",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNetReceiptsBetweenPadDistricts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_no2_distillate_prices_by_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum no2 distillate prices by sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "residential_price_by_all_sellers",
        "product": "no_2_distillate",
        "region": "us",
        "series": "us_no_2_distillate_residential_price_by_all_sellers",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNo2DistillatePricesBySalesType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_number_and_capacity_of_petroleum_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum number and capacity of petroleum refineries fetcher."""
    params = {
        "process": "refinery_catalytic_cracking_fresh_feed_downstream_charge",
        "region": "pri",
        "series": "8_NA_8CCF_NPZ_5",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNumberAndCapacityOfPetroleumRefineries"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_nymex_futures_prices_fetcher(credentials=test_credentials):
    """Test the EIA petroleum nymex futures prices fetcher."""
    params = {
        "frequency": "weekly",
        "process": "future_contract_1",
        "product": "no_2_fuel_oil_heating_oil",
        "region": "new_york_city",
        "series": "new_york_harbor_no_2_heating_oil_future_contract_1",
        "start_date": date(1980, 1, 4),
        "end_date": date(1980, 1, 4),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumNymexFuturesPrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_oxygenate_production_fetcher(credentials=test_credentials):
    """Test the EIA petroleum oxygenate production fetcher."""
    params = {
        "frequency": "monthly",
        "process": "oxygenate_plant_production",
        "product": "fuel_ethanol",
        "region": "us",
        "series": "us_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumOxygenateProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_pad_district_exports_by_destination_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum pad district exports by destination fetcher."""
    params = {
        "frequency": "monthly",
        "product": "asphalt_and_road_oil",
        "region": "padd_1",
        "series": "MAPEXP11",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumPadDistrictExportsByDestination"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_pad_district_imports_by_country_of_origin_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum pad district imports by country of origin fetcher."""
    params = {
        "frequency": "monthly",
        "process": "imports_by_padd_of_processing",
        "product": "crude_oil",
        "region": "padd_1",
        "series": "MCRIPP11",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumPadDistrictImportsByCountryOfOrigin"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_percentages_of_total_imported_crude_oil_by_api_gravity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum percentages of total imported crude oil by api gravity fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_gravity_20_0_percent_or_less",
        "series": "us_percent_total_imported_by_api_gravity_of_crude_gravity_20_0_percent_or_less",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumPercentagesOfTotalImportedCrudeOilByApiGravity"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_prices_sales_volumes_stocks_by_state_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum prices sales volumes stocks by state fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "kerosene_type_jet_fuel",
        "region": "us",
        "series": "EMA_EPJK_PTG_NUS_DPG",
        "start_date": date(1975, 7, 1),
        "end_date": date(1975, 7, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumPricesSalesVolumesStocksByState"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_prime_supplier_sales_volumes_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum prime supplier sales volumes fetcher."""
    params = {
        "frequency": "monthly",
        "product": "total_gasoline",
        "region": "us",
        "series": "C100000001",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumPrimeSupplierSalesVolumes"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_product_supplied_fetcher(credentials=test_credentials):
    """Test the EIA petroleum product supplied fetcher."""
    params = {
        "frequency": "monthly",
        "product": "residual_fuel_oil",
        "region": "us",
        "series": "us_product_supplied_of_residual_fuel_oil_thousand_barrels",
        "start_date": date(1936, 1, 1),
        "end_date": date(1936, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumProductSupplied"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_production_capacity_of_operable_petroleum_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum production capacity of operable petroleum refineries fetcher."""
    params = {
        "process": "production_capacity_of_alkylates",
        "region": "pri",
        "series": "puerto_rico_refinery_alkylates_production_capacity_as_of",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumProductionCapacityOfOperablePetroleumRefineries"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_propane_prices_by_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum propane prices by sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "residential_price_by_all_sellers",
        "region": "us",
        "series": "us_propane_residential_price_by_all_sellers",
        "start_date": date(1993, 10, 1),
        "end_date": date(1993, 10, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumPropanePricesBySalesType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_proved_nonproducing_reserves_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum proved nonproducing reserves fetcher."""
    params = {
        "process": "associated_dissolved_reserves_in_nonproducing_reservoirs",
        "product": "natural_gas",
        "region": "na",
        "series": "gulf_of_america_federal_offshore_western_associated_dissolved_natural_gas_reserves_in_nonproducing_reservoirs_wet_bcf",
        "start_date": date(1996, 1, 1),
        "end_date": date(1996, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumProvedNonproducingReserves"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_acquisition_cost_of_crude_oil_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner acquisition cost of crude oil fetcher."""
    params = {
        "frequency": "monthly",
        "process": "imported_acquisition_cost",
        "region": "us",
        "series": "us_crude_oil_imported_acquisition_cost_by_refiners",
        "start_date": date(1974, 1, 1),
        "end_date": date(1974, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefinerAcquisitionCostOfCrudeOil"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_gasoline_prices_by_grade_and_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner gasoline prices by grade and sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "total_gasoline",
        "region": "us",
        "series": "us_total_gasoline_retail_sales_by_refiners",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefinerGasolinePricesByGradeAndSalesType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_motor_gasoline_sales_volumes_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner motor gasoline sales volumes fetcher."""
    params = {
        "frequency": "monthly",
        "process": "through_company_outlets_volume_by_refiners_and_gas_plants",
        "product": "total_gasoline",
        "region": "us",
        "series": "A103400001",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefinerMotorGasolineSalesVolumes"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_petroleum_product_prices_by_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner petroleum product prices by sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "kerosene_type_jet_fuel",
        "region": "us",
        "series": "us_kerosene_type_jet_fuel_retail_sales_by_refiners",
        "start_date": date(1975, 7, 1),
        "end_date": date(1975, 7, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefinerPetroleumProductPricesBySalesType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_residual_fuel_oil_and_no4_fuel_sales_volumes_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner residual fuel oil and no4 fuel sales volumes fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "residual_fuel_oil",
        "region": "us",
        "series": "us_residual_fuel_oil_retail_sales_by_refiners",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumes"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refiner_sales_volumes_of_other_petroleum_products_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refiner sales volumes of other petroleum products fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "no_2_distillate",
        "region": "us",
        "series": "A203600001",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumRefinerSalesVolumesOfOtherPetroleumProducts"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_blender_net_input_fetcher(credentials=test_credentials):
    """Test the EIA petroleum refinery blender net input fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "MCRRIUS2",
        "start_date": date(1961, 1, 1),
        "end_date": date(1961, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryBlenderNetInput"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_blender_net_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refinery blender net production fetcher."""
    params = {
        "frequency": "monthly",
        "product": "residual_fuel_oil",
        "region": "us",
        "series": "MRERPUS1",
        "start_date": date(1936, 1, 1),
        "end_date": date(1936, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryBlenderNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_bulk_terminal_and_natural_gas_plant_stocks_by_state_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refinery bulk terminal and natural gas plant stocks by state fetcher."""
    params = {
        "frequency": "monthly",
        "product": "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
        "region": "us",
        "series": "us_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
        "start_date": date(1993, 1, 1),
        "end_date": date(1993, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByState"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_net_input_fetcher(credentials=test_credentials):
    """Test the EIA petroleum refinery net input fetcher."""
    params = {
        "frequency": "monthly",
        "process": "refinery_receipts_of_alaskan_oil",
        "product": "crude_oil",
        "region": "na",
        "series": "MACNR2A1",
        "start_date": date(1986, 1, 1),
        "end_date": date(1986, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryNetInput"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_net_production_fetcher(credentials=test_credentials):
    """Test the EIA petroleum refinery net production fetcher."""
    params = {
        "frequency": "monthly",
        "product": "commercial_kerosene_type_jet_fuel",
        "region": "us",
        "series": "M_EPJKC_YPY_NUS_MBBL",
        "start_date": date(1993, 1, 1),
        "end_date": date(1993, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_receipts_of_crude_oil_by_method_of_transportation_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refinery receipts of crude oil by method of transportation fetcher."""
    params = {
        "process": "crude_oil_refinery_receipts_by_barge",
        "region": "us",
        "series": "us_crude_oil_refinery_receipts_by_barge",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportation"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_stocks_fetcher(credentials=test_credentials):
    """Test the EIA petroleum refinery stocks fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "padd_1",
        "series": "MCRRSP11",
        "start_date": date(1981, 1, 1),
        "end_date": date(1981, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryStocks"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_utilization_and_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum refinery utilization and capacity fetcher."""
    params = {
        "frequency": "monthly",
        "process": "refinery_net_input",
        "region": "na",
        "series": "indiana_illinois_kentucky_refinery_district_gross_inputs_to",
        "start_date": date(1985, 1, 1),
        "end_date": date(1985, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryUtilizationAndCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_refinery_yield_fetcher(credentials=test_credentials):
    """Test the EIA petroleum refinery yield fetcher."""
    params = {
        "frequency": "monthly",
        "product": "asphalt_and_road_oil",
        "region": "na",
        "series": "refining_district_indiana_illinois_kentucky_refinery_yield_of_asphalt_and_road_oil_percent",
        "start_date": date(1993, 1, 1),
        "end_date": date(1993, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumRefineryYield"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_residual_fuel_oil_prices_by_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum residual fuel oil prices by sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_all_sellers",
        "product": "residual_fuel_oil_greater_than_1_sulfur",
        "region": "us",
        "series": "us_residual_fuel_oil_sulfur_greater_than_1_retail_sales_by",
        "start_date": date(1983, 1, 1),
        "end_date": date(1983, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumResidualFuelOilPricesBySalesType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_sales_of_distillate_fuel_oil_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum sales of distillate fuel oil by end use fetcher."""
    params = {
        "process": "commercial_consumption",
        "product": "distillate_fuel_oil",
        "region": "us",
        "series": "us_total_distillate_sales_deliveries_to_commercial_consumers",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumSalesOfDistillateFuelOilByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_sales_of_kerosene_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum sales of kerosene by end use fetcher."""
    params = {
        "process": "commercial_consumption",
        "region": "us",
        "series": "us_kerosene_sales_deliveries_to_commercial_consumers",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumSalesOfKeroseneByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_sales_of_residual_fuel_oil_by_end_use_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum sales of residual fuel oil by end use fetcher."""
    params = {
        "process": "commercial_consumption",
        "region": "us",
        "series": "us_residual_fuel_oil_sales_deliveries_to_commercial",
        "start_date": date(1984, 1, 1),
        "end_date": date(1984, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumSalesOfResidualFuelOilByEndUse"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_shell_storage_capacity_at_operable_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum shell storage capacity at operable refineries fetcher."""
    params = {
        "process": "shell_storage_capacity_at_refineries",
        "region": "us",
        "series": "us_refinery_shell_storage_capacity_as_of_january_1",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumShellStorageCapacityAtOperableRefineries"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_spot_prices_fetcher(credentials=test_credentials):
    """Test the EIA petroleum spot prices fetcher."""
    params = {
        "frequency": "weekly",
        "product": "wti_crude_oil",
        "region": "na",
        "series": "cushing_ok_wti_spot_price_fob",
        "start_date": date(1986, 1, 3),
        "end_date": date(1986, 1, 3),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumSpotPrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_stocks_by_type_fetcher(credentials=test_credentials):
    """Test the EIA petroleum stocks by type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "ending_stocks",
        "product": "crude_oil",
        "region": "us",
        "series": "MCRSTUS1",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumStocksByType"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_stocks_of_selected_products_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum stocks of selected products fetcher."""
    params = {
        "frequency": "monthly",
        "product": "residual_fuel_oil",
        "region": "us",
        "series": "us_ending_stocks_of_residual_fuel_oil",
        "start_date": date(1936, 1, 1),
        "end_date": date(1936, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumStocksOfSelectedProducts"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_supply_and_disposition_fetcher(credentials=test_credentials):
    """Test the EIA petroleum supply and disposition fetcher."""
    params = {
        "frequency": "monthly",
        "process": "ending_stocks",
        "product": "crude_oil",
        "region": "us",
        "series": "MCRSTUS1",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumSupplyAndDisposition"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_biodiesel_production_capacity_sales_and_stocks_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum us biodiesel production capacity sales and stocks fetcher."""
    params = {
        "frequency": "monthly",
        "process": "ending_stocks",
        "region": "us",
        "series": "us_ending_stocks_of_b100",
        "start_date": date(2009, 1, 1),
        "end_date": date(2009, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumUsBiodieselProductionCapacitySalesAndStocks"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_crude_oil_supply_disposition_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum us crude oil supply disposition fetcher."""
    params = {
        "frequency": "monthly",
        "process": "ending_stocks",
        "region": "us",
        "series": "us_ending_stocks_of_crude_oil",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumUsCrudeOilSupplyDisposition"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_imports_by_country_of_origin_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum us imports by country of origin fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "MCRIMUS1",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumUsImportsByCountryOfOrigin"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_net_imports_by_country_fetcher(credentials=test_credentials):
    """Test the EIA petroleum us net imports by country fetcher."""
    params = {
        "frequency": "monthly",
        "product": "crude_oil",
        "region": "us",
        "series": "MCRNTUS2",
        "start_date": date(1920, 1, 1),
        "end_date": date(1920, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumUsNetImportsByCountry"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_refiner_gasoline_prices_by_formulation_grade_sales_type_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum us refiner gasoline prices by formulation grade sales type fetcher."""
    params = {
        "frequency": "monthly",
        "process": "retail_sales_by_refiners_and_gas_plants",
        "product": "reformulated_motor_gasoline",
        "series": "us_reformulated_gasoline_retail_sales_by_refiners",
        "start_date": date(1994, 1, 1),
        "end_date": date(1994, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesType"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_us_weekly_product_supplied_fetcher(credentials=test_credentials):
    """Test the EIA petroleum us weekly product supplied fetcher."""
    params = {
        "frequency": "weekly",
        "product": "total_petroleum_products",
        "series": "us_product_supplied_of_petroleum_products",
        "start_date": date(1990, 11, 9),
        "end_date": date(1990, 11, 9),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumUsWeeklyProductSupplied"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_blender_net_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly blender net production fetcher."""
    params = {
        "frequency": "weekly",
        "product": "distillate_fuel_oil_greater_than_500_ppm_sulfur",
        "region": "us",
        "series": "us_blender_net_production_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels_per_day",
        "start_date": date(2010, 6, 4),
        "end_date": date(2010, 6, 4),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyBlenderNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_crude_imports_by_top10_origins_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly crude imports by top10 origins fetcher."""
    params = {
        "frequency": "weekly",
        "region": "dza",
        "series": "us_imports_from_algeria_of_crude_oil",
        "start_date": date(2010, 6, 4),
        "end_date": date(2010, 6, 4),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyCrudeImportsByTop10Origins"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_ethanol_plant_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly ethanol plant production fetcher."""
    params = {
        "frequency": "weekly",
        "region": "us",
        "series": "us_oxygenate_plant_production_of_fuel_ethanol",
        "start_date": date(2010, 6, 4),
        "end_date": date(2010, 6, 4),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyEthanolPlantProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_heating_oil_and_propane_prices_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly heating oil and propane prices fetcher."""
    params = {
        "frequency": "weekly",
        "process": "price_delivered_to_residential_consumers",
        "product": "no_2_fuel_oil_heating_oil",
        "region": "us",
        "series": "us_weekly_no_2_heating_oil_residential_price",
        "start_date": date(1990, 10, 1),
        "end_date": date(1990, 10, 1),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyHeatingOilAndPropanePrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_imports_exports_fetcher(credentials=test_credentials):
    """Test the EIA petroleum weekly imports exports fetcher."""
    params = {
        "frequency": "weekly",
        "process": "imports",
        "product": "distillate_fuel_oil",
        "region": "us",
        "series": "us_imports_of_distillate_fuel_oil",
        "start_date": date(1982, 8, 20),
        "end_date": date(1982, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyImportsExports"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_inputs_utilization_fetcher(credentials=test_credentials):
    """Test the EIA petroleum weekly inputs utilization fetcher."""
    params = {
        "frequency": "weekly",
        "process": "refinery_net_input",
        "product": "crude_oil",
        "region": "us",
        "series": "us_refiner_net_input_of_crude_oil",
        "start_date": date(1982, 8, 20),
        "end_date": date(1982, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyInputsUtilization"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_refiner_blender_net_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly refiner blender net production fetcher."""
    params = {
        "frequency": "weekly",
        "process": "refinery_and_blender_net_production",
        "product": "distillate_fuel_oil",
        "region": "us",
        "series": "us_refiner_and_blender_net_production_of_distillate_fuel_oil",
        "start_date": date(1982, 8, 20),
        "end_date": date(1982, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyRefinerBlenderNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_refiner_net_production_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly refiner net production fetcher."""
    params = {
        "frequency": "weekly",
        "product": "distillate_fuel_oil_greater_than_500_ppm_sulfur",
        "region": "us",
        "series": "us_refiner_net_production_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels_per_day",
        "start_date": date(2010, 6, 4),
        "end_date": date(2010, 6, 4),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyRefinerNetProduction"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_retail_gasoline_and_diesel_prices_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum weekly retail gasoline and diesel prices fetcher."""
    params = {
        "frequency": "weekly",
        "product": "conventional_regular_gasoline",
        "region": "us",
        "series": "us_regular_conventional_retail_gasoline_prices",
        "start_date": date(1990, 8, 20),
        "end_date": date(1990, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyRetailGasolineAndDieselPrices"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_stocks_fetcher(credentials=test_credentials):
    """Test the EIA petroleum weekly stocks fetcher."""
    params = {
        "process": "ending_stocks",
        "product": "crude_oil",
        "region": "us",
        "series": "us_ending_stocks_of_crude_oil",
        "start_date": date(1982, 8, 20),
        "end_date": date(1982, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklyStocks"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_weekly_supply_estimates_fetcher(credentials=test_credentials):
    """Test the EIA petroleum weekly supply estimates fetcher."""
    params = {
        "frequency": "weekly",
        "process": "refinery_net_input",
        "product": "crude_oil",
        "region": "us",
        "series": "us_refiner_net_input_of_crude_oil",
        "start_date": date(1982, 8, 20),
        "end_date": date(1982, 8, 20),
    }

    fetcher = DATASET_FETCHERS["EiaPetroleumWeeklySupplyEstimates"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_petroleum_working_storage_capacity_at_operable_refineries_fetcher(
    credentials=test_credentials,
):
    """Test the EIA petroleum working storage capacity at operable refineries fetcher."""
    params = {
        "process": "working_storage_capacity",
        "region": "us",
        "series": "us_refinery_working_storage_capacity_as_of_january_1",
        "start_date": date(1982, 1, 1),
        "end_date": date(1982, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaPetroleumWorkingStorageCapacityAtOperableRefineries"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_seds_fetcher(credentials=test_credentials):
    """Test the EIA seds fetcher."""
    params = {
        "series": "aviation_gasoline_blending_components_consumed_by_the",
        "state": "alaska",
        "start_date": date(1960, 1, 1),
        "end_date": date(1960, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaSeds"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_advanced_metering_infrastructure_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles advanced metering infrastructure fetcher."""
    params = {
        "sector": "commercial",
        "state": "alaska",
        "technology": "advanced_metering_infrastructure",
        "start_date": date(2013, 1, 1),
        "end_date": date(2013, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaStateElectricityProfilesAdvancedMeteringInfrastructure"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_costs_and_savings_from_energy_efficiency_programs_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles costs and savings from energy efficiency programs fetcher."""
    params = {
        "sector": "commercial",
        "state": "alaska",
        "start_date": date(2013, 1, 1),
        "end_date": date(2013, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyPrograms"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_electricity_net_metering_customers_and_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles electricity net metering customers and capacity fetcher."""
    params = {
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacity"
    ]()
    with pytest.raises(EmptyDataError):
        fetcher.test(params, credentials)


@pytest.mark.record_http
def test_eia_state_electricity_profiles_emissions_by_state_by_fuel_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles emissions by state by fuel fetcher."""
    params = {
        "fuel": "total",
        "state": "alaska",
        "start_date": date(1990, 1, 1),
        "end_date": date(1990, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaStateElectricityProfilesEmissionsByStateByFuel"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_generating_capacity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles generating capacity fetcher."""
    params = {
        "energy_source": "all",
        "producer_type": "electric_utilities",
        "state": "alaska",
        "start_date": date(1990, 1, 1),
        "end_date": date(1990, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaStateElectricityProfilesGeneratingCapacity"]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_state_rankings_for_key_statistics_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles state rankings for key statistics fetcher."""
    params = {
        "state": "alaska",
        "start_date": date(2008, 1, 1),
        "end_date": date(2008, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaStateElectricityProfilesStateRankingsForKeyStatistics"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_state_electricity_profiles_supply_and_disposition_of_electricity_fetcher(
    credentials=test_credentials,
):
    """Test the EIA state electricity profiles supply and disposition of electricity fetcher."""
    params = {
        "state": "alaska",
        "start_date": date(1990, 1, 1),
        "end_date": date(1990, 1, 1),
    }

    fetcher = DATASET_FETCHERS[
        "EiaStateElectricityProfilesSupplyAndDispositionOfElectricity"
    ]()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_eia_total_energy_fetcher(credentials=test_credentials):
    """Test the EIA total energy fetcher."""
    params = {
        "frequency": "monthly",
        "msn": "asphalt_and_road_oil_consumed_by_the_industrial_sector_in_trillion_btu",
        "start_date": date(1973, 1, 1),
        "end_date": date(1973, 1, 1),
    }

    fetcher = DATASET_FETCHERS["EiaTotalEnergy"]()
    result = fetcher.test(params, credentials)
    assert result is None
