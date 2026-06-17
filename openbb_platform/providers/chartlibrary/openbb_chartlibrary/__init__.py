"""ChartLibrary provider module."""

from openbb_chartlibrary.models.pattern_similarity import (
    ChartLibraryPatternSimilarityFetcher,
)
from openbb_core.provider.abstract.provider import Provider

chartlibrary_provider = Provider(
    name="chartlibrary",
    website="https://chartlibrary.io",
    description="""ChartLibrary provides historical chart pattern similarity search
using embedding-based matches across US equities.""",
    credentials=["api_key"],
    fetcher_dict={
        "ChartPatternSimilarity": ChartLibraryPatternSimilarityFetcher,
    },
    repr_name="ChartLibrary",
)
