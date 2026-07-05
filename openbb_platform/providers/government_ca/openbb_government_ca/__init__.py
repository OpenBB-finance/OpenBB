"""Canadian government data provider module (Bank of Canada + Statistics Canada)."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_government_ca.boc.fx import BankOfCanadaFXFetcher
from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher
from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher
from openbb_government_ca.statscan.available_indicators import (
    StatsCanAvailableIndicatorsFetcher,
)
from openbb_government_ca.statscan.economic_indicators import (
    StatsCanEconomicIndicatorsFetcher,
)

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None


def _key(standard: str, local_alias: str) -> str:
    """Return the standard key when ``openbb-economy`` is installed, else the local alias."""
    return standard if ECONOMY_INSTALLED else local_alias


government_ca_provider = Provider(
    name="government_ca",
    website="https://www.bankofcanada.ca/valet/",
    description="""Access Canadian public-sector data via the Bank of
Canada Valet API and Statistics Canada SDMX REST API.

Covers FX rates (FX_RATES_DAILY), the Bank of Canada policy overnight
rate (V39079 / CBC20210), benchmark bond yields (BD.CDN.ALL...), and
Statistics Canada key economic indicators.""",
    fetcher_dict={
        _key("CurrencyHistorical", "BankOfCanadaFX"): BankOfCanadaFXFetcher,
        _key("CountryInterestRates", "BankOfCanadaRates"): (BankOfCanadaRatesFetcher),
        _key("TreasuryRates", "BankOfCanadaYields"): BankOfCanadaYieldsFetcher,
        _key("EconomicIndicators", "StatsCanEconomicIndicators"): (
            StatsCanEconomicIndicatorsFetcher
        ),
        _key("AvailableIndicators", "StatsCanAvailableIndicators"): (
            StatsCanAvailableIndicatorsFetcher
        ),
    },
    repr_name="Canadian Government Data (Bank of Canada + Statistics Canada)",
)
