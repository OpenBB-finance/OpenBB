"""SEC provider module."""
from openbb_provider.abstract.provider import Provider
from openbb_sec.models.cik_map import SecCikMapFetcher
from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
from openbb_sec.models.institutions_search import SecInstitutionsSearchFetcher
from openbb_sec.models.schema_files import SecSchemaFilesFetcher
from openbb_sec.models.stock_ftd import SecStockFtdFetcher
from openbb_sec.models.stock_search import SecStockSearchFetcher
from openbb_sec.models.symbol_map import SecSymbolMapFetcher

sec_provider = Provider(
    name="sec",
    website="https://sec.gov",
    description="SEC is the public listings regulatory body for the United States.",
    required_credentials=None,
    fetcher_dict={
        "CikMap": SecCikMapFetcher,
        "CompanyFilings": SecCompanyFilingsFetcher,
        "Filings": SecCompanyFilingsFetcher,
        "InstitutionsSearch": SecInstitutionsSearchFetcher,
        "SchemaFiles": SecSchemaFilesFetcher,
        "StockFTD": SecStockFtdFetcher,
        "StockSearch": SecStockSearchFetcher,
        "SymbolMap": SecSymbolMapFetcher,
    },
)
