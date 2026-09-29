"""USDA provider module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_government_us.usda.models.adoption_of_genetically_engineered_crops_in_the_united_states import (
    AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesFetcher,
)
from openbb_government_us.usda.models.agricultural_and_food_research_and_development_expenditures_in_the_united_states import (
    AgriculturalAndFoodRdExpendituresFetcher,
)
from openbb_government_us.usda.models.agricultural_exchange_rates import (
    AgriculturalExchangeRatesFetcher,
)
from openbb_government_us.usda.models.agricultural_productivity import (
    AgriculturalProductivityFetcher,
)
from openbb_government_us.usda.models.agricultural_trade_multipliers import (
    AgriculturalTradeMultipliersFetcher,
)
from openbb_government_us.usda.models.area_and_road_ruggedness_scales import (
    AreaAndRoadRuggednessScalesFetcher,
)
from openbb_government_us.usda.models.bell_report import FasBellReportFetcher
from openbb_government_us.usda.models.commodity_costs_and_returns import (
    CommodityCostsAndReturnsFetcher,
)
from openbb_government_us.usda.models.commodity_psd_data import (
    UsdaCommodityPsdDataFetcher,
)
from openbb_government_us.usda.models.commodity_psd_report import (
    UsdaCommodityPsdReportFetcher,
)
from openbb_government_us.usda.models.commuting_zones_and_labor_market_areas import (
    CommutingZonesAndLaborMarketAreasFetcher,
)
from openbb_government_us.usda.models.cost_estimates_of_foodborne_illnesses import (
    CostEstimatesOfFoodborneIllnessesFetcher,
)
from openbb_government_us.usda.models.cotton_wool_and_textile_data import (
    CottonWoolAndTextileDataFetcher,
)
from openbb_government_us.usda.models.county_typology_codes import (
    CountyTypologyCodesFetcher,
)
from openbb_government_us.usda.models.dairy_data import DairyDataFetcher
from openbb_government_us.usda.models.eating_and_health_module_atus import (
    EatingAndHealthModuleAtusFetcher,
)
from openbb_government_us.usda.models.ers_publication_download import (
    ErsPublicationDownloadFetcher,
)
from openbb_government_us.usda.models.ers_publications import ErsPublicationsFetcher
from openbb_government_us.usda.models.farm_household_income_and_characteristics import (
    FarmHouseholdIncomeAndCharacteristicsFetcher,
)
from openbb_government_us.usda.models.farm_income_and_wealth_statistics import (
    FarmIncomeAndWealthStatisticsFetcher,
)
from openbb_government_us.usda.models.feed_grains_database import (
    FeedGrainsDatabaseFetcher,
)
from openbb_government_us.usda.models.fertilizer_use_and_price import (
    FertilizerUseAndPriceFetcher,
)
from openbb_government_us.usda.models.food_at_home_monthly_area_prices import (
    FoodAtHomeMonthlyAreaPricesFetcher,
)
from openbb_government_us.usda.models.food_availability_per_capita_data_system import (
    FoodAvailabilityPerCapitaDataSystemFetcher,
)
from openbb_government_us.usda.models.food_consumption_nutrient_intakes_and_diet_quality import (
    FoodConsumptionNutrientIntakesAndDietQualityFetcher,
)
from openbb_government_us.usda.models.food_dollar_series import (
    FoodDollarSeriesFetcher,
)
from openbb_government_us.usda.models.food_expenditure_series import (
    FoodExpenditureSeriesFetcher,
)
from openbb_government_us.usda.models.food_price_outlook import (
    FoodPriceOutlookFetcher,
)
from openbb_government_us.usda.models.food_security_in_the_united_states import (
    FoodSecurityInTheUnitedStatesFetcher,
)
from openbb_government_us.usda.models.frontier_and_remote_area_codes import (
    FrontierAndRemoteAreaCodesFetcher,
)
from openbb_government_us.usda.models.fruit_and_tree_nuts_data import (
    FruitAndTreeNutsDataFetcher,
)
from openbb_government_us.usda.models.fruit_and_vegetable_prices import (
    FruitAndVegetablePricesFetcher,
)
from openbb_government_us.usda.models.global_food_assessment import (
    GlobalFoodAssessmentFetcher,
)
from openbb_government_us.usda.models.international_agricultural_productivity import (
    InternationalAgriculturalProductivityFetcher,
)
from openbb_government_us.usda.models.international_baseline_data import (
    InternationalBaselineDataFetcher,
)
from openbb_government_us.usda.models.international_macroeconomic_data_set import (
    InternationalMacroeconomicDataSetFetcher,
)
from openbb_government_us.usda.models.livestock_and_meat_domestic_data import (
    LivestockAndMeatDomesticDataFetcher,
)
from openbb_government_us.usda.models.livestock_and_meat_international_trade_data import (
    LivestockAndMeatInternationalTradeDataFetcher,
)
from openbb_government_us.usda.models.major_land_uses import MajorLandUsesFetcher
from openbb_government_us.usda.models.meat_price_spreads import (
    MeatPriceSpreadsFetcher,
)
from openbb_government_us.usda.models.milk_cost_of_production import (
    MilkCostOfProductionFetcher,
)
from openbb_government_us.usda.models.natural_amenities_scale import (
    NaturalAmenitiesScaleFetcher,
)
from openbb_government_us.usda.models.normalized_prices import (
    NormalizedPricesFetcher,
)
from openbb_government_us.usda.models.oil_crops_yearbook import (
    OilCropsYearbookFetcher,
)
from openbb_government_us.usda.models.poverty_area_measures import (
    PovertyAreaMeasuresFetcher,
)
from openbb_government_us.usda.models.price_spreads import (
    FarmToConsumerPriceSpreadsFetcher,
)
from openbb_government_us.usda.models.purchase_to_plate import (
    PurchaseToPlateFetcher,
)
from openbb_government_us.usda.models.report_calendar import FasReportCalendarFetcher
from openbb_government_us.usda.models.resource_requirements_of_food_demand import (
    ResourceRequirementsOfFoodDemandFetcher,
)
from openbb_government_us.usda.models.rice_yearbook import RiceYearbookFetcher
from openbb_government_us.usda.models.rural_urban_commuting_area_codes import (
    RuralUrbanCommutingAreaCodesFetcher,
)
from openbb_government_us.usda.models.rural_urban_continuum_codes import (
    RuralUrbanContinuumCodesFetcher,
)
from openbb_government_us.usda.models.season_average_price_forecasts import (
    SeasonAveragePriceForecastsFetcher,
)
from openbb_government_us.usda.models.snap_policy_data_sets import (
    SnapPolicyDataSetsFetcher,
)
from openbb_government_us.usda.models.state_agricultural_trade import (
    StateAgriculturalTradeFetcher,
)
from openbb_government_us.usda.models.sugar_sweeteners_yearbook import (
    SugarSweetenersYearbookFetcher,
)
from openbb_government_us.usda.models.urban_influence_codes import (
    UrbanInfluenceCodesFetcher,
)
from openbb_government_us.usda.models.us_agricultural_trade import (
    UsAgriculturalTradeFetcher,
)
from openbb_government_us.usda.models.us_bioenergy_statistics import (
    UsBioenergyStatisticsFetcher,
)
from openbb_government_us.usda.models.us_food_imports import UsFoodImportsFetcher
from openbb_government_us.usda.models.vegetables_and_pulses import (
    VegetablesAndPulsesFetcher,
)
from openbb_government_us.usda.models.weather_bulletin import (
    UsdaWeatherBulletinFetcher,
)
from openbb_government_us.usda.models.weather_bulletin_download import (
    UsdaWeatherBulletinDownloadFetcher,
)
from openbb_government_us.usda.models.wheat_data import WheatDataFetcher

COMMODITY_INSTALLED = find_spec("openbb_commodity") is not None

usda_provider = Provider(
    name="usda",
    website="https://www.usda.gov",
    description="""Data published by the U.S. Department of Agriculture -
Production, Supply and Distribution (PSD) reports and time series from the
Foreign Agricultural Service, and the Weekly Weather and Crop Bulletin from
the Economics, Statistics and Market Information System. All sources are
public and keyless.""",
    fetcher_dict={
        "AdoptionOfGeneticallyEngineeredCropsInTheUnitedStates": (
            AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesFetcher
        ),
        "AgriculturalAndFoodRdExpenditures": AgriculturalAndFoodRdExpendituresFetcher,
        "AgriculturalExchangeRates": AgriculturalExchangeRatesFetcher,
        "AgriculturalProductivity": AgriculturalProductivityFetcher,
        "AgriculturalTradeMultipliers": AgriculturalTradeMultipliersFetcher,
        "AreaAndRoadRuggednessScales": AreaAndRoadRuggednessScalesFetcher,
        "CommodityCostsAndReturns": CommodityCostsAndReturnsFetcher,
        "CommodityPsdData": UsdaCommodityPsdDataFetcher,
        "CommodityPsdReport": UsdaCommodityPsdReportFetcher,
        "CommutingZonesAndLaborMarketAreas": (CommutingZonesAndLaborMarketAreasFetcher),
        "CostEstimatesOfFoodborneIllnesses": CostEstimatesOfFoodborneIllnessesFetcher,
        "CottonWoolAndTextileData": CottonWoolAndTextileDataFetcher,
        "CountyTypologyCodes": CountyTypologyCodesFetcher,
        "DairyData": DairyDataFetcher,
        "EatingAndHealthModuleAtus": EatingAndHealthModuleAtusFetcher,
        "ErsPublicationDownload": ErsPublicationDownloadFetcher,
        "ErsPublications": ErsPublicationsFetcher,
        "FarmHouseholdIncomeAndCharacteristics": (
            FarmHouseholdIncomeAndCharacteristicsFetcher
        ),
        "FarmIncomeAndWealthStatistics": FarmIncomeAndWealthStatisticsFetcher,
        "FarmToConsumerPriceSpreads": FarmToConsumerPriceSpreadsFetcher,
        "FasBellReport": FasBellReportFetcher,
        "FasReportCalendar": FasReportCalendarFetcher,
        "FeedGrainsDatabase": FeedGrainsDatabaseFetcher,
        "FertilizerUseAndPrice": FertilizerUseAndPriceFetcher,
        "FoodAtHomeMonthlyAreaPrices": FoodAtHomeMonthlyAreaPricesFetcher,
        "FoodAvailabilityPerCapitaDataSystem": (
            FoodAvailabilityPerCapitaDataSystemFetcher
        ),
        "FoodConsumptionNutrientIntakesAndDietQuality": (
            FoodConsumptionNutrientIntakesAndDietQualityFetcher
        ),
        "FoodDollarSeries": FoodDollarSeriesFetcher,
        "FoodExpenditureSeries": FoodExpenditureSeriesFetcher,
        "FoodPriceOutlook": FoodPriceOutlookFetcher,
        "FoodSecurityInTheUnitedStates": FoodSecurityInTheUnitedStatesFetcher,
        "FrontierAndRemoteAreaCodes": FrontierAndRemoteAreaCodesFetcher,
        "FruitAndTreeNutsData": FruitAndTreeNutsDataFetcher,
        "FruitAndVegetablePrices": FruitAndVegetablePricesFetcher,
        "GlobalFoodAssessment": GlobalFoodAssessmentFetcher,
        "InternationalAgriculturalProductivity": (
            InternationalAgriculturalProductivityFetcher
        ),
        "InternationalBaselineData": InternationalBaselineDataFetcher,
        "InternationalMacroeconomicDataSet": InternationalMacroeconomicDataSetFetcher,
        "LivestockAndMeatDomesticData": LivestockAndMeatDomesticDataFetcher,
        "LivestockAndMeatInternationalTradeData": (
            LivestockAndMeatInternationalTradeDataFetcher
        ),
        "MajorLandUses": MajorLandUsesFetcher,
        "MeatPriceSpreads": MeatPriceSpreadsFetcher,
        "MilkCostOfProduction": MilkCostOfProductionFetcher,
        "NaturalAmenitiesScale": NaturalAmenitiesScaleFetcher,
        "NormalizedPrices": NormalizedPricesFetcher,
        "OilCropsYearbook": OilCropsYearbookFetcher,
        "PovertyAreaMeasures": PovertyAreaMeasuresFetcher,
        "PurchaseToPlate": PurchaseToPlateFetcher,
        "ResourceRequirementsOfFoodDemand": ResourceRequirementsOfFoodDemandFetcher,
        "RiceYearbook": RiceYearbookFetcher,
        "RuralUrbanCommutingAreaCodes": RuralUrbanCommutingAreaCodesFetcher,
        "RuralUrbanContinuumCodes": RuralUrbanContinuumCodesFetcher,
        "SeasonAveragePriceForecasts": SeasonAveragePriceForecastsFetcher,
        "SnapPolicyDataSets": SnapPolicyDataSetsFetcher,
        "StateAgriculturalTrade": StateAgriculturalTradeFetcher,
        "SugarSweetenersYearbook": SugarSweetenersYearbookFetcher,
        "UrbanInfluenceCodes": UrbanInfluenceCodesFetcher,
        "UsAgriculturalTrade": UsAgriculturalTradeFetcher,
        "UsBioenergyStatistics": UsBioenergyStatisticsFetcher,
        "UsFoodImports": UsFoodImportsFetcher,
        "VegetablesAndPulses": VegetablesAndPulsesFetcher,
        "WeatherBulletin": UsdaWeatherBulletinFetcher,
        "WeatherBulletinDownload": UsdaWeatherBulletinDownloadFetcher,
        "WheatData": WheatDataFetcher,
    },
    repr_name="U.S. Department of Agriculture",
    instructions="""All endpoints use public, keyless data from USDA FAS PSD
Online and the USDA ESMIS publication service, so no credentials are
required.""",
)
