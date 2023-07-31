"""Abstract class for providers."""

from typing import Dict, List, Optional, Type

from openbb_provider.abstract.fetcher import Fetcher


class Provider:
    """Abstract class for providers."""

    def __init__(
        self,
        name: str,
        description: str,
        required_credentials: Optional[List[str]],
        fetcher_dict: Dict[str, Type[Fetcher]],
    ) -> None:
        """Initialize the provider."""
        self.name = name
        self.description = description

        if required_credentials is None:
            self.required_credentials: List = []
        else:
            self.required_credentials = []
            for rq in required_credentials:
                self.required_credentials.append(f"{self.name.lower()}_{rq}")

        self.fetcher_dict = fetcher_dict
