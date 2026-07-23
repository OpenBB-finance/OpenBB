"""OpenBB CME Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_cme.models.futures_curve import CMEFuturesCurveFetcher
from openbb_cme.models.futures_historical import CMEFuturesHistoricalFetcher
from openbb_cme.models.futures_info import CMEFuturesInfoFetcher
from openbb_cme.models.futures_instruments import CMEFuturesInstrumentsFetcher

DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None


def _key(standard: str, cme_alias: str) -> str:
    """Return the standard key when derivatives is installed, else the CME alias."""
    return standard if DERIVATIVES_INSTALLED else cme_alias


cme_provider = Provider(
    name="cme",
    website="https://www.cmegroup.com/",
    description=(
        "CME Group provider for equity index futures settlement data. "
        "Provides daily settlement prices, term structure, contract specifications, "
        "and listed instruments for ES, NQ, MES, MNQ, and YM futures. "
        "Uses publicly available CME settlement APIs — no API key required."
    ),
    credentials=None,
    fetcher_dict={
        _key("FuturesCurve", "CmeFuturesCurve"): CMEFuturesCurveFetcher,
        _key("FuturesHistorical", "CmeFuturesHistorical"): (
            CMEFuturesHistoricalFetcher
        ),
        _key("FuturesInfo", "CmeFuturesInfo"): CMEFuturesInfoFetcher,
        _key("FuturesInstruments", "CmeFuturesInstruments"): (
            CMEFuturesInstrumentsFetcher
        ),
    },
    repr_name="CME Group Public Settlement Data",
    instructions=(
        "This provider uses CME Group's public settlement data endpoints."
        " No credentials are required."
        " Data is published after the trading session."
    ),
)
