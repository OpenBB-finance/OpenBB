"""Ultima provider module."""

import warnings
from typing import Union

from openbb_core.provider.abstract.provider import Provider

ultima_provider: Union[Provider, None] = None

try:
    from openbb_ultima.models.company_news import UltimaCompanyNewsFetcher
    from openbb_ultima.models.sector_news import UltimaSectorNewsFetcher

    ultima_provider = Provider(
        name="ultima",
        website="https://www.ultimainsights.ai/openbb",
        description="""Ultima harnesses the power of LLMs to deliver news before it hits the frontpage of Bloomberg.""",
        credentials=["api_key"],
        fetcher_dict={
            "CompanyNews": UltimaCompanyNewsFetcher,
            "SectorNews": UltimaSectorNewsFetcher,
        },
    )
except ImportError:
    warnings.warn(
        "openbb-ultima is not installed. Please install openbb-ultima to use the Ultima provider."
    )
