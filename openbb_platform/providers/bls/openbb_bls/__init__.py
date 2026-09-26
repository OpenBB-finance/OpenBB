"""BLS Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_bls.models.ces_analytical_tables import (
    BlsCesConfidenceIntervalsFetcher,
    BlsCesTable1Fetcher,
    BlsCesTable2Fetcher,
    BlsCesTable3AFetcher,
    BlsCesTable3BFetcher,
    BlsCesTable4Fetcher,
    BlsCesTable5Fetcher,
    BlsCesTable6Fetcher,
    BlsCesTable7Fetcher,
)
from openbb_bls.models.cpi_charts import CPI_CHART_FETCHERS
from openbb_bls.models.cpi_documents import BlsCpiDocumentsFetcher
from openbb_bls.models.cpi_news_release import (
    BlsCpiNrTable1Fetcher,
    BlsCpiNrTable2Fetcher,
    BlsCpiNrTable3Fetcher,
    BlsCpiNrTable4Fetcher,
    BlsCpiNrTable5Fetcher,
    BlsCpiNrTable6Fetcher,
    BlsCpiNrTable7Fetcher,
)
from openbb_bls.models.cpi_relative_importance import (
    BlsCpiRelativeImportanceFetcher,
)
from openbb_bls.models.cpi_seasonal_factors import BlsCpiSeasonalFactorsFetcher
from openbb_bls.models.cpi_supplemental_tables import (
    BlsCpiSupplementalTablesFetcher,
)
from openbb_bls.models.economic_calendar import BlsEconomicCalendarFetcher
from openbb_bls.models.empsit_charts import EMPSIT_CHART_FETCHERS
from openbb_bls.models.empsit_documents import BlsEmpsitDocumentsFetcher
from openbb_bls.models.empsit_summary import EMPSIT_SUMMARY_FETCHERS
from openbb_bls.models.jolts_charts import JOLTS_CHART_FETCHERS
from openbb_bls.models.jolts_documents import BlsJoltsDocumentsFetcher
from openbb_bls.models.jolts_revisions import BlsJoltsRevisionsFetcher
from openbb_bls.models.jolts_tables import BlsJoltsChangeAnalysisFetcher
from openbb_bls.models.mining_manufacturing_charts import (
    MINING_MANUFACTURING_CHART_FETCHERS,
)
from openbb_bls.models.ppi_charts import PPI_CHART_FETCHERS
from openbb_bls.models.ppi_detailed_report import BlsPpiDetailedReportFetcher
from openbb_bls.models.ppi_documents import BlsPpiDocumentsFetcher
from openbb_bls.models.ppi_relative_importance import BlsPpiRelativeImportanceFetcher
from openbb_bls.models.ppi_seasonal_factors import BlsPpiSeasonalFactorsFetcher
from openbb_bls.models.productivity_charts import PRODUCTIVITY_CHART_FETCHERS
from openbb_bls.models.productivity_documents import BlsProductivityDocumentsFetcher
from openbb_bls.models.productivity_tables import BlsProductivityTablesFetcher
from openbb_bls.models.realer_documents import BlsRealerDocumentsFetcher
from openbb_bls.models.search import BlsSearchFetcher
from openbb_bls.models.series import BlsSeriesFetcher
from openbb_bls.models.tfp_charts import TFP_CHART_FETCHERS
from openbb_bls.models.wholesale_retail_charts import WHOLESALE_RETAIL_CHART_FETCHERS
from openbb_bls.models.ximpim_charts import (
    BlsXimpimAirFaresFetcher,
    BlsXimpimExportsByCategoryFetcher,
    BlsXimpimExportsByGrainsFetcher,
    BlsXimpimImportExportFetcher,
    BlsXimpimImportsByCategoryFetcher,
    BlsXimpimImportsByOriginFetcher,
)
from openbb_bls.models.ximpim_documents import BlsXimpimDocumentsFetcher

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None

_calendar_key = "EconomicCalendar" if ECONOMY_INSTALLED else "BlsEconomicCalendar"

bls_provider = Provider(
    name="bls",
    website="https://www.bls.gov/developers/api_signature_v2.htm",
    description="The Bureau of Labor Statistics' (BLS) Public Data Application Programming Interface (API)"
    + " gives the public access to economic data from all BLS programs."
    + " It is the Bureau's hope that talented developers and programmers will use the BLS Public Data API to create"
    + " original, inventive applications with published BLS data.",
    credentials=["api_key"],
    fetcher_dict={
        "BlsCpiDocuments": BlsCpiDocumentsFetcher,
        "BlsEmpsitDocuments": BlsEmpsitDocumentsFetcher,
        "BlsCesTable1": BlsCesTable1Fetcher,
        "BlsCesTable2": BlsCesTable2Fetcher,
        "BlsCesTable3A": BlsCesTable3AFetcher,
        "BlsCesTable3B": BlsCesTable3BFetcher,
        "BlsCesTable4": BlsCesTable4Fetcher,
        "BlsCesTable5": BlsCesTable5Fetcher,
        "BlsCesTable6": BlsCesTable6Fetcher,
        "BlsCesTable7": BlsCesTable7Fetcher,
        "BlsCesConfidenceIntervals": BlsCesConfidenceIntervalsFetcher,
        **EMPSIT_SUMMARY_FETCHERS,
        **EMPSIT_CHART_FETCHERS,
        "BlsCpiNrTable1": BlsCpiNrTable1Fetcher,
        "BlsCpiNrTable2": BlsCpiNrTable2Fetcher,
        "BlsCpiNrTable3": BlsCpiNrTable3Fetcher,
        "BlsCpiNrTable4": BlsCpiNrTable4Fetcher,
        "BlsCpiNrTable5": BlsCpiNrTable5Fetcher,
        "BlsCpiNrTable6": BlsCpiNrTable6Fetcher,
        "BlsCpiNrTable7": BlsCpiNrTable7Fetcher,
        "BlsCpiRelativeImportance": BlsCpiRelativeImportanceFetcher,
        "BlsCpiSeasonalFactors": BlsCpiSeasonalFactorsFetcher,
        "BlsCpiSupplementalTables": BlsCpiSupplementalTablesFetcher,
        **CPI_CHART_FETCHERS,
        "BlsJoltsChangeAnalysis": BlsJoltsChangeAnalysisFetcher,
        "BlsJoltsDocuments": BlsJoltsDocumentsFetcher,
        "BlsJoltsRevisions": BlsJoltsRevisionsFetcher,
        **JOLTS_CHART_FETCHERS,
        "BlsPpiDetailedReport": BlsPpiDetailedReportFetcher,
        "BlsPpiDocuments": BlsPpiDocumentsFetcher,
        "BlsPpiRelativeImportance": BlsPpiRelativeImportanceFetcher,
        "BlsPpiSeasonalFactors": BlsPpiSeasonalFactorsFetcher,
        **PPI_CHART_FETCHERS,
        "BlsProductivityDocuments": BlsProductivityDocumentsFetcher,
        "BlsProductivityTables": BlsProductivityTablesFetcher,
        **PRODUCTIVITY_CHART_FETCHERS,
        **TFP_CHART_FETCHERS,
        **WHOLESALE_RETAIL_CHART_FETCHERS,
        **MINING_MANUFACTURING_CHART_FETCHERS,
        "BlsRealerDocuments": BlsRealerDocumentsFetcher,
        "BlsSearch": BlsSearchFetcher,
        "BlsSeries": BlsSeriesFetcher,
        "BlsXimpimImportExport": BlsXimpimImportExportFetcher,
        "BlsXimpimImportsByCategory": BlsXimpimImportsByCategoryFetcher,
        "BlsXimpimExportsByCategory": BlsXimpimExportsByCategoryFetcher,
        "BlsXimpimImportsByOrigin": BlsXimpimImportsByOriginFetcher,
        "BlsXimpimExportsByGrains": BlsXimpimExportsByGrainsFetcher,
        "BlsXimpimAirFares": BlsXimpimAirFaresFetcher,
        "BlsXimpimDocuments": BlsXimpimDocumentsFetcher,
        _calendar_key: BlsEconomicCalendarFetcher,
    },
    repr_name="Bureau of Labor Statistics' (BLS) Public Data API",
    instructions="Sign up for a free API key here: https://data.bls.gov/registrationEngine/",
)
