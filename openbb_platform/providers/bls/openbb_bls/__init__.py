"""BLS Provider Module."""

from openbb_bls.models.search import BlsSearchFetcher
from openbb_bls.models.series import BlsSeriesFetcher
from openbb_core.provider.abstract.provider import Provider

bls_provider = Provider(
    name="bls",
    website="https://www.bls.gov/developers/api_signature_v2.htm",
    description="The Bureau of Labor Statistics' (BLS) Public Data Application Programming Interface (API)"
    + " gives the public access to economic data from all BLS programs."
    + " It is the Bureau's hope that talented developers and programmers will use the BLS Public Data API to create"
    + " original, inventive applications with published BLS data.",
    credentials=["api_key"],
    fetcher_dict={
        "BlsSearch": BlsSearchFetcher,
        "BlsSeries": BlsSeriesFetcher,
    },
    repr_name="Bureau of Labor Statistics' (BLS) Public Data API",
    instructions="Sign up for a free API key here: https://data.bls.gov/registrationEngine/",
)
