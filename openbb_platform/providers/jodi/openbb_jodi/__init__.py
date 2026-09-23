"""OpenBB JODI Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_jodi.models.gas_balance import JodiGasBalanceFetcher
from openbb_jodi.models.gas_demand import JodiGasDemandFetcher
from openbb_jodi.models.gas_exports import JodiGasExportsFetcher
from openbb_jodi.models.gas_imports import JodiGasImportsFetcher
from openbb_jodi.models.gas_production import JodiGasProductionFetcher
from openbb_jodi.models.gas_stocks import JodiGasStocksFetcher
from openbb_jodi.models.oil_balance import JodiOilBalanceFetcher
from openbb_jodi.models.oil_demand import JodiOilDemandFetcher
from openbb_jodi.models.oil_demand_by_product import JodiOilDemandByProductFetcher
from openbb_jodi.models.oil_exports import JodiOilExportsFetcher
from openbb_jodi.models.oil_imports import JodiOilImportsFetcher
from openbb_jodi.models.oil_production import JodiOilProductionFetcher
from openbb_jodi.models.oil_stocks import JodiOilStocksFetcher

jodi_provider = Provider(
    name="jodi",
    website="https://www.jodidata.org",
    description="The Joint Organisations Data Initiative (JODI) provides free monthly"
    + " petroleum and natural gas supply, demand, and stock statistics,"
    + " self-reported by over 100 countries, through the JODI-Oil and JODI-Gas"
    + " World Databases.",
    fetcher_dict={
        "JodiGasBalance": JodiGasBalanceFetcher,
        "JodiGasDemand": JodiGasDemandFetcher,
        "JodiGasExports": JodiGasExportsFetcher,
        "JodiGasImports": JodiGasImportsFetcher,
        "JodiGasProduction": JodiGasProductionFetcher,
        "JodiGasStocks": JodiGasStocksFetcher,
        "JodiOilBalance": JodiOilBalanceFetcher,
        "JodiOilDemand": JodiOilDemandFetcher,
        "JodiOilDemandByProduct": JodiOilDemandByProductFetcher,
        "JodiOilExports": JodiOilExportsFetcher,
        "JodiOilImports": JodiOilImportsFetcher,
        "JodiOilProduction": JodiOilProductionFetcher,
        "JodiOilStocks": JodiOilStocksFetcher,
    },
    repr_name="Joint Organisations Data Initiative (JODI) World Databases",
)
