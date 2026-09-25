"""CFTC provider extension module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_cftc.models.cds_index_trades import CftcCdsIndexTradesFetcher
from openbb_cftc.models.cot import CftcCotFetcher
from openbb_cftc.models.cot_index import CftcCotIndexFetcher
from openbb_cftc.models.cot_movers import CftcCotMoversFetcher
from openbb_cftc.models.cot_positioning import CftcCotPositioningFetcher
from openbb_cftc.models.cot_search import CftcCotSearchFetcher
from openbb_cftc.models.fx_forward_curve import CftcFxForwardCurveFetcher
from openbb_cftc.models.fx_forward_points import CftcFxForwardPointsFetcher
from openbb_cftc.models.fx_forward_trades import CftcFxForwardTradesFetcher
from openbb_cftc.models.fx_implied_vol import CftcFxImpliedVolFetcher
from openbb_cftc.models.fx_option_trades import CftcFxOptionTradesFetcher
from openbb_cftc.models.historical_fixings import CftcHistoricalFixingsFetcher
from openbb_cftc.models.ois_curve import CftcOisCurveFetcher
from openbb_cftc.models.ois_curve_history import CftcOisCurveHistoryFetcher
from openbb_cftc.models.ois_forward_curve import CftcOisForwardCurveFetcher
from openbb_cftc.models.ois_policy_path import CftcOisPolicyPathFetcher
from openbb_cftc.models.swap_summary import CftcSwapSummaryFetcher
from openbb_cftc.models.swap_trades import CftcSwapTradesFetcher
from openbb_cftc.models.swap_valuation import CftcSwapValuationFetcher

cftc_provider = Provider(
    name="cftc",
    website="https://cftc.gov/",
    description="""The mission of the Commodity Futures Trading Commission (CFTC) is to promote the integrity,
    resilience, and vibrancy of the U.S. derivatives markets through sound regulation.
    Commitment of Traders reports are sourced from the CFTC Public Reporting API. Swap transaction
    and pricing data is sourced from the DTCC Public Price Dissemination service, the swap data
    repository that publishes CFTC-jurisdiction transactions. Overnight index swap curves and FX
    forward points are constructed from those executed transactions.""",
    credentials=["app_token"],
    fetcher_dict={
        "CftcCdsIndexTrades": CftcCdsIndexTradesFetcher,
        "CftcCot": CftcCotFetcher,
        "CftcCotIndex": CftcCotIndexFetcher,
        "CftcCotMovers": CftcCotMoversFetcher,
        "CftcCotPositioning": CftcCotPositioningFetcher,
        "CftcCotSearch": CftcCotSearchFetcher,
        "CftcFxForwardCurve": CftcFxForwardCurveFetcher,
        "CftcFxForwardPoints": CftcFxForwardPointsFetcher,
        "CftcFxForwardTrades": CftcFxForwardTradesFetcher,
        "CftcFxImpliedVol": CftcFxImpliedVolFetcher,
        "CftcFxOptionTrades": CftcFxOptionTradesFetcher,
        "CftcHistoricalFixings": CftcHistoricalFixingsFetcher,
        "CftcOisCurve": CftcOisCurveFetcher,
        "CftcOisCurveHistory": CftcOisCurveHistoryFetcher,
        "CftcOisForwardCurve": CftcOisForwardCurveFetcher,
        "CftcOisPolicyPath": CftcOisPolicyPathFetcher,
        "CftcSwapSummary": CftcSwapSummaryFetcher,
        "CftcSwapTrades": CftcSwapTradesFetcher,
        "CftcSwapValuation": CftcSwapValuationFetcher,
    },
    repr_name="Commodity Futures Trading Commission (CFTC)",
    instructions="""Credentials are not required, but your IP address may be subject to throttling limits
    on the Commitment of Traders endpoints. API requests made using an application token are not throttled.
    Create an account here: https://evergreen.data.socrata.com/signup
    and then generate the app_token by signing in with the credentials
    here: https://publicreporting.cftc.gov/profile/edit/developer_settings.
    The DTCC Public Price Dissemination endpoints are public and require no credentials.""",
)
