"""OpenBB CME Provider Module."""

from openbb_cme.models.futures_curve import CMEFuturesCurveFetcher
from openbb_cme.models.futures_historical import CMEFuturesHistoricalFetcher
from openbb_cme.models.futures_info import CMEFuturesInfoFetcher
from openbb_cme.models.futures_instruments import CMEFuturesInstrumentsFetcher
from openbb_core.provider.abstract.provider import Provider

cme_provider = Provider(
    name="cme",
    website="https://www.cmegroup.com/",
    description=(
        "CME Group provider for equity index futures settlement data. "
        "Provides daily settlement prices, term structure, contract specifications, "
        "and listed instruments for ES, NQ, MES, MNQ, RTY, and YM futures. "
        "Uses publicly available CME settlement APIs — no API key required."
    ),
    credentials=None,
    fetcher_dict={
        "FuturesCurve": CMEFuturesCurveFetcher,
        "FuturesHistorical": CMEFuturesHistoricalFetcher,
        "FuturesInfo": CMEFuturesInfoFetcher,
        "FuturesInstruments": CMEFuturesInstrumentsFetcher,
    },
    repr_name="CME Group Public Settlement Data",
    instructions=(
        "This provider uses CME Group's public settlement data endpoints."
        " No credentials are required."
        " Data is delayed (T+1 for settlements)."
    ),
)
