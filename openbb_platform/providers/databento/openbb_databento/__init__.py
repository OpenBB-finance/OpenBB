"""Databento provider module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_databento.models.futures_curve import (
    DatabentoFuturesCurveFetcher,
)
from openbb_databento.models.options_chains import (
    DatabentoOptionsChainsFetcher,
)

databento_provider = Provider(
    name="databento",
    website="https://www.databento.com/",
    description="""Databento.""",
    credentials=["api_key"],
    fetcher_dict={
        "FuturesCurve": DatabentoFuturesCurveFetcher,
        "OptionsChains": DatabentoOptionsChainsFetcher,
    },
)
