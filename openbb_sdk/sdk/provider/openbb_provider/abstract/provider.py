"""Abstract class for providers."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher


class Provider:
    """Abstract class for providers."""

    QUERIES = ["get_query_type", "get_provider_query_type"]

    def __init__(
        self,
        name: str,
        description: str,
        required_credentials: Optional[List[str]],
        fetcher_list: List[Fetcher],
    ) -> None:
        """Initialize the provider.

        Parameters
        ----------
        name : str
            The name of the provider.
        description : str
            The description of the provider.
        required_credentials : Optional[List[str]]
            The list of required credentials for the provider.
            For example, ["api_key", "api_secret"] which would be used inside
            the fetcher to get the credentials from the credentials dict.
            For example credentials.get("PROVIDER_API_KEY").
        fetcher_list : List[Fetcher]
            The list of fetchers that the provider supports.
        """
        self.name = name
        self.description = description
        self.required_credentials = required_credentials
        the_dict: Dict[str, Any] = {}
        for query in self.QUERIES:
            the_dict[query] = {getattr(x, query)().__name__: x for x in fetcher_list}
        self.fetcher_dict = the_dict
        # This is used only for documentation generation
        self.fetcher_list = fetcher_list
