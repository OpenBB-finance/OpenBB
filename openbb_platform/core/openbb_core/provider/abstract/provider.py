"""Provider Abstract Class."""

from typing import Dict, List, Optional, Type

from openbb_core.provider.abstract.fetcher import Fetcher


class Provider:
    """Serves as provider extension entry point and must be created by each provider."""

    def __init__(
        self,
        name: str,
        description: str,
        website: Optional[str] = None,
        credentials: Optional[List[str]] = None,
        fetcher_dict: Optional[Dict[str, Type[Fetcher]]] = None,
    ) -> None:
        """Initialize the provider.

        Parameters
        ----------
        name : str
            Name of the provider.
        description : str
            Description of the provider.
        website : Optional[str]
            Website of the provider, by default None.
        credentials : Optional[List[str]], optional
            List of required credentials, by default None
        fetcher_dict : Optional[Dict[str, Type[Fetcher]]]
            Dictionary of fetchers, by default None.
        """
        self.name = name
        self.description = description
        self.website = website
        self.fetcher_dict = fetcher_dict or {}
        if credentials is None:
            self.credentials: List = []
        else:
            self.credentials = []
            for c in credentials:
                self.credentials.append(f"{self.name.lower()}_{c}")
