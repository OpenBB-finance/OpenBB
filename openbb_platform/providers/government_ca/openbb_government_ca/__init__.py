"""Canadian government data provider module (Bank of Canada + Statistics Canada).

This module exposes a single OpenBB ``Provider`` that registers
fetchers for both Canadian data sources. Routing is split into two
sub-routers exposed under ``obb.boc`` and ``obb.statscan`` — see
``government_ca_router.py`` for the wiring.
"""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

# The fetchers are imported lazily-as-module-level so that
# ``openbb_provider_extension`` entry-point resolution always succeeds
# even when an upstream standard-model package is missing. The
# ``_key`` helper mirrors the pattern introduced by ``openbb-oecd``
# (PR #7413): when ``openbb-economy`` (or whichever core extension owns
# the standard model) is installed, we register the fetcher under its
# standard key; otherwise we fall back to a provider-local alias so
# the data is still reachable.
# BoC fetchers — Phase 5.
from openbb_government_ca.boc.fx import BankOfCanadaFXFetcher
from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher
from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

# StatsCan fetchers — Phase 4.
from openbb_government_ca.statscan.economic_indicators import (
    StatsCanEconomicIndicatorsFetcher,
)

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None


def _key(standard: str, local_alias: str) -> str:
    """Return the standard key when ``openbb-economy`` is installed, else the local alias.

    This lets the extension ship standalone (with provider-local model
    names) or integrated into the wider OpenBB economy namespace (with
    standard model names like ``CurrencyHistorical``,
    ``CountryInterestRates``, ``TreasuryRates``).
    """
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
        # ---- Phase 5 — BoC fetchers ----
        # Each is registered under either the standard key (when
        # ``openbb-economy`` is installed) or a provider-local alias
        # (standalone mode).
        _key("CurrencyHistorical", "BankOfCanadaFX"): BankOfCanadaFXFetcher,
        _key("CountryInterestRates", "BankOfCanadaRates"): (BankOfCanadaRatesFetcher),
        _key("TreasuryRates", "BankOfCanadaYields"): BankOfCanadaYieldsFetcher,
        # ---- Phase 4 — StatsCan fetchers ----
        _key("EconomicIndicators", "StatsCanEconomicIndicators"): (
            StatsCanEconomicIndicatorsFetcher
        ),
    },
    repr_name="Canadian Government Data (Bank of Canada + Statistics Canada)",
)
