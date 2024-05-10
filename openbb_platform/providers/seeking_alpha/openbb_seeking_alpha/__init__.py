"""Seeking Alpha Provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_seeking_alpha.models.upcoming_release_days import (
    SAUpcomingReleaseDaysFetcher,
)

seeking_alpha_provider = Provider(
    name="seeking_alpha",
    website="https://seekingalpha.com",
    description="""Seeking Alpha is a data provider with access to news, analysis, and
real-time alerts on stocks.""",
    fetcher_dict={
        "UpcomingReleaseDays": SAUpcomingReleaseDaysFetcher,
    },
    repr_name="Seeking Alpha",
    logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Seeking_Alpha_Logo.svg/280px-Seeking_Alpha_Logo.svg.png",
)
