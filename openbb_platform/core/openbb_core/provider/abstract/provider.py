"""Provider Abstract Class."""

from typing import Dict, List, Optional, Type

from openbb_core.provider.abstract.fetcher import Fetcher


class Provider:
    """Serves as provider extension entry point and must be created by each provider."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        description: str,
        website: Optional[str] = None,
        credentials: Optional[List[str]] = None,
        fetcher_dict: Optional[Dict[str, Type[Fetcher]]] = None,
        repr_name: Optional[str] = None,
        deprecated_credentials: Optional[Dict[str, Optional[str]]] = None,
        instructions: Optional[str] = None,
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
        credentials : Optional[List[str]]
            List of required credentials, by default None.
        fetcher_dict : Optional[Dict[str, Type[Fetcher]]]
            Dictionary of fetchers, by default None.
        repr_name: Optional[str]
            Full name of the provider, by default None.
        deprecated_credentials: Optional[Dict[str, Optional[str]]]
            Map of deprecated credentials to its current name, by default None.
        instructions: Optional[str]
            Instructions on how to setup the provider. For example, how to get an API key.
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
        self.repr_name = repr_name
        self.deprecated_credentials = deprecated_credentials
        self.instructions = instructions
