"""Abstract class for providers."""

from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher


class Provider:
    """Abstract class for providers."""

    def __init__(
        self,
        name: str,
        description: str,
        required_credentials: Optional[List[str]],
        fetcher_dict: Dict[str, Fetcher],
    ) -> None:
        """Initialize the provider."""
        self.name = name
        self.description = description

        self.required_credentials = required_credentials
        self.formatted_credentials = []
        if required_credentials is not None:
            for rq in required_credentials:
                self.formatted_credentials.append(f"{self.name.lower()}_{rq}")

        self.fetcher_dict = fetcher_dict
