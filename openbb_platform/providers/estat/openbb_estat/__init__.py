"""e-Stat Provider Module.

ATTRIBUTION: This service uses API functions from e-Stat,
however its contents are not guaranteed by government.
"""

from openbb_core.provider.abstract.provider import Provider

from openbb_estat.models.statistical_data import EstatStatisticalDataFetcher

estat_provider = Provider(
    name="estat",
    website="https://www.e-stat.go.jp/api/",
    description="The e-Stat API provides access to Japanese government statistical data"
    + " from various ministries and agencies including economic, demographic, and social statistics."
    + " Attribution: This service uses API functions from e-Stat, however its contents are not guaranteed by government.",
    credentials=["estat_api_key"],
    fetcher_dict={
        "EstatStatisticalData": EstatStatisticalDataFetcher,
    },
    repr_name="e-Stat Japan Statistical Data API",
    instructions="Register for a free API key at: https://www.e-stat.go.jp/api/",
)
