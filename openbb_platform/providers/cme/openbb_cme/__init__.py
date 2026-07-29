"""OpenBB CME Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_cme.models.contract_specs import CMEContractSpecsFetcher
from openbb_cme.models.futures_curve import CMEFuturesCurveFetcher
from openbb_cme.models.futures_historical import CMEFuturesHistoricalFetcher
from openbb_cme.models.futures_info import CMEFuturesInfoFetcher
from openbb_cme.models.futures_instruments import CMEFuturesInstrumentsFetcher
from openbb_cme.models.options_chains import CMEOptionsChainsFetcher
from openbb_cme.models.products import CMEProductsFetcher

DERIVATIVES_INSTALLED = find_spec("openbb_derivatives") is not None


def _key(standard: str, cme_alias: str) -> str:
    """Return the standard key when derivatives is installed, else the CME alias."""
    return standard if DERIVATIVES_INSTALLED else cme_alias


cme_provider = Provider(
    name="cme",
    website="https://www.cmegroup.com/",
    description=(
        "CME Group provider for futures and options-on-futures reference and "
        "settlement data across the exchange's asset classes. Product metadata and "
        "contract specifications are generated from CME's public product slate."
    ),
    credentials=None,
    fetcher_dict={
        "CmeProducts": CMEProductsFetcher,
        "CmeContractSpecs": CMEContractSpecsFetcher,
        _key("OptionsChains", "CmeOptionsChains"): CMEOptionsChainsFetcher,
        _key("FuturesCurve", "CmeFuturesCurve"): CMEFuturesCurveFetcher,
        _key("FuturesHistorical", "CmeFuturesHistorical"): (
            CMEFuturesHistoricalFetcher
        ),
        _key("FuturesInfo", "CmeFuturesInfo"): CMEFuturesInfoFetcher,
        _key("FuturesInstruments", "CmeFuturesInstruments"): (
            CMEFuturesInstrumentsFetcher
        ),
    },
    repr_name="CME Group Public Derivatives Data",
    instructions=(
        "This provider uses CME Group's public product-slate, contract-specification,"
        " calendar, and settlement endpoints. No credentials are required."
        " Settlement data is published after the trading session."
    ),
)
