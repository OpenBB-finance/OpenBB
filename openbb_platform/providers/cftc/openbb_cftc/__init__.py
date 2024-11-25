"""CFTC provider extension module."""

from openbb_cftc.models.cot import CftcCotFetcher
from openbb_cftc.models.cot_search import CftcCotSearchFetcher
from openbb_core.provider.abstract.provider import Provider

cftc_provider = Provider(
    name="cftc",
    website="https://cftc.gov/",
    description="""The mission of the Commodity Futures Trading Commission (CFTC) is to promote the integrity,
    resilience, and vibrancy of the U.S. derivatives markets through sound regulation.""",
    credentials=["app_token"],  # This is optional
    fetcher_dict={
        "COT": CftcCotFetcher,
        "COTSearch": CftcCotSearchFetcher,
    },
    repr_name="Commodity Futures Trading Commission (CFTC) Public Reporting API",
    instructions="""Credentials are not required, but your IP address may be subject to throttling limits.
    API requests made using an application token are not throttled.
    Create an account here: https://evergreen.data.socrata.com/signup
    and then generate the app_token by signing in with the credentials
    here: https://publicreporting.cftc.gov/profile/edit/developer_settings.""",
)
