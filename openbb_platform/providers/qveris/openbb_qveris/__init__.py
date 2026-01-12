"""QVERISAI provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_qveris.models.tool_execute import QverisToolExecuteFetcher
from openbb_qveris.models.tool_search import QverisToolSearchFetcher

qveris_provider = Provider(
    name="qveris",
    website="https://qveris.ai",
    description="""QVERISAI is a third-party API tool platform that provides access to various
    tools for retrieving and processing data in fields such as finance, economics, healthcare,
    sports, scientific research, and more.""",
    credentials=["api_key"],
    fetcher_dict={
        "ToolExecute": QverisToolExecuteFetcher,
        "ToolSearch": QverisToolSearchFetcher,
    },
    repr_name="QVERISAI",
    instructions="""To use QVERISAI, you need to set the QVERIS_API_KEY environment variable
    with your API key. You can get an API key from https://qveris.ai""",
)
