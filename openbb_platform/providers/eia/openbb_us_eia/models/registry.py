"""Registry of EIA dataset fetchers."""

from openbb_us_eia.models.aeo import EiaAeoFetcher
from openbb_us_eia.models.coal.aggregate_production import (
    EiaCoalAggregateProductionFetcher,
)
from openbb_us_eia.models.coal.by_mine_by_plant import EiaCoalByMineByPlantFetcher
from openbb_us_eia.models.coal.consumption_and_quality import (
    EiaCoalConsumptionAndQualityFetcher,
)
from openbb_us_eia.models.coal.exports_imports_quantity_price import (
    EiaCoalExportsImportsQuantityPriceFetcher,
)
from openbb_us_eia.models.coal.market_sales_price import EiaCoalMarketSalesPriceFetcher
from openbb_us_eia.models.coal.mine_aggregates import EiaCoalMineAggregatesFetcher
from openbb_us_eia.models.coal.mine_production import EiaCoalMineProductionFetcher
from openbb_us_eia.models.coal.mine_state_aggregates import (
    EiaCoalMineStateAggregatesFetcher,
)
from openbb_us_eia.models.coal.plant_aggregates import EiaCoalPlantAggregatesFetcher
from openbb_us_eia.models.coal.plant_state_aggregates import (
    EiaCoalPlantStateAggregatesFetcher,
)
from openbb_us_eia.models.coal.price_by_rank import EiaCoalPriceByRankFetcher
from openbb_us_eia.models.coal.receipts import EiaCoalReceiptsFetcher
from openbb_us_eia.models.coal.reserves_capacity import EiaCoalReservesCapacityFetcher
from openbb_us_eia.models.crude_oil_imports import EiaCrudeOilImportsFetcher
from openbb_us_eia.models.densified_biomass.capacity_by_region import (
    EiaDensifiedBiomassCapacityByRegionFetcher,
)
from openbb_us_eia.models.densified_biomass.characteristics_by_region import (
    EiaDensifiedBiomassCharacteristicsByRegionFetcher,
)
from openbb_us_eia.models.densified_biomass.export_sales_and_price import (
    EiaDensifiedBiomassExportSalesAndPriceFetcher,
)
from openbb_us_eia.models.densified_biomass.feedstocks_and_costs import (
    EiaDensifiedBiomassFeedstocksAndCostsFetcher,
)
from openbb_us_eia.models.densified_biomass.inventories_by_region import (
    EiaDensifiedBiomassInventoriesByRegionFetcher,
)
from openbb_us_eia.models.densified_biomass.production_by_region import (
    EiaDensifiedBiomassProductionByRegionFetcher,
)
from openbb_us_eia.models.densified_biomass.sales_and_price_by_region import (
    EiaDensifiedBiomassSalesAndPriceByRegionFetcher,
)
from openbb_us_eia.models.densified_biomass.wood_pellet_plant_capacity import (
    EiaDensifiedBiomassWoodPelletPlantCapacityFetcher,
)
from openbb_us_eia.models.electricity.electric_power_operations import (
    EiaElectricityElectricPowerOperationsFetcher,
)
from openbb_us_eia.models.electricity.electric_power_operations_for_individual_power_plants import (
    EiaElectricityElectricPowerOperationsForIndividualPowerPlantsFetcher,
)
from openbb_us_eia.models.electricity.electricity_sales_to_ultimate_customers import (
    EiaElectricityElectricitySalesToUltimateCustomersFetcher,
)
from openbb_us_eia.models.electricity.inventory_of_operable_generators import (
    EiaElectricityInventoryOfOperableGeneratorsFetcher,
)
from openbb_us_eia.models.electricity_grid.demand import EiaElectricityGridDemandFetcher
from openbb_us_eia.models.electricity_grid.demand_by_subregion import (
    EiaElectricityGridDemandBySubregionFetcher,
)
from openbb_us_eia.models.electricity_grid.generation_by_fuel import (
    EiaElectricityGridGenerationByFuelFetcher,
)
from openbb_us_eia.models.electricity_grid.interchange import (
    EiaElectricityGridInterchangeFetcher,
)
from openbb_us_eia.models.ieo import EiaIeoFetcher
from openbb_us_eia.models.international import EiaInternationalFetcher
from openbb_us_eia.models.natural_gas.associated_dissolved_proved_reserves import (
    EiaNaturalGasAssociatedDissolvedProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.average_depth_of_crude_oil_and_natural_gas_wells import (
    EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsFetcher,
)
from openbb_us_eia.models.natural_gas.coalbed_methane import (
    EiaNaturalGasCoalbedMethaneFetcher,
)
from openbb_us_eia.models.natural_gas.coalbed_methane_production import (
    EiaNaturalGasCoalbedMethaneProductionFetcher,
)
from openbb_us_eia.models.natural_gas.costs_of_crude_oil_and_natural_gas_wells_drilled import (
    EiaNaturalGasCostsOfCrudeOilAndNaturalGasWellsDrilledFetcher,
)
from openbb_us_eia.models.natural_gas.crude_oil_and_natural_gas_drilling_activity import (
    EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityFetcher,
)
from openbb_us_eia.models.natural_gas.crude_oil_and_natural_gas_exploratory_and_development_wells import (
    EiaNaturalGasCrudeOilAndNaturalGasExploratoryAndDevelopmentWellsFetcher,
)
from openbb_us_eia.models.natural_gas.crude_oil_plus_lease_condensate import (
    EiaNaturalGasCrudeOilPlusLeaseCondensateFetcher,
)
from openbb_us_eia.models.natural_gas.dry_natural_gas_proved_reserves import (
    EiaNaturalGasDryNaturalGasProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.federal_offshore_gulf_of_america_proved_reserves import (
    EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.footage_drilled_for_crude_oil_and_natural_gas_wells import (
    EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsFetcher,
)
from openbb_us_eia.models.natural_gas.gulf_of_america_federal_offshore_production import (
    EiaNaturalGasGulfOfAmericaFederalOffshoreProductionFetcher,
)
from openbb_us_eia.models.natural_gas.heat_content_of_natural_gas_consumed import (
    EiaNaturalGasHeatContentOfNaturalGasConsumedFetcher,
)
from openbb_us_eia.models.natural_gas.international_interstate_movements_of_natural_gas_by_state import (
    EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateFetcher,
)
from openbb_us_eia.models.natural_gas.lease_condensate import (
    EiaNaturalGasLeaseCondensateFetcher,
)
from openbb_us_eia.models.natural_gas.lease_condensate_production import (
    EiaNaturalGasLeaseCondensateProductionFetcher,
)
from openbb_us_eia.models.natural_gas.lng_storage_additions_and_withdrawals import (
    EiaNaturalGasLngStorageAdditionsAndWithdrawalsFetcher,
)
from openbb_us_eia.models.natural_gas.maximum_us_active_seismic_crew_counts import (
    EiaNaturalGasMaximumUsActiveSeismicCrewCountsFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_annual_supply_disposition_by_state import (
    EiaNaturalGasNaturalGasAnnualSupplyDispositionByStateFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_consumption_by_end_use import (
    EiaNaturalGasNaturalGasConsumptionByEndUseFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_delivered_for_the_account_of_others import (
    EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_gross_withdrawals_and_production import (
    EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_liquids_proved_reserves import (
    EiaNaturalGasNaturalGasLiquidsProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_plant_liquids_production import (
    EiaNaturalGasNaturalGasPlantLiquidsProductionFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_plant_processing import (
    EiaNaturalGasNaturalGasPlantProcessingFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_prices import (
    EiaNaturalGasNaturalGasPricesFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_proved_reserves_wet_after_lease_separation import (
    EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_reserves_summary_as_of_dec_31 import (
    EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Fetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_spot_and_futures_prices import (
    EiaNaturalGasNaturalGasSpotAndFuturesPricesFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_summary import (
    EiaNaturalGasNaturalGasSummaryFetcher,
)
from openbb_us_eia.models.natural_gas.natural_gas_wellhead_value_and_marketed_production import (
    EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionFetcher,
)
from openbb_us_eia.models.natural_gas.nonassociated_proved_reserves import (
    EiaNaturalGasNonassociatedProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.number_of_gas_producing_oil_wells import (
    EiaNaturalGasNumberOfGasProducingOilWellsFetcher,
)
from openbb_us_eia.models.natural_gas.number_of_natural_gas_consumers import (
    EiaNaturalGasNumberOfNaturalGasConsumersFetcher,
)
from openbb_us_eia.models.natural_gas.number_of_producing_gas_wells import (
    EiaNaturalGasNumberOfProducingGasWellsFetcher,
)
from openbb_us_eia.models.natural_gas.offshore_gross_withdrawals_of_natural_gas import (
    EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasFetcher,
)
from openbb_us_eia.models.natural_gas.plant_liquids_in_proved_reserves import (
    EiaNaturalGasPlantLiquidsInProvedReservesFetcher,
)
from openbb_us_eia.models.natural_gas.proved_nonproducing_reserves import (
    EiaNaturalGasProvedNonproducingReservesFetcher,
)
from openbb_us_eia.models.natural_gas.residential_and_commercial_prices_selected_states import (
    EiaNaturalGasResidentialAndCommercialPricesSelectedStatesFetcher,
)
from openbb_us_eia.models.natural_gas.shale_gas import EiaNaturalGasShaleGasFetcher
from openbb_us_eia.models.natural_gas.shale_gas_production import (
    EiaNaturalGasShaleGasProductionFetcher,
)
from openbb_us_eia.models.natural_gas.share_of_total_us_natural_gas_delivered_to_consumers import (
    EiaNaturalGasShareOfTotalUsNaturalGasDeliveredToConsumersFetcher,
)
from openbb_us_eia.models.natural_gas.supplemental_gas_supplies import (
    EiaNaturalGasSupplementalGasSuppliesFetcher,
)
from openbb_us_eia.models.natural_gas.underground_natural_gas_storage_by_all_operators import (
    EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsFetcher,
)
from openbb_us_eia.models.natural_gas.underground_natural_gas_storage_capacity import (
    EiaNaturalGasUndergroundNaturalGasStorageCapacityFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_exports_and_re_exports_by_country import (
    EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_exports_and_re_exports_by_point_of_exit import (
    EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_imports_by_country import (
    EiaNaturalGasUsNaturalGasImportsByCountryFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_imports_by_point_of_entry import (
    EiaNaturalGasUsNaturalGasImportsByPointOfEntryFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_imports_exports_by_state import (
    EiaNaturalGasUsNaturalGasImportsExportsByStateFetcher,
)
from openbb_us_eia.models.natural_gas.us_natural_gas_monthly_supply_and_disposition_balance import (
    EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceFetcher,
)
from openbb_us_eia.models.natural_gas.us_underground_natural_gas_storage_by_storage_type import (
    EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeFetcher,
)
from openbb_us_eia.models.natural_gas.weekly_working_gas_in_underground_storage import (
    EiaNaturalGasWeeklyWorkingGasInUndergroundStorageFetcher,
)
from openbb_us_eia.models.nuclear_outages.facility_level_nuclear_outages import (
    EiaNuclearOutagesFacilityLevelNuclearOutagesFetcher,
)
from openbb_us_eia.models.nuclear_outages.generator_level_nuclear_outages import (
    EiaNuclearOutagesGeneratorLevelNuclearOutagesFetcher,
)
from openbb_us_eia.models.nuclear_outages.us_nuclear_outages import (
    EiaNuclearOutagesUsNuclearOutagesFetcher,
)
from openbb_us_eia.models.petroleum.adjusted_distillate_fuel_oil_and_kerosene_sales_by_end_use import (
    EiaPetroleumAdjustedDistillateFuelOilAndKeroseneSalesByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.adjusted_sales_of_distillate_fuel_oil_by_end_use import (
    EiaPetroleumAdjustedSalesOfDistillateFuelOilByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.adjusted_sales_of_kerosene_by_end_use import (
    EiaPetroleumAdjustedSalesOfKeroseneByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.adjusted_sales_of_residual_fuel_oil_by_end_use import (
    EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.average_depth_of_crude_oil_and_natural_gas_wells import (
    EiaPetroleumAverageDepthOfCrudeOilAndNaturalGasWellsFetcher,
)
from openbb_us_eia.models.petroleum.biofuels_operable_production_capacity import (
    EiaPetroleumBiofuelsOperableProductionCapacityFetcher,
)
from openbb_us_eia.models.petroleum.blender_net_input import (
    EiaPetroleumBlenderNetInputFetcher,
)
from openbb_us_eia.models.petroleum.blender_net_production import (
    EiaPetroleumBlenderNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.costs_of_crude_oil_and_natural_gas_wells_drilled import (
    EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledFetcher,
)
from openbb_us_eia.models.petroleum.crude_first_purchase_prices_selected_streams import (
    EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_and_lease_condensate_production_by_api_gravity import (
    EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_and_natural_gas_drilling_activity import (
    EiaPetroleumCrudeOilAndNaturalGasDrillingActivityFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_and_natural_gas_exploratory_and_development_wells import (
    EiaPetroleumCrudeOilAndNaturalGasExploratoryAndDevelopmentWellsFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_input_qualities import (
    EiaPetroleumCrudeOilInputQualitiesFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_production import (
    EiaPetroleumCrudeOilProductionFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_proved_reserves_reserves_changes_and_production import (
    EiaPetroleumCrudeOilProvedReservesReservesChangesAndProductionFetcher,
)
from openbb_us_eia.models.petroleum.crude_oil_stocks_at_tank_farms_pipelines import (
    EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesFetcher,
)
from openbb_us_eia.models.petroleum.crude_plus_lease_condensate_proved_reserves import (
    EiaPetroleumCrudePlusLeaseCondensateProvedReservesFetcher,
)
from openbb_us_eia.models.petroleum.distillate_fuel_oil_and_kerosene_sales_by_end_use import (
    EiaPetroleumDistillateFuelOilAndKeroseneSalesByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.domestic_crude_oil_first_purchase_prices_by_api_gravity import (
    EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityFetcher,
)
from openbb_us_eia.models.petroleum.domestic_crude_oil_first_purchase_prices_by_area import (
    EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaFetcher,
)
from openbb_us_eia.models.petroleum.downstream_charge_capacity_of_operable_petroleum_refineries import (
    EiaPetroleumDownstreamChargeCapacityOfOperablePetroleumRefineriesFetcher,
)
from openbb_us_eia.models.petroleum.downstream_processing_of_fresh_feed_input import (
    EiaPetroleumDownstreamProcessingOfFreshFeedInputFetcher,
)
from openbb_us_eia.models.petroleum.exports import EiaPetroleumExportsFetcher
from openbb_us_eia.models.petroleum.exports_by_destination import (
    EiaPetroleumExportsByDestinationFetcher,
)
from openbb_us_eia.models.petroleum.feedstocks_consumed_for_production_of_biofuels import (
    EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsFetcher,
)
from openbb_us_eia.models.petroleum.fob_costs_of_imported_crude_oil_by_api_gravity import (
    EiaPetroleumFobCostsOfImportedCrudeOilByApiGravityFetcher,
)
from openbb_us_eia.models.petroleum.fob_costs_of_imported_crude_oil_by_area import (
    EiaPetroleumFobCostsOfImportedCrudeOilByAreaFetcher,
)
from openbb_us_eia.models.petroleum.fob_costs_of_imported_crude_oil_for_selected_crude_streams import (
    EiaPetroleumFobCostsOfImportedCrudeOilForSelectedCrudeStreamsFetcher,
)
from openbb_us_eia.models.petroleum.footage_drilled_for_crude_oil_and_natural_gas_wells import (
    EiaPetroleumFootageDrilledForCrudeOilAndNaturalGasWellsFetcher,
)
from openbb_us_eia.models.petroleum.fuel_consumed_at_biofuels_plants import (
    EiaPetroleumFuelConsumedAtBiofuelsPlantsFetcher,
)
from openbb_us_eia.models.petroleum.fuel_consumed_at_refineries import (
    EiaPetroleumFuelConsumedAtRefineriesFetcher,
)
from openbb_us_eia.models.petroleum.gasoline_prices_by_formulation_grade_sales_type import (
    EiaPetroleumGasolinePricesByFormulationGradeSalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.gulf_of_america_federal_offshore_production import (
    EiaPetroleumGulfOfAmericaFederalOffshoreProductionFetcher,
)
from openbb_us_eia.models.petroleum.imports_by_area_of_entry import (
    EiaPetroleumImportsByAreaOfEntryFetcher,
)
from openbb_us_eia.models.petroleum.imports_by_processing_area import (
    EiaPetroleumImportsByProcessingAreaFetcher,
)
from openbb_us_eia.models.petroleum.imports_of_residual_fuel import (
    EiaPetroleumImportsOfResidualFuelFetcher,
)
from openbb_us_eia.models.petroleum.landed_costs_of_imported_crude_by_api_gravity import (
    EiaPetroleumLandedCostsOfImportedCrudeByApiGravityFetcher,
)
from openbb_us_eia.models.petroleum.landed_costs_of_imported_crude_by_area import (
    EiaPetroleumLandedCostsOfImportedCrudeByAreaFetcher,
)
from openbb_us_eia.models.petroleum.landed_costs_of_imported_crude_for_selected_crude_streams import (
    EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsFetcher,
)
from openbb_us_eia.models.petroleum.maximum_us_active_seismic_crew_counts import (
    EiaPetroleumMaximumUsActiveSeismicCrewCountsFetcher,
)
from openbb_us_eia.models.petroleum.movements_between_pad_districts import (
    EiaPetroleumMovementsBetweenPadDistrictsFetcher,
)
from openbb_us_eia.models.petroleum.movements_by_pipeline_between_pad_districts import (
    EiaPetroleumMovementsByPipelineBetweenPadDistrictsFetcher,
)
from openbb_us_eia.models.petroleum.movements_by_rail_between_pad_districts import (
    EiaPetroleumMovementsByRailBetweenPadDistrictsFetcher,
)
from openbb_us_eia.models.petroleum.movements_by_tanker_and_barge_between_pad_districts import (
    EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsFetcher,
)
from openbb_us_eia.models.petroleum.movements_of_crude_oil_and_selected_products_by_rail import (
    EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailFetcher,
)
from openbb_us_eia.models.petroleum.natural_gas_feedstock_for_hydrogen import (
    EiaPetroleumNaturalGasFeedstockForHydrogenFetcher,
)
from openbb_us_eia.models.petroleum.natural_gas_plant_field_production import (
    EiaPetroleumNaturalGasPlantFieldProductionFetcher,
)
from openbb_us_eia.models.petroleum.natural_gas_plant_stocks import (
    EiaPetroleumNaturalGasPlantStocksFetcher,
)
from openbb_us_eia.models.petroleum.net_receipts_between_pad_districts import (
    EiaPetroleumNetReceiptsBetweenPadDistrictsFetcher,
)
from openbb_us_eia.models.petroleum.no2_distillate_prices_by_sales_type import (
    EiaPetroleumNo2DistillatePricesBySalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.number_and_capacity_of_petroleum_refineries import (
    EiaPetroleumNumberAndCapacityOfPetroleumRefineriesFetcher,
)
from openbb_us_eia.models.petroleum.nymex_futures_prices import (
    EiaPetroleumNymexFuturesPricesFetcher,
)
from openbb_us_eia.models.petroleum.oxygenate_production import (
    EiaPetroleumOxygenateProductionFetcher,
)
from openbb_us_eia.models.petroleum.pad_district_exports_by_destination import (
    EiaPetroleumPadDistrictExportsByDestinationFetcher,
)
from openbb_us_eia.models.petroleum.pad_district_imports_by_country_of_origin import (
    EiaPetroleumPadDistrictImportsByCountryOfOriginFetcher,
)
from openbb_us_eia.models.petroleum.percentages_of_total_imported_crude_oil_by_api_gravity import (
    EiaPetroleumPercentagesOfTotalImportedCrudeOilByApiGravityFetcher,
)
from openbb_us_eia.models.petroleum.prices_sales_volumes_stocks_by_state import (
    EiaPetroleumPricesSalesVolumesStocksByStateFetcher,
)
from openbb_us_eia.models.petroleum.prime_supplier_sales_volumes import (
    EiaPetroleumPrimeSupplierSalesVolumesFetcher,
)
from openbb_us_eia.models.petroleum.product_supplied import (
    EiaPetroleumProductSuppliedFetcher,
)
from openbb_us_eia.models.petroleum.production_capacity_of_operable_petroleum_refineries import (
    EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesFetcher,
)
from openbb_us_eia.models.petroleum.propane_prices_by_sales_type import (
    EiaPetroleumPropanePricesBySalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.proved_nonproducing_reserves import (
    EiaPetroleumProvedNonproducingReservesFetcher,
)
from openbb_us_eia.models.petroleum.refiner_acquisition_cost_of_crude_oil import (
    EiaPetroleumRefinerAcquisitionCostOfCrudeOilFetcher,
)
from openbb_us_eia.models.petroleum.refiner_gasoline_prices_by_grade_and_sales_type import (
    EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.refiner_motor_gasoline_sales_volumes import (
    EiaPetroleumRefinerMotorGasolineSalesVolumesFetcher,
)
from openbb_us_eia.models.petroleum.refiner_petroleum_product_prices_by_sales_type import (
    EiaPetroleumRefinerPetroleumProductPricesBySalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.refiner_residual_fuel_oil_and_no4_fuel_sales_volumes import (
    EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesFetcher,
)
from openbb_us_eia.models.petroleum.refiner_sales_volumes_of_other_petroleum_products import (
    EiaPetroleumRefinerSalesVolumesOfOtherPetroleumProductsFetcher,
)
from openbb_us_eia.models.petroleum.refinery_blender_net_input import (
    EiaPetroleumRefineryBlenderNetInputFetcher,
)
from openbb_us_eia.models.petroleum.refinery_blender_net_production import (
    EiaPetroleumRefineryBlenderNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.refinery_bulk_terminal_and_natural_gas_plant_stocks_by_state import (
    EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateFetcher,
)
from openbb_us_eia.models.petroleum.refinery_net_input import (
    EiaPetroleumRefineryNetInputFetcher,
)
from openbb_us_eia.models.petroleum.refinery_net_production import (
    EiaPetroleumRefineryNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.refinery_receipts_of_crude_oil_by_method_of_transportation import (
    EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationFetcher,
)
from openbb_us_eia.models.petroleum.refinery_stocks import (
    EiaPetroleumRefineryStocksFetcher,
)
from openbb_us_eia.models.petroleum.refinery_utilization_and_capacity import (
    EiaPetroleumRefineryUtilizationAndCapacityFetcher,
)
from openbb_us_eia.models.petroleum.refinery_yield import (
    EiaPetroleumRefineryYieldFetcher,
)
from openbb_us_eia.models.petroleum.residual_fuel_oil_prices_by_sales_type import (
    EiaPetroleumResidualFuelOilPricesBySalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.sales_of_distillate_fuel_oil_by_end_use import (
    EiaPetroleumSalesOfDistillateFuelOilByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.sales_of_kerosene_by_end_use import (
    EiaPetroleumSalesOfKeroseneByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.sales_of_residual_fuel_oil_by_end_use import (
    EiaPetroleumSalesOfResidualFuelOilByEndUseFetcher,
)
from openbb_us_eia.models.petroleum.shell_storage_capacity_at_operable_refineries import (
    EiaPetroleumShellStorageCapacityAtOperableRefineriesFetcher,
)
from openbb_us_eia.models.petroleum.spot_prices import EiaPetroleumSpotPricesFetcher
from openbb_us_eia.models.petroleum.stocks_by_type import (
    EiaPetroleumStocksByTypeFetcher,
)
from openbb_us_eia.models.petroleum.stocks_of_selected_products import (
    EiaPetroleumStocksOfSelectedProductsFetcher,
)
from openbb_us_eia.models.petroleum.supply_and_disposition import (
    EiaPetroleumSupplyAndDispositionFetcher,
)
from openbb_us_eia.models.petroleum.us_biodiesel_production_capacity_sales_and_stocks import (
    EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksFetcher,
)
from openbb_us_eia.models.petroleum.us_crude_oil_supply_disposition import (
    EiaPetroleumUsCrudeOilSupplyDispositionFetcher,
)
from openbb_us_eia.models.petroleum.us_imports_by_country_of_origin import (
    EiaPetroleumUsImportsByCountryOfOriginFetcher,
)
from openbb_us_eia.models.petroleum.us_net_imports_by_country import (
    EiaPetroleumUsNetImportsByCountryFetcher,
)
from openbb_us_eia.models.petroleum.us_refiner_gasoline_prices_by_formulation_grade_sales_type import (
    EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeFetcher,
)
from openbb_us_eia.models.petroleum.us_weekly_product_supplied import (
    EiaPetroleumUsWeeklyProductSuppliedFetcher,
)
from openbb_us_eia.models.petroleum.weekly_blender_net_production import (
    EiaPetroleumWeeklyBlenderNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.weekly_crude_imports_by_top_10_origins import (
    EiaPetroleumWeeklyCrudeImportsByTop10OriginsFetcher,
)
from openbb_us_eia.models.petroleum.weekly_ethanol_plant_production import (
    EiaPetroleumWeeklyEthanolPlantProductionFetcher,
)
from openbb_us_eia.models.petroleum.weekly_heating_oil_and_propane_prices import (
    EiaPetroleumWeeklyHeatingOilAndPropanePricesFetcher,
)
from openbb_us_eia.models.petroleum.weekly_imports_exports import (
    EiaPetroleumWeeklyImportsExportsFetcher,
)
from openbb_us_eia.models.petroleum.weekly_inputs_utilization import (
    EiaPetroleumWeeklyInputsUtilizationFetcher,
)
from openbb_us_eia.models.petroleum.weekly_refiner_blender_net_production import (
    EiaPetroleumWeeklyRefinerBlenderNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.weekly_refiner_net_production import (
    EiaPetroleumWeeklyRefinerNetProductionFetcher,
)
from openbb_us_eia.models.petroleum.weekly_retail_gasoline_and_diesel_prices import (
    EiaPetroleumWeeklyRetailGasolineAndDieselPricesFetcher,
)
from openbb_us_eia.models.petroleum.weekly_stocks import EiaPetroleumWeeklyStocksFetcher
from openbb_us_eia.models.petroleum.weekly_supply_estimates import (
    EiaPetroleumWeeklySupplyEstimatesFetcher,
)
from openbb_us_eia.models.petroleum.working_storage_capacity_at_operable_refineries import (
    EiaPetroleumWorkingStorageCapacityAtOperableRefineriesFetcher,
)
from openbb_us_eia.models.seds import EiaSedsFetcher
from openbb_us_eia.models.state_electricity_profiles.advanced_metering_infrastructure import (
    EiaStateElectricityProfilesAdvancedMeteringInfrastructureFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.costs_and_savings_from_energy_efficiency_programs import (
    EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.electricity_net_metering_customers_and_capacity import (
    EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.emissions_by_state_by_fuel import (
    EiaStateElectricityProfilesEmissionsByStateByFuelFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.generating_capacity import (
    EiaStateElectricityProfilesGeneratingCapacityFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.state_rankings_for_key_statistics import (
    EiaStateElectricityProfilesStateRankingsForKeyStatisticsFetcher,
)
from openbb_us_eia.models.state_electricity_profiles.supply_and_disposition_of_electricity import (
    EiaStateElectricityProfilesSupplyAndDispositionOfElectricityFetcher,
)
from openbb_us_eia.models.total_energy import EiaTotalEnergyFetcher

DATASET_FETCHERS = {
    "EiaAeo": EiaAeoFetcher,
    "EiaCoalAggregateProduction": EiaCoalAggregateProductionFetcher,
    "EiaCoalByMineByPlant": EiaCoalByMineByPlantFetcher,
    "EiaCoalConsumptionAndQuality": EiaCoalConsumptionAndQualityFetcher,
    "EiaCoalExportsImportsQuantityPrice": EiaCoalExportsImportsQuantityPriceFetcher,
    "EiaCoalMarketSalesPrice": EiaCoalMarketSalesPriceFetcher,
    "EiaCoalMineAggregates": EiaCoalMineAggregatesFetcher,
    "EiaCoalMineProduction": EiaCoalMineProductionFetcher,
    "EiaCoalMineStateAggregates": EiaCoalMineStateAggregatesFetcher,
    "EiaCoalPlantAggregates": EiaCoalPlantAggregatesFetcher,
    "EiaCoalPlantStateAggregates": EiaCoalPlantStateAggregatesFetcher,
    "EiaCoalPriceByRank": EiaCoalPriceByRankFetcher,
    "EiaCoalReceipts": EiaCoalReceiptsFetcher,
    "EiaCoalReservesCapacity": EiaCoalReservesCapacityFetcher,
    "EiaCrudeOilImports": EiaCrudeOilImportsFetcher,
    "EiaDensifiedBiomassCapacityByRegion": EiaDensifiedBiomassCapacityByRegionFetcher,
    "EiaDensifiedBiomassCharacteristicsByRegion": EiaDensifiedBiomassCharacteristicsByRegionFetcher,
    "EiaDensifiedBiomassExportSalesAndPrice": EiaDensifiedBiomassExportSalesAndPriceFetcher,
    "EiaDensifiedBiomassFeedstocksAndCosts": EiaDensifiedBiomassFeedstocksAndCostsFetcher,
    "EiaDensifiedBiomassInventoriesByRegion": EiaDensifiedBiomassInventoriesByRegionFetcher,
    "EiaDensifiedBiomassProductionByRegion": EiaDensifiedBiomassProductionByRegionFetcher,
    "EiaDensifiedBiomassSalesAndPriceByRegion": EiaDensifiedBiomassSalesAndPriceByRegionFetcher,
    "EiaDensifiedBiomassWoodPelletPlantCapacity": EiaDensifiedBiomassWoodPelletPlantCapacityFetcher,
    "EiaElectricityElectricPowerOperations": EiaElectricityElectricPowerOperationsFetcher,
    "EiaElectricityElectricPowerOperationsForIndividualPowerPlants": EiaElectricityElectricPowerOperationsForIndividualPowerPlantsFetcher,
    "EiaElectricityElectricitySalesToUltimateCustomers": EiaElectricityElectricitySalesToUltimateCustomersFetcher,
    "EiaElectricityGridDemand": EiaElectricityGridDemandFetcher,
    "EiaElectricityGridDemandBySubregion": EiaElectricityGridDemandBySubregionFetcher,
    "EiaElectricityGridGenerationByFuel": EiaElectricityGridGenerationByFuelFetcher,
    "EiaElectricityGridInterchange": EiaElectricityGridInterchangeFetcher,
    "EiaElectricityInventoryOfOperableGenerators": EiaElectricityInventoryOfOperableGeneratorsFetcher,
    "EiaIeo": EiaIeoFetcher,
    "EiaInternational": EiaInternationalFetcher,
    "EiaNaturalGasAssociatedDissolvedProvedReserves": EiaNaturalGasAssociatedDissolvedProvedReservesFetcher,
    "EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWells": EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsFetcher,
    "EiaNaturalGasCoalbedMethane": EiaNaturalGasCoalbedMethaneFetcher,
    "EiaNaturalGasCoalbedMethaneProduction": EiaNaturalGasCoalbedMethaneProductionFetcher,
    "EiaNaturalGasCostsOfCrudeOilAndNaturalGasWellsDrilled": EiaNaturalGasCostsOfCrudeOilAndNaturalGasWellsDrilledFetcher,
    "EiaNaturalGasCrudeOilAndNaturalGasDrillingActivity": EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityFetcher,
    "EiaNaturalGasCrudeOilAndNaturalGasExploratoryAndDevelopmentWells": EiaNaturalGasCrudeOilAndNaturalGasExploratoryAndDevelopmentWellsFetcher,
    "EiaNaturalGasCrudeOilPlusLeaseCondensate": EiaNaturalGasCrudeOilPlusLeaseCondensateFetcher,
    "EiaNaturalGasDryNaturalGasProvedReserves": EiaNaturalGasDryNaturalGasProvedReservesFetcher,
    "EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReserves": EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesFetcher,
    "EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWells": EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsFetcher,
    "EiaNaturalGasGulfOfAmericaFederalOffshoreProduction": EiaNaturalGasGulfOfAmericaFederalOffshoreProductionFetcher,
    "EiaNaturalGasHeatContentOfNaturalGasConsumed": EiaNaturalGasHeatContentOfNaturalGasConsumedFetcher,
    "EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByState": EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateFetcher,
    "EiaNaturalGasLeaseCondensate": EiaNaturalGasLeaseCondensateFetcher,
    "EiaNaturalGasLeaseCondensateProduction": EiaNaturalGasLeaseCondensateProductionFetcher,
    "EiaNaturalGasLngStorageAdditionsAndWithdrawals": EiaNaturalGasLngStorageAdditionsAndWithdrawalsFetcher,
    "EiaNaturalGasMaximumUsActiveSeismicCrewCounts": EiaNaturalGasMaximumUsActiveSeismicCrewCountsFetcher,
    "EiaNaturalGasNaturalGasAnnualSupplyDispositionByState": EiaNaturalGasNaturalGasAnnualSupplyDispositionByStateFetcher,
    "EiaNaturalGasNaturalGasConsumptionByEndUse": EiaNaturalGasNaturalGasConsumptionByEndUseFetcher,
    "EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthers": EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersFetcher,
    "EiaNaturalGasNaturalGasGrossWithdrawalsAndProduction": EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionFetcher,
    "EiaNaturalGasNaturalGasLiquidsProvedReserves": EiaNaturalGasNaturalGasLiquidsProvedReservesFetcher,
    "EiaNaturalGasNaturalGasPlantLiquidsProduction": EiaNaturalGasNaturalGasPlantLiquidsProductionFetcher,
    "EiaNaturalGasNaturalGasPlantProcessing": EiaNaturalGasNaturalGasPlantProcessingFetcher,
    "EiaNaturalGasNaturalGasPrices": EiaNaturalGasNaturalGasPricesFetcher,
    "EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparation": EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationFetcher,
    "EiaNaturalGasNaturalGasReservesSummaryAsOfDec31": EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Fetcher,
    "EiaNaturalGasNaturalGasSpotAndFuturesPrices": EiaNaturalGasNaturalGasSpotAndFuturesPricesFetcher,
    "EiaNaturalGasNaturalGasSummary": EiaNaturalGasNaturalGasSummaryFetcher,
    "EiaNaturalGasNaturalGasWellheadValueAndMarketedProduction": EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionFetcher,
    "EiaNaturalGasNonassociatedProvedReserves": EiaNaturalGasNonassociatedProvedReservesFetcher,
    "EiaNaturalGasNumberOfGasProducingOilWells": EiaNaturalGasNumberOfGasProducingOilWellsFetcher,
    "EiaNaturalGasNumberOfNaturalGasConsumers": EiaNaturalGasNumberOfNaturalGasConsumersFetcher,
    "EiaNaturalGasNumberOfProducingGasWells": EiaNaturalGasNumberOfProducingGasWellsFetcher,
    "EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGas": EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasFetcher,
    "EiaNaturalGasPlantLiquidsInProvedReserves": EiaNaturalGasPlantLiquidsInProvedReservesFetcher,
    "EiaNaturalGasProvedNonproducingReserves": EiaNaturalGasProvedNonproducingReservesFetcher,
    "EiaNaturalGasResidentialAndCommercialPricesSelectedStates": EiaNaturalGasResidentialAndCommercialPricesSelectedStatesFetcher,
    "EiaNaturalGasShaleGas": EiaNaturalGasShaleGasFetcher,
    "EiaNaturalGasShaleGasProduction": EiaNaturalGasShaleGasProductionFetcher,
    "EiaNaturalGasShareOfTotalUsNaturalGasDeliveredToConsumers": EiaNaturalGasShareOfTotalUsNaturalGasDeliveredToConsumersFetcher,
    "EiaNaturalGasSupplementalGasSupplies": EiaNaturalGasSupplementalGasSuppliesFetcher,
    "EiaNaturalGasUndergroundNaturalGasStorageByAllOperators": EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsFetcher,
    "EiaNaturalGasUndergroundNaturalGasStorageCapacity": EiaNaturalGasUndergroundNaturalGasStorageCapacityFetcher,
    "EiaNaturalGasUsNaturalGasExportsAndReExportsByCountry": EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryFetcher,
    "EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExit": EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitFetcher,
    "EiaNaturalGasUsNaturalGasImportsByCountry": EiaNaturalGasUsNaturalGasImportsByCountryFetcher,
    "EiaNaturalGasUsNaturalGasImportsByPointOfEntry": EiaNaturalGasUsNaturalGasImportsByPointOfEntryFetcher,
    "EiaNaturalGasUsNaturalGasImportsExportsByState": EiaNaturalGasUsNaturalGasImportsExportsByStateFetcher,
    "EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalance": EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceFetcher,
    "EiaNaturalGasUsUndergroundNaturalGasStorageByStorageType": EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeFetcher,
    "EiaNaturalGasWeeklyWorkingGasInUndergroundStorage": EiaNaturalGasWeeklyWorkingGasInUndergroundStorageFetcher,
    "EiaNuclearOutagesFacilityLevelNuclearOutages": EiaNuclearOutagesFacilityLevelNuclearOutagesFetcher,
    "EiaNuclearOutagesGeneratorLevelNuclearOutages": EiaNuclearOutagesGeneratorLevelNuclearOutagesFetcher,
    "EiaNuclearOutagesUsNuclearOutages": EiaNuclearOutagesUsNuclearOutagesFetcher,
    "EiaPetroleumAdjustedDistillateFuelOilAndKeroseneSalesByEndUse": EiaPetroleumAdjustedDistillateFuelOilAndKeroseneSalesByEndUseFetcher,
    "EiaPetroleumAdjustedSalesOfDistillateFuelOilByEndUse": EiaPetroleumAdjustedSalesOfDistillateFuelOilByEndUseFetcher,
    "EiaPetroleumAdjustedSalesOfKeroseneByEndUse": EiaPetroleumAdjustedSalesOfKeroseneByEndUseFetcher,
    "EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUse": EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseFetcher,
    "EiaPetroleumAverageDepthOfCrudeOilAndNaturalGasWells": EiaPetroleumAverageDepthOfCrudeOilAndNaturalGasWellsFetcher,
    "EiaPetroleumBiofuelsOperableProductionCapacity": EiaPetroleumBiofuelsOperableProductionCapacityFetcher,
    "EiaPetroleumBlenderNetInput": EiaPetroleumBlenderNetInputFetcher,
    "EiaPetroleumBlenderNetProduction": EiaPetroleumBlenderNetProductionFetcher,
    "EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilled": EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledFetcher,
    "EiaPetroleumCrudeFirstPurchasePricesSelectedStreams": EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsFetcher,
    "EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravity": EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityFetcher,
    "EiaPetroleumCrudeOilAndNaturalGasDrillingActivity": EiaPetroleumCrudeOilAndNaturalGasDrillingActivityFetcher,
    "EiaPetroleumCrudeOilAndNaturalGasExploratoryAndDevelopmentWells": EiaPetroleumCrudeOilAndNaturalGasExploratoryAndDevelopmentWellsFetcher,
    "EiaPetroleumCrudeOilInputQualities": EiaPetroleumCrudeOilInputQualitiesFetcher,
    "EiaPetroleumCrudeOilProduction": EiaPetroleumCrudeOilProductionFetcher,
    "EiaPetroleumCrudeOilProvedReservesReservesChangesAndProduction": EiaPetroleumCrudeOilProvedReservesReservesChangesAndProductionFetcher,
    "EiaPetroleumCrudeOilStocksAtTankFarmsPipelines": EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesFetcher,
    "EiaPetroleumCrudePlusLeaseCondensateProvedReserves": EiaPetroleumCrudePlusLeaseCondensateProvedReservesFetcher,
    "EiaPetroleumDistillateFuelOilAndKeroseneSalesByEndUse": EiaPetroleumDistillateFuelOilAndKeroseneSalesByEndUseFetcher,
    "EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravity": EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityFetcher,
    "EiaPetroleumDomesticCrudeOilFirstPurchasePricesByArea": EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaFetcher,
    "EiaPetroleumDownstreamChargeCapacityOfOperablePetroleumRefineries": EiaPetroleumDownstreamChargeCapacityOfOperablePetroleumRefineriesFetcher,
    "EiaPetroleumDownstreamProcessingOfFreshFeedInput": EiaPetroleumDownstreamProcessingOfFreshFeedInputFetcher,
    "EiaPetroleumExports": EiaPetroleumExportsFetcher,
    "EiaPetroleumExportsByDestination": EiaPetroleumExportsByDestinationFetcher,
    "EiaPetroleumFeedstocksConsumedForProductionOfBiofuels": EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsFetcher,
    "EiaPetroleumFobCostsOfImportedCrudeOilByApiGravity": EiaPetroleumFobCostsOfImportedCrudeOilByApiGravityFetcher,
    "EiaPetroleumFobCostsOfImportedCrudeOilByArea": EiaPetroleumFobCostsOfImportedCrudeOilByAreaFetcher,
    "EiaPetroleumFobCostsOfImportedCrudeOilForSelectedCrudeStreams": EiaPetroleumFobCostsOfImportedCrudeOilForSelectedCrudeStreamsFetcher,
    "EiaPetroleumFootageDrilledForCrudeOilAndNaturalGasWells": EiaPetroleumFootageDrilledForCrudeOilAndNaturalGasWellsFetcher,
    "EiaPetroleumFuelConsumedAtBiofuelsPlants": EiaPetroleumFuelConsumedAtBiofuelsPlantsFetcher,
    "EiaPetroleumFuelConsumedAtRefineries": EiaPetroleumFuelConsumedAtRefineriesFetcher,
    "EiaPetroleumGasolinePricesByFormulationGradeSalesType": EiaPetroleumGasolinePricesByFormulationGradeSalesTypeFetcher,
    "EiaPetroleumGulfOfAmericaFederalOffshoreProduction": EiaPetroleumGulfOfAmericaFederalOffshoreProductionFetcher,
    "EiaPetroleumImportsByAreaOfEntry": EiaPetroleumImportsByAreaOfEntryFetcher,
    "EiaPetroleumImportsByProcessingArea": EiaPetroleumImportsByProcessingAreaFetcher,
    "EiaPetroleumImportsOfResidualFuel": EiaPetroleumImportsOfResidualFuelFetcher,
    "EiaPetroleumLandedCostsOfImportedCrudeByApiGravity": EiaPetroleumLandedCostsOfImportedCrudeByApiGravityFetcher,
    "EiaPetroleumLandedCostsOfImportedCrudeByArea": EiaPetroleumLandedCostsOfImportedCrudeByAreaFetcher,
    "EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreams": EiaPetroleumLandedCostsOfImportedCrudeForSelectedCrudeStreamsFetcher,
    "EiaPetroleumMaximumUsActiveSeismicCrewCounts": EiaPetroleumMaximumUsActiveSeismicCrewCountsFetcher,
    "EiaPetroleumMovementsBetweenPadDistricts": EiaPetroleumMovementsBetweenPadDistrictsFetcher,
    "EiaPetroleumMovementsByPipelineBetweenPadDistricts": EiaPetroleumMovementsByPipelineBetweenPadDistrictsFetcher,
    "EiaPetroleumMovementsByRailBetweenPadDistricts": EiaPetroleumMovementsByRailBetweenPadDistrictsFetcher,
    "EiaPetroleumMovementsByTankerAndBargeBetweenPadDistricts": EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsFetcher,
    "EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRail": EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailFetcher,
    "EiaPetroleumNaturalGasFeedstockForHydrogen": EiaPetroleumNaturalGasFeedstockForHydrogenFetcher,
    "EiaPetroleumNaturalGasPlantFieldProduction": EiaPetroleumNaturalGasPlantFieldProductionFetcher,
    "EiaPetroleumNaturalGasPlantStocks": EiaPetroleumNaturalGasPlantStocksFetcher,
    "EiaPetroleumNetReceiptsBetweenPadDistricts": EiaPetroleumNetReceiptsBetweenPadDistrictsFetcher,
    "EiaPetroleumNo2DistillatePricesBySalesType": EiaPetroleumNo2DistillatePricesBySalesTypeFetcher,
    "EiaPetroleumNumberAndCapacityOfPetroleumRefineries": EiaPetroleumNumberAndCapacityOfPetroleumRefineriesFetcher,
    "EiaPetroleumNymexFuturesPrices": EiaPetroleumNymexFuturesPricesFetcher,
    "EiaPetroleumOxygenateProduction": EiaPetroleumOxygenateProductionFetcher,
    "EiaPetroleumPadDistrictExportsByDestination": EiaPetroleumPadDistrictExportsByDestinationFetcher,
    "EiaPetroleumPadDistrictImportsByCountryOfOrigin": EiaPetroleumPadDistrictImportsByCountryOfOriginFetcher,
    "EiaPetroleumPercentagesOfTotalImportedCrudeOilByApiGravity": EiaPetroleumPercentagesOfTotalImportedCrudeOilByApiGravityFetcher,
    "EiaPetroleumPricesSalesVolumesStocksByState": EiaPetroleumPricesSalesVolumesStocksByStateFetcher,
    "EiaPetroleumPrimeSupplierSalesVolumes": EiaPetroleumPrimeSupplierSalesVolumesFetcher,
    "EiaPetroleumProductSupplied": EiaPetroleumProductSuppliedFetcher,
    "EiaPetroleumProductionCapacityOfOperablePetroleumRefineries": EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesFetcher,
    "EiaPetroleumPropanePricesBySalesType": EiaPetroleumPropanePricesBySalesTypeFetcher,
    "EiaPetroleumProvedNonproducingReserves": EiaPetroleumProvedNonproducingReservesFetcher,
    "EiaPetroleumRefinerAcquisitionCostOfCrudeOil": EiaPetroleumRefinerAcquisitionCostOfCrudeOilFetcher,
    "EiaPetroleumRefinerGasolinePricesByGradeAndSalesType": EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeFetcher,
    "EiaPetroleumRefinerMotorGasolineSalesVolumes": EiaPetroleumRefinerMotorGasolineSalesVolumesFetcher,
    "EiaPetroleumRefinerPetroleumProductPricesBySalesType": EiaPetroleumRefinerPetroleumProductPricesBySalesTypeFetcher,
    "EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumes": EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesFetcher,
    "EiaPetroleumRefinerSalesVolumesOfOtherPetroleumProducts": EiaPetroleumRefinerSalesVolumesOfOtherPetroleumProductsFetcher,
    "EiaPetroleumRefineryBlenderNetInput": EiaPetroleumRefineryBlenderNetInputFetcher,
    "EiaPetroleumRefineryBlenderNetProduction": EiaPetroleumRefineryBlenderNetProductionFetcher,
    "EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByState": EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateFetcher,
    "EiaPetroleumRefineryNetInput": EiaPetroleumRefineryNetInputFetcher,
    "EiaPetroleumRefineryNetProduction": EiaPetroleumRefineryNetProductionFetcher,
    "EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportation": EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationFetcher,
    "EiaPetroleumRefineryStocks": EiaPetroleumRefineryStocksFetcher,
    "EiaPetroleumRefineryUtilizationAndCapacity": EiaPetroleumRefineryUtilizationAndCapacityFetcher,
    "EiaPetroleumRefineryYield": EiaPetroleumRefineryYieldFetcher,
    "EiaPetroleumResidualFuelOilPricesBySalesType": EiaPetroleumResidualFuelOilPricesBySalesTypeFetcher,
    "EiaPetroleumSalesOfDistillateFuelOilByEndUse": EiaPetroleumSalesOfDistillateFuelOilByEndUseFetcher,
    "EiaPetroleumSalesOfKeroseneByEndUse": EiaPetroleumSalesOfKeroseneByEndUseFetcher,
    "EiaPetroleumSalesOfResidualFuelOilByEndUse": EiaPetroleumSalesOfResidualFuelOilByEndUseFetcher,
    "EiaPetroleumShellStorageCapacityAtOperableRefineries": EiaPetroleumShellStorageCapacityAtOperableRefineriesFetcher,
    "EiaPetroleumSpotPrices": EiaPetroleumSpotPricesFetcher,
    "EiaPetroleumStocksByType": EiaPetroleumStocksByTypeFetcher,
    "EiaPetroleumStocksOfSelectedProducts": EiaPetroleumStocksOfSelectedProductsFetcher,
    "EiaPetroleumSupplyAndDisposition": EiaPetroleumSupplyAndDispositionFetcher,
    "EiaPetroleumUsBiodieselProductionCapacitySalesAndStocks": EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksFetcher,
    "EiaPetroleumUsCrudeOilSupplyDisposition": EiaPetroleumUsCrudeOilSupplyDispositionFetcher,
    "EiaPetroleumUsImportsByCountryOfOrigin": EiaPetroleumUsImportsByCountryOfOriginFetcher,
    "EiaPetroleumUsNetImportsByCountry": EiaPetroleumUsNetImportsByCountryFetcher,
    "EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesType": EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeFetcher,
    "EiaPetroleumUsWeeklyProductSupplied": EiaPetroleumUsWeeklyProductSuppliedFetcher,
    "EiaPetroleumWeeklyBlenderNetProduction": EiaPetroleumWeeklyBlenderNetProductionFetcher,
    "EiaPetroleumWeeklyCrudeImportsByTop10Origins": EiaPetroleumWeeklyCrudeImportsByTop10OriginsFetcher,
    "EiaPetroleumWeeklyEthanolPlantProduction": EiaPetroleumWeeklyEthanolPlantProductionFetcher,
    "EiaPetroleumWeeklyHeatingOilAndPropanePrices": EiaPetroleumWeeklyHeatingOilAndPropanePricesFetcher,
    "EiaPetroleumWeeklyImportsExports": EiaPetroleumWeeklyImportsExportsFetcher,
    "EiaPetroleumWeeklyInputsUtilization": EiaPetroleumWeeklyInputsUtilizationFetcher,
    "EiaPetroleumWeeklyRefinerBlenderNetProduction": EiaPetroleumWeeklyRefinerBlenderNetProductionFetcher,
    "EiaPetroleumWeeklyRefinerNetProduction": EiaPetroleumWeeklyRefinerNetProductionFetcher,
    "EiaPetroleumWeeklyRetailGasolineAndDieselPrices": EiaPetroleumWeeklyRetailGasolineAndDieselPricesFetcher,
    "EiaPetroleumWeeklyStocks": EiaPetroleumWeeklyStocksFetcher,
    "EiaPetroleumWeeklySupplyEstimates": EiaPetroleumWeeklySupplyEstimatesFetcher,
    "EiaPetroleumWorkingStorageCapacityAtOperableRefineries": EiaPetroleumWorkingStorageCapacityAtOperableRefineriesFetcher,
    "EiaSeds": EiaSedsFetcher,
    "EiaStateElectricityProfilesAdvancedMeteringInfrastructure": EiaStateElectricityProfilesAdvancedMeteringInfrastructureFetcher,
    "EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyPrograms": EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsFetcher,
    "EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacity": EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityFetcher,
    "EiaStateElectricityProfilesEmissionsByStateByFuel": EiaStateElectricityProfilesEmissionsByStateByFuelFetcher,
    "EiaStateElectricityProfilesGeneratingCapacity": EiaStateElectricityProfilesGeneratingCapacityFetcher,
    "EiaStateElectricityProfilesStateRankingsForKeyStatistics": EiaStateElectricityProfilesStateRankingsForKeyStatisticsFetcher,
    "EiaStateElectricityProfilesSupplyAndDispositionOfElectricity": EiaStateElectricityProfilesSupplyAndDispositionOfElectricityFetcher,
    "EiaTotalEnergy": EiaTotalEnergyFetcher,
}
