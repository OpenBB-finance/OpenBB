"""OpenBB FINRA Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_finra.models.bond_historical import FinraBondHistoricalFetcher
from openbb_finra.models.bond_list import FinraBondListFetcher
from openbb_finra.models.bond_prices import FinraBondPricesFetcher
from openbb_finra.models.equity_info import FinraEquityInfoFetcher
from openbb_finra.models.equity_list import FinraEquityListFetcher
from openbb_finra.models.equity_search import FinraEquitySearchFetcher
from openbb_finra.models.equity_short_interest import FinraShortInterestFetcher
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher

EQUITY_INSTALLED = find_spec("openbb_equity") is not None
FIXEDINCOME_INSTALLED = find_spec("openbb_fixedincome") is not None


def _key(standard: str, alias: str, installed: bool) -> str:
    """Return the standard key when the extension owning it is installed, else the alias."""
    return standard if installed else alias


_fetcher_dict: dict = {
    _key("EquityInfo", "FinraEquityInfo", EQUITY_INSTALLED): FinraEquityInfoFetcher,
    _key("EquitySearch", "FinraEquitySearch", EQUITY_INSTALLED): (
        FinraEquitySearchFetcher
    ),
    _key("EquityShortInterest", "FinraEquityShortInterest", EQUITY_INSTALLED): (
        FinraShortInterestFetcher
    ),
    _key("OTCAggregate", "FinraOTCAggregate", EQUITY_INSTALLED): (
        FinraOTCAggregateFetcher
    ),
    _key("BondPrices", "FinraBondPrices", FIXEDINCOME_INSTALLED): (
        FinraBondPricesFetcher
    ),
    "FinraBondHistorical": FinraBondHistoricalFetcher,
    "FinraBondList": FinraBondListFetcher,
    "FinraEquityList": FinraEquityListFetcher,
}

finra_provider = Provider(
    name="finra",
    website="https://www.finra.org/finra-data",
    description="""FINRA Data provides centralized access to the abundance of data FINRA
makes available to the public, media, researchers and member firms.""",
    credentials=None,
    fetcher_dict=_fetcher_dict,
    repr_name="Financial Industry Regulatory Authority (FINRA)",
    instructions="This provider needs no credentials.",
)
