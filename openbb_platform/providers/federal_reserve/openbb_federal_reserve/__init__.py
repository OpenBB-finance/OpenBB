"""Federal Reserve provider module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_federal_reserve.models.bhcpr_report import (
    FederalReserveBhcprReportFetcher,
)
from openbb_federal_reserve.models.call_report import (
    FederalReserveCallReportFetcher,
)
from openbb_federal_reserve.models.call_report_router import (
    FederalReserveCallReportSectionedFetcher,
)
from openbb_federal_reserve.models.central_bank_holdings import (
    FederalReserveCentralBankHoldingsFetcher,
)
from openbb_federal_reserve.models.country_exposure import (
    FederalReserveCountryExposureFetcher,
)
from openbb_federal_reserve.models.custom_peer_group import (
    FederalReserveCustomPeerGroupFetcher,
)
from openbb_federal_reserve.models.executive_summary import (
    FederalReserveExecutiveSummaryFetcher,
)
from openbb_federal_reserve.models.fed_data import (
    FederalReserveDataDownloadFetcher,
)
from openbb_federal_reserve.models.federal_funds_rate import (
    FederalReserveFederalFundsRateFetcher,
)
from openbb_federal_reserve.models.ffiec.bhcpr import (
    FederalReserveBhcprFetcher,
)
from openbb_federal_reserve.models.ffiec.financial_report import (
    FederalReserveFinancialReportFetcher,
)
from openbb_federal_reserve.models.ffiec.financial_report_pdf import (
    FederalReserveFinancialReportPdfFetcher,
)
from openbb_federal_reserve.models.fomc_documents import (
    FederalReserveFomcDocumentsFetcher,
)
from openbb_federal_reserve.models.inflation_expectations import (
    FederalReserveInflationExpectationsFetcher,
)
from openbb_federal_reserve.models.institution_structure import (
    FederalReserveInstitutionStructureFetcher,
)
from openbb_federal_reserve.models.institutions import (
    FederalReserveInstitutionsFetcher,
)
from openbb_federal_reserve.models.international_portfolio_investment import (
    FederalReserveInternationalPortfolioInvestmentFetcher,
)
from openbb_federal_reserve.models.large_holding_companies import (
    FederalReserveLargeHoldingCompaniesFetcher,
)
from openbb_federal_reserve.models.list_of_banks_peer_group import (
    FederalReserveListOfBanksPeerGroupFetcher,
)
from openbb_federal_reserve.models.money_market_funds import (
    FederalReserveMoneyMarketFundsFetcher,
)
from openbb_federal_reserve.models.money_measures import (
    FederalReserveMoneyMeasuresFetcher,
)
from openbb_federal_reserve.models.overnight_bank_funding_rate import (
    FederalReserveOvernightBankFundingRateFetcher,
)
from openbb_federal_reserve.models.peer_group_average import (
    FederalReservePeerGroupAverageFetcher,
)
from openbb_federal_reserve.models.peer_group_bank import (
    FederalReservePeerGroupBankFetcher,
)
from openbb_federal_reserve.models.peer_group_distribution import (
    FederalReservePeerGroupDistributionFetcher,
)
from openbb_federal_reserve.models.primary_dealer_fails import (
    FederalReservePrimaryDealerFailsFetcher,
)
from openbb_federal_reserve.models.primary_dealer_positioning import (
    FederalReservePrimaryDealerPositioningFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_bie import (
    FederalReserveAtlantaBusinessInflationFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_gdpnow import (
    FederalReserveAtlantaGdpNowFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_market_probability import (
    FederalReserveAtlantaMarketProbabilityFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_publication_series import (
    FederalReserveAtlantaPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_publications import (
    FederalReserveAtlantaPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_sbu import (
    FederalReserveAtlantaBusinessUncertaintyFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_sticky_cpi import (
    FederalReserveAtlantaStickyCpiFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_taylor_rule import (
    FederalReserveAtlantaTaylorRuleFetcher,
    FederalReserveAtlantaTaylorRuleHeatmapFetcher,
    FederalReserveAtlantaTaylorRuleMeasuresFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_wage_growth import (
    FederalReserveAtlantaWageGrowthFetcher,
)
from openbb_federal_reserve.models.regional.boston_economic_indicators import (
    FederalReserveBostonEconomicIndicatorsFetcher,
)
from openbb_federal_reserve.models.regional.boston_publication_series import (
    FederalReserveBostonPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.boston_publications import (
    FederalReserveBostonPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.chicago_ag_credit import (
    FederalReserveChicagoAgCreditFetcher,
)
from openbb_federal_reserve.models.regional.chicago_bbki import (
    FederalReserveChicagoBraveButtersKelleyFetcher,
)
from openbb_federal_reserve.models.regional.chicago_carts import (
    FederalReserveChicagoRetailTradeFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cflmi import (
    FederalReserveChicagoLaborMarketFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cfnai import (
    FederalReserveChicagoNationalActivityFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cfsec import (
    FederalReserveChicagoEconomicConditionsFetcher,
)
from openbb_federal_reserve.models.regional.chicago_farm_loans import (
    FederalReserveChicagoFarmLoanRatesFetcher,
)
from openbb_federal_reserve.models.regional.chicago_farmland import (
    FederalReserveChicagoFarmlandValuesFetcher,
)
from openbb_federal_reserve.models.regional.chicago_mei import (
    FederalReserveChicagoMidwestEconomyFetcher,
)
from openbb_federal_reserve.models.regional.chicago_nfci import (
    FederalReserveChicagoFinancialConditionsFetcher,
)
from openbb_federal_reserve.models.regional.chicago_publication_series import (
    FederalReserveChicagoPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.chicago_publications import (
    FederalReserveChicagoPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_inflation import (
    FederalReserveClevelandInflationFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_inflation_nowcast import (
    FederalReserveClevelandInflationNowcastFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_median_cpi import (
    FederalReserveClevelandMedianCpiFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_median_cpi_components import (
    FederalReserveClevelandMedianCpiComponentsFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_publication_series import (
    FederalReserveClevelandPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_publications import (
    FederalReserveClevelandPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_systemic_risk import (
    FederalReserveClevelandSystemicRiskFetcher,
)
from openbb_federal_reserve.models.regional.dallas_agsurvey import (
    FederalReserveDallasAgSurveyFetcher,
)
from openbb_federal_reserve.models.regional.dallas_bcs import (
    FederalReserveDallasBankingFetcher,
)
from openbb_federal_reserve.models.regional.dallas_breakeven import (
    FederalReserveDallasBreakevenFetcher,
)
from openbb_federal_reserve.models.regional.dallas_dgei import (
    FederalReserveDallasDgeiFetcher,
)
from openbb_federal_reserve.models.regional.dallas_energy import (
    FederalReserveDallasEnergyFetcher,
)
from openbb_federal_reserve.models.regional.dallas_gigafactory import (
    FederalReserveDallasGigafactoryFetcher,
)
from openbb_federal_reserve.models.regional.dallas_govdebt import (
    FederalReserveDallasGovernmentDebtFetcher,
)
from openbb_federal_reserve.models.regional.dallas_igrea import (
    FederalReserveDallasIgreaFetcher,
)
from openbb_federal_reserve.models.regional.dallas_lithium import (
    FederalReserveDallasLithiumFetcher,
)
from openbb_federal_reserve.models.regional.dallas_pce import (
    FederalReserveDallasTrimmedMeanPCEFetcher,
)
from openbb_federal_reserve.models.regional.dallas_publication_series import (
    FederalReserveDallasPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.dallas_publications import (
    FederalReserveDallasPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.dallas_tli import (
    FederalReserveDallasLeadingIndexFetcher,
)
from openbb_federal_reserve.models.regional.dallas_tmos import (
    FederalReserveDallasManufacturingFetcher,
)
from openbb_federal_reserve.models.regional.dallas_tros import (
    FederalReserveDallasRetailFetcher,
)
from openbb_federal_reserve.models.regional.dallas_tssos import (
    FederalReserveDallasServiceSectorFetcher,
)
from openbb_federal_reserve.models.regional.dallas_wei import (
    FederalReserveDallasWeeklyEconomicFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_credit_survey import (
    FederalReserveKansasCityAgCreditSurveyFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_databook_archived import (
    FederalReserveKansasCityAgDatabookArchivedFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_district_surveys import (
    FederalReserveKansasCityAgDistrictSurveysFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_finance import (
    FederalReserveKansasCityAgFinanceFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_rates import (
    FederalReserveKansasCityAgRatesFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_terms_of_lending import (
    FederalReserveKansasCityAgTermsOfLendingFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_div_lmci import (
    FederalReserveKansasCityDivisionalLmciFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_fsi import (
    FederalReserveKansasCityFinancialStressFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_natural_rate import (
    FederalReserveKansasCityNaturalRateFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_prs import (
    FederalReserveKansasCityPolicyRateUncertaintyFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_publication_series import (
    FederalReserveKansasCityPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_publications import (
    FederalReserveKansasCityPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_roro import (
    FederalReserveKansasCityRiskIndexFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_business_conditions import (
    FederalReserveMinneapolisBusinessConditionsFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_claims import (
    FederalReserveMinneapolisClaimsFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_cpi import (
    FederalReserveMinneapolisCpiFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_employment import (
    FederalReserveMinneapolisEmploymentFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_gdp import (
    FederalReserveMinneapolisGdpFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_job_openings import (
    FederalReserveMinneapolisJobOpeningsFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_labor_force import (
    FederalReserveMinneapolisLaborForceFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_publication_series import (
    FederalReserveMinneapolisPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_publications import (
    FederalReserveMinneapolisPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_quits_rate import (
    FederalReserveMinneapolisQuitsRateFetcher,
)
from openbb_federal_reserve.models.regional.minneapolis_unemployment import (
    FederalReserveMinneapolisUnemploymentFetcher,
)
from openbb_federal_reserve.models.regional.new_york_bls import (
    FederalReserveNewYorkBusinessLeadersFetcher,
)
from openbb_federal_reserve.models.regional.new_york_cmdi import (
    FederalReserveNewYorkCorporateDistressFetcher,
)
from openbb_federal_reserve.models.regional.new_york_empire import (
    FederalReserveNewYorkEmpireStateFetcher,
)
from openbb_federal_reserve.models.regional.new_york_empire_reports import (
    FederalReserveNewYorkEmpireReportsFetcher,
)
from openbb_federal_reserve.models.regional.new_york_gscpi import (
    FederalReserveNewYorkSupplyChainFetcher,
)
from openbb_federal_reserve.models.regional.new_york_hhdc import (
    FederalReserveNewYorkHouseholdDebtFetcher,
)
from openbb_federal_reserve.models.regional.new_york_market_expectations import (
    FederalReserveNewYorkMarketExpectationsFetcher,
)
from openbb_federal_reserve.models.regional.new_york_market_expectations_reports import (
    FederalReserveNewYorkMarketExpectationsReportsFetcher,
)
from openbb_federal_reserve.models.regional.new_york_mct import (
    FederalReserveNewYorkCoreTrendInflationFetcher,
)
from openbb_federal_reserve.models.regional.new_york_nowcast import (
    FederalReserveNewYorkNowcastFetcher,
)
from openbb_federal_reserve.models.regional.new_york_publication_series import (
    FederalReserveNewYorkPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.new_york_publications import (
    FederalReserveNewYorkPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.new_york_sce import (
    FederalReserveNewYorkConsumerExpectationsFetcher,
)
from openbb_federal_reserve.models.regional.new_york_sce_credit import (
    FederalReserveNewYorkConsumerCreditAccessFetcher,
)
from openbb_federal_reserve.models.regional.new_york_sce_housing import (
    FederalReserveNewYorkConsumerHousingFetcher,
)
from openbb_federal_reserve.models.regional.new_york_sce_labor import (
    FederalReserveNewYorkConsumerLaborMarketFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_ads import (
    FederalReservePhiladelphiaAdsFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_anxious import (
    FederalReservePhiladelphiaAnxiousFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_atsix import (
    FederalReservePhiladelphiaAtsixFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_coincident import (
    FederalReservePhiladelphiaCoincidentFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_gdpplus import (
    FederalReservePhiladelphiaGdpPlusFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_livingston import (
    FederalReservePhiladelphiaLivingstonFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_mbos import (
    FederalReservePhiladelphiaManufacturingFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_nbos import (
    FederalReservePhiladelphiaNonmanufacturingFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_partisan import (
    FederalReservePhiladelphiaPartisanFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_publication_series import (
    FederalReservePhiladelphiaPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_publications import (
    FederalReservePhiladelphiaPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_spf import (
    FederalReservePhiladelphiaSpfFetcher,
)
from openbb_federal_reserve.models.regional.richmond_cfo import (
    FederalReserveRichmondCFOFetcher,
)
from openbb_federal_reserve.models.regional.richmond_manufacturing import (
    FederalReserveRichmondManufacturingFetcher,
)
from openbb_federal_reserve.models.regional.richmond_nei import (
    FederalReserveRichmondNonEmploymentFetcher,
)
from openbb_federal_reserve.models.regional.richmond_publication_series import (
    FederalReserveRichmondPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.richmond_publications import (
    FederalReserveRichmondPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.richmond_service_sector import (
    FederalReserveRichmondServiceSectorFetcher,
)
from openbb_federal_reserve.models.regional.richmond_sos import (
    FederalReserveRichmondRecessionIndicatorFetcher,
)
from openbb_federal_reserve.models.regional.richmond_state_survey import (
    FederalReserveRichmondStateSurveyFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_cyclical_pce import (
    FederalReserveSanFranciscoCyclicalPceFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_news_sentiment import (
    FederalReserveSanFranciscoNewsSentimentFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_proxy_funds_rate import (
    FederalReserveSanFranciscoProxyFundsRateFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_publication_series import (
    FederalReserveSanFranciscoPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_publications import (
    FederalReserveSanFranciscoPublicationsFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_short_rate_path import (
    FederalReserveSanFranciscoShortRatePathFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_supply_demand_pce import (
    FederalReserveSanFranciscoSupplyDemandPceFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_term_premium import (
    FederalReserveSanFranciscoTermPremiumFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_tfp import (
    FederalReserveSanFranciscoTfpFetcher,
)
from openbb_federal_reserve.models.regional.st_louis_fred_panel import (
    FederalReserveStLouisFredMdFetcher,
    FederalReserveStLouisFredQdFetcher,
)
from openbb_federal_reserve.models.regional.st_louis_indexes import (
    FederalReserveStLouisNationalIndexFetcher,
)
from openbb_federal_reserve.models.regional.st_louis_publication_series import (
    FederalReserveStLouisPublicationSeriesFetcher,
)
from openbb_federal_reserve.models.regional.st_louis_publications import (
    FederalReserveStLouisPublicationsFetcher,
)
from openbb_federal_reserve.models.sofr import FederalReserveSOFRFetcher
from openbb_federal_reserve.models.state_average import (
    FederalReserveStateAverageFetcher,
)
from openbb_federal_reserve.models.treasury_rates import (
    FederalReserveTreasuryRatesFetcher,
)
from openbb_federal_reserve.models.ubpr import (
    FederalReserveUBPRFetcher,
)
from openbb_federal_reserve.models.yield_curve import FederalReserveYieldCurveFetcher

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None
FIXEDINCOME_INSTALLED = find_spec("openbb_fixedincome") is not None


def _key(standard: str, alias: str, installed: bool) -> str:
    """Return the standard key when the host extension is installed, else the federal_reserve alias."""
    return standard if installed else alias


federal_reserve_provider = Provider(
    name="federal_reserve",
    website="https://www.federalreserve.gov/data.htm",  #  Not a typo, it's really .htm
    description="""Access data provided by the Federal Reserve System, the Central Bank of the United States.""",
    fetcher_dict={
        _key(
            "CentralBankHoldings",
            "FederalReserveCentralBankHoldings",
            ECONOMY_INSTALLED,
        ): FederalReserveCentralBankHoldingsFetcher,
        _key(
            "FomcDocuments", "FederalReserveFomcDocuments", ECONOMY_INSTALLED
        ): FederalReserveFomcDocumentsFetcher,
        _key(
            "InflationExpectations",
            "FederalReserveInflationExpectations",
            ECONOMY_INSTALLED,
        ): FederalReserveInflationExpectationsFetcher,
        _key(
            "MoneyMeasures", "FederalReserveMoneyMeasures", ECONOMY_INSTALLED
        ): FederalReserveMoneyMeasuresFetcher,
        _key(
            "PrimaryDealerFails",
            "FederalReservePrimaryDealerFails",
            ECONOMY_INSTALLED,
        ): FederalReservePrimaryDealerFailsFetcher,
        _key(
            "PrimaryDealerPositioning",
            "FederalReservePrimaryDealerPositioning",
            ECONOMY_INSTALLED,
        ): FederalReservePrimaryDealerPositioningFetcher,
        _key(
            "FederalFundsRate",
            "FederalReserveFederalFundsRate",
            FIXEDINCOME_INSTALLED,
        ): FederalReserveFederalFundsRateFetcher,
        _key(
            "OvernightBankFundingRate",
            "FederalReserveOvernightBankFundingRate",
            FIXEDINCOME_INSTALLED,
        ): FederalReserveOvernightBankFundingRateFetcher,
        _key(
            "SOFR", "FederalReserveSOFR", FIXEDINCOME_INSTALLED
        ): FederalReserveSOFRFetcher,
        _key(
            "TreasuryRates", "FederalReserveTreasuryRates", FIXEDINCOME_INSTALLED
        ): FederalReserveTreasuryRatesFetcher,
        _key(
            "YieldCurve", "FederalReserveYieldCurve", FIXEDINCOME_INSTALLED
        ): FederalReserveYieldCurveFetcher,
        "FederalReserveDataDownload": FederalReserveDataDownloadFetcher,
        "FederalReserveInstitutions": FederalReserveInstitutionsFetcher,
        "FederalReserveCallReport": FederalReserveCallReportFetcher,
        "FederalReserveCallReportSectioned": (FederalReserveCallReportSectionedFetcher),
        "FederalReserveUBPR": FederalReserveUBPRFetcher,
        "FederalReserveExecutiveSummary": FederalReserveExecutiveSummaryFetcher,
        "FederalReserveCustomPeerGroup": FederalReserveCustomPeerGroupFetcher,
        "FederalReservePeerGroupAverage": FederalReservePeerGroupAverageFetcher,
        "FederalReservePeerGroupBank": FederalReservePeerGroupBankFetcher,
        "FederalReservePeerGroupDistribution": (
            FederalReservePeerGroupDistributionFetcher
        ),
        "FederalReserveStateAverage": FederalReserveStateAverageFetcher,
        "FederalReserveListOfBanksPeerGroup": (
            FederalReserveListOfBanksPeerGroupFetcher
        ),
        "FederalReserveCountryExposure": FederalReserveCountryExposureFetcher,
        "FederalReserveInternationalPortfolioInvestment": (
            FederalReserveInternationalPortfolioInvestmentFetcher
        ),
        "FederalReserveMoneyMarketFunds": FederalReserveMoneyMarketFundsFetcher,
        "FederalReserveBhcpr": FederalReserveBhcprFetcher,
        "FederalReserveBhcprReport": FederalReserveBhcprReportFetcher,
        "FederalReserveFinancialReport": FederalReserveFinancialReportFetcher,
        "FederalReserveFinancialReportPdf": (FederalReserveFinancialReportPdfFetcher),
        "FederalReserveLargeHoldingCompanies": (
            FederalReserveLargeHoldingCompaniesFetcher
        ),
        "FederalReserveInstitutionStructure": FederalReserveInstitutionStructureFetcher,
        "FederalReserveChicagoNationalActivity": (
            FederalReserveChicagoNationalActivityFetcher
        ),
        "FederalReserveChicagoFinancialConditions": (
            FederalReserveChicagoFinancialConditionsFetcher
        ),
        "FederalReservePhiladelphiaAds": FederalReservePhiladelphiaAdsFetcher,
        "FederalReserveNewYorkSupplyChain": FederalReserveNewYorkSupplyChainFetcher,
        "FederalReserveNewYorkCorporateDistress": (
            FederalReserveNewYorkCorporateDistressFetcher
        ),
        "FederalReserveNewYorkConsumerExpectations": (
            FederalReserveNewYorkConsumerExpectationsFetcher
        ),
        "FederalReserveNewYorkBusinessLeaders": (
            FederalReserveNewYorkBusinessLeadersFetcher
        ),
        "FederalReserveNewYorkMarketExpectations": (
            FederalReserveNewYorkMarketExpectationsFetcher
        ),
        "FederalReserveNewYorkMarketExpectationsReports": (
            FederalReserveNewYorkMarketExpectationsReportsFetcher
        ),
        "FederalReserveNewYorkNowcast": FederalReserveNewYorkNowcastFetcher,
        "FederalReserveClevelandInflation": FederalReserveClevelandInflationFetcher,
        "FederalReserveClevelandInflationNowcast": (
            FederalReserveClevelandInflationNowcastFetcher
        ),
        "FederalReserveClevelandMedianCpi": FederalReserveClevelandMedianCpiFetcher,
        "FederalReserveClevelandMedianCpiComponents": (
            FederalReserveClevelandMedianCpiComponentsFetcher
        ),
        "FederalReserveClevelandSystemicRisk": (
            FederalReserveClevelandSystemicRiskFetcher
        ),
        "FederalReserveClevelandPublicationSeries": FederalReserveClevelandPublicationSeriesFetcher,
        "FederalReserveClevelandPublications": (
            FederalReserveClevelandPublicationsFetcher
        ),
        "FederalReserveDallasManufacturing": FederalReserveDallasManufacturingFetcher,
        "FederalReserveDallasServiceSector": FederalReserveDallasServiceSectorFetcher,
        "FederalReserveDallasRetail": FederalReserveDallasRetailFetcher,
        "FederalReserveDallasBanking": FederalReserveDallasBankingFetcher,
        "FederalReserveDallasEnergy": FederalReserveDallasEnergyFetcher,
        "FederalReserveDallasAgSurvey": FederalReserveDallasAgSurveyFetcher,
        "FederalReserveDallasBreakeven": FederalReserveDallasBreakevenFetcher,
        "FederalReserveDallasDgei": FederalReserveDallasDgeiFetcher,
        "FederalReserveDallasGigafactory": FederalReserveDallasGigafactoryFetcher,
        "FederalReserveDallasGovernmentDebt": (
            FederalReserveDallasGovernmentDebtFetcher
        ),
        "FederalReserveDallasIgrea": FederalReserveDallasIgreaFetcher,
        "FederalReserveDallasLithium": FederalReserveDallasLithiumFetcher,
        "FederalReserveDallasTrimmedMeanPCE": (
            FederalReserveDallasTrimmedMeanPCEFetcher
        ),
        "FederalReserveDallasWeeklyEconomic": (
            FederalReserveDallasWeeklyEconomicFetcher
        ),
        "FederalReserveDallasLeadingIndex": FederalReserveDallasLeadingIndexFetcher,
        "FederalReserveDallasPublicationSeries": FederalReserveDallasPublicationSeriesFetcher,
        "FederalReserveDallasPublications": FederalReserveDallasPublicationsFetcher,
        "FederalReserveMinneapolisBusinessConditions": (
            FederalReserveMinneapolisBusinessConditionsFetcher
        ),
        "FederalReserveMinneapolisEmployment": (
            FederalReserveMinneapolisEmploymentFetcher
        ),
        "FederalReserveMinneapolisUnemployment": (
            FederalReserveMinneapolisUnemploymentFetcher
        ),
        "FederalReserveMinneapolisLaborForce": (
            FederalReserveMinneapolisLaborForceFetcher
        ),
        "FederalReserveMinneapolisQuitsRate": FederalReserveMinneapolisQuitsRateFetcher,
        "FederalReserveMinneapolisGdp": FederalReserveMinneapolisGdpFetcher,
        "FederalReserveMinneapolisCpi": FederalReserveMinneapolisCpiFetcher,
        "FederalReserveMinneapolisClaims": FederalReserveMinneapolisClaimsFetcher,
        "FederalReserveMinneapolisPublicationSeries": FederalReserveMinneapolisPublicationSeriesFetcher,
        "FederalReserveMinneapolisPublications": (
            FederalReserveMinneapolisPublicationsFetcher
        ),
        "FederalReserveMinneapolisJobOpenings": (
            FederalReserveMinneapolisJobOpeningsFetcher
        ),
        "FederalReserveStLouisFredMd": FederalReserveStLouisFredMdFetcher,
        "FederalReserveStLouisFredQd": FederalReserveStLouisFredQdFetcher,
        "FederalReserveStLouisNationalIndex": (
            FederalReserveStLouisNationalIndexFetcher
        ),
        "FederalReserveStLouisPublicationSeries": (
            FederalReserveStLouisPublicationSeriesFetcher
        ),
        "FederalReserveStLouisPublications": (FederalReserveStLouisPublicationsFetcher),
        "FederalReserveAtlantaGdpNow": FederalReserveAtlantaGdpNowFetcher,
        "FederalReserveAtlantaWageGrowth": FederalReserveAtlantaWageGrowthFetcher,
        "FederalReserveAtlantaStickyCpi": FederalReserveAtlantaStickyCpiFetcher,
        "FederalReserveAtlantaBusinessInflation": (
            FederalReserveAtlantaBusinessInflationFetcher
        ),
        "FederalReserveAtlantaBusinessUncertainty": (
            FederalReserveAtlantaBusinessUncertaintyFetcher
        ),
        "FederalReserveAtlantaMarketProbability": (
            FederalReserveAtlantaMarketProbabilityFetcher
        ),
        "FederalReserveAtlantaTaylorRule": FederalReserveAtlantaTaylorRuleFetcher,
        "FederalReserveAtlantaTaylorRuleMeasures": (
            FederalReserveAtlantaTaylorRuleMeasuresFetcher
        ),
        "FederalReserveAtlantaTaylorRuleHeatmap": (
            FederalReserveAtlantaTaylorRuleHeatmapFetcher
        ),
        "FederalReserveAtlantaPublicationSeries": FederalReserveAtlantaPublicationSeriesFetcher,
        "FederalReserveAtlantaPublications": FederalReserveAtlantaPublicationsFetcher,
        "FederalReserveKansasCityFinancialStress": (
            FederalReserveKansasCityFinancialStressFetcher
        ),
        "FederalReserveKansasCityRiskIndex": FederalReserveKansasCityRiskIndexFetcher,
        "FederalReserveKansasCityAgCreditSurvey": (
            FederalReserveKansasCityAgCreditSurveyFetcher
        ),
        "FederalReserveKansasCityAgRates": FederalReserveKansasCityAgRatesFetcher,
        "FederalReserveKansasCityAgFinance": FederalReserveKansasCityAgFinanceFetcher,
        "FederalReserveKansasCityAgTermsOfLending": (
            FederalReserveKansasCityAgTermsOfLendingFetcher
        ),
        "FederalReserveKansasCityAgDistrictSurveys": (
            FederalReserveKansasCityAgDistrictSurveysFetcher
        ),
        "FederalReserveKansasCityAgDatabookArchived": (
            FederalReserveKansasCityAgDatabookArchivedFetcher
        ),
        "FederalReserveKansasCityPolicyRateUncertainty": (
            FederalReserveKansasCityPolicyRateUncertaintyFetcher
        ),
        "FederalReserveKansasCityNaturalRate": (
            FederalReserveKansasCityNaturalRateFetcher
        ),
        "FederalReserveKansasCityDivisionalLmci": (
            FederalReserveKansasCityDivisionalLmciFetcher
        ),
        "FederalReserveKansasCityPublicationSeries": FederalReserveKansasCityPublicationSeriesFetcher,
        "FederalReserveKansasCityPublications": (
            FederalReserveKansasCityPublicationsFetcher
        ),
        "FederalReserveRichmondManufacturing": (
            FederalReserveRichmondManufacturingFetcher
        ),
        "FederalReserveRichmondServiceSector": (
            FederalReserveRichmondServiceSectorFetcher
        ),
        "FederalReserveRichmondStateSurvey": FederalReserveRichmondStateSurveyFetcher,
        "FederalReserveRichmondCFO": FederalReserveRichmondCFOFetcher,
        "FederalReserveRichmondNonEmployment": (
            FederalReserveRichmondNonEmploymentFetcher
        ),
        "FederalReserveRichmondRecessionIndicator": (
            FederalReserveRichmondRecessionIndicatorFetcher
        ),
        "FederalReserveRichmondPublicationSeries": FederalReserveRichmondPublicationSeriesFetcher,
        "FederalReserveRichmondPublications": FederalReserveRichmondPublicationsFetcher,
        "FederalReserveChicagoEconomicConditions": (
            FederalReserveChicagoEconomicConditionsFetcher
        ),
        "FederalReserveChicagoRetailTrade": FederalReserveChicagoRetailTradeFetcher,
        "FederalReserveChicagoLaborMarket": FederalReserveChicagoLaborMarketFetcher,
        "FederalReserveChicagoFarmlandValues": (
            FederalReserveChicagoFarmlandValuesFetcher
        ),
        "FederalReserveChicagoAgCredit": FederalReserveChicagoAgCreditFetcher,
        "FederalReserveChicagoFarmLoanRates": FederalReserveChicagoFarmLoanRatesFetcher,
        "FederalReserveChicagoBraveButtersKelley": (
            FederalReserveChicagoBraveButtersKelleyFetcher
        ),
        "FederalReserveChicagoMidwestEconomy": (
            FederalReserveChicagoMidwestEconomyFetcher
        ),
        "FederalReserveChicagoPublicationSeries": FederalReserveChicagoPublicationSeriesFetcher,
        "FederalReserveChicagoPublications": FederalReserveChicagoPublicationsFetcher,
        "FederalReservePhiladelphiaSpf": FederalReservePhiladelphiaSpfFetcher,
        "FederalReservePhiladelphiaAnxious": FederalReservePhiladelphiaAnxiousFetcher,
        "FederalReservePhiladelphiaGdpPlus": FederalReservePhiladelphiaGdpPlusFetcher,
        "FederalReservePhiladelphiaPartisan": FederalReservePhiladelphiaPartisanFetcher,
        "FederalReservePhiladelphiaCoincident": (
            FederalReservePhiladelphiaCoincidentFetcher
        ),
        "FederalReservePhiladelphiaLivingston": (
            FederalReservePhiladelphiaLivingstonFetcher
        ),
        "FederalReservePhiladelphiaManufacturing": (
            FederalReservePhiladelphiaManufacturingFetcher
        ),
        "FederalReservePhiladelphiaNonmanufacturing": (
            FederalReservePhiladelphiaNonmanufacturingFetcher
        ),
        "FederalReservePhiladelphiaAtsix": FederalReservePhiladelphiaAtsixFetcher,
        "FederalReservePhiladelphiaPublicationSeries": FederalReservePhiladelphiaPublicationSeriesFetcher,
        "FederalReservePhiladelphiaPublications": (
            FederalReservePhiladelphiaPublicationsFetcher
        ),
        "FederalReserveNewYorkEmpireState": FederalReserveNewYorkEmpireStateFetcher,
        "FederalReserveNewYorkEmpireReports": (
            FederalReserveNewYorkEmpireReportsFetcher
        ),
        "FederalReserveNewYorkConsumerLaborMarket": (
            FederalReserveNewYorkConsumerLaborMarketFetcher
        ),
        "FederalReserveNewYorkConsumerHousing": (
            FederalReserveNewYorkConsumerHousingFetcher
        ),
        "FederalReserveNewYorkConsumerCreditAccess": (
            FederalReserveNewYorkConsumerCreditAccessFetcher
        ),
        "FederalReserveNewYorkHouseholdDebt": FederalReserveNewYorkHouseholdDebtFetcher,
        "FederalReserveNewYorkCoreTrendInflation": (
            FederalReserveNewYorkCoreTrendInflationFetcher
        ),
        "FederalReserveNewYorkPublicationSeries": FederalReserveNewYorkPublicationSeriesFetcher,
        "FederalReserveNewYorkPublications": (FederalReserveNewYorkPublicationsFetcher),
        "FederalReserveBostonEconomicIndicators": (
            FederalReserveBostonEconomicIndicatorsFetcher
        ),
        "FederalReserveBostonPublicationSeries": FederalReserveBostonPublicationSeriesFetcher,
        "FederalReserveBostonPublications": FederalReserveBostonPublicationsFetcher,
        "FederalReserveSanFranciscoNewsSentiment": (
            FederalReserveSanFranciscoNewsSentimentFetcher
        ),
        "FederalReserveSanFranciscoProxyFundsRate": (
            FederalReserveSanFranciscoProxyFundsRateFetcher
        ),
        "FederalReserveSanFranciscoCyclicalPce": (
            FederalReserveSanFranciscoCyclicalPceFetcher
        ),
        "FederalReserveSanFranciscoSupplyDemandPce": (
            FederalReserveSanFranciscoSupplyDemandPceFetcher
        ),
        "FederalReserveSanFranciscoTfp": FederalReserveSanFranciscoTfpFetcher,
        "FederalReserveSanFranciscoShortRatePath": (
            FederalReserveSanFranciscoShortRatePathFetcher
        ),
        "FederalReserveSanFranciscoTermPremium": (
            FederalReserveSanFranciscoTermPremiumFetcher
        ),
        "FederalReserveSanFranciscoPublicationSeries": FederalReserveSanFranciscoPublicationSeriesFetcher,
        "FederalReserveSanFranciscoPublications": (
            FederalReserveSanFranciscoPublicationsFetcher
        ),
    },
    repr_name="Federal Reserve (FED)",
)
