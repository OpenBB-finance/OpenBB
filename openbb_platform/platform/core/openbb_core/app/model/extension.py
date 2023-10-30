from typing import List, Optional


class Extension:
    """Serves as extension entry point and must be created by each extension package."""

    def __init__(
        self,
        name: str,
        required_credentials: Optional[List[str]] = None,
    ) -> None:
        """Initialize the extension.

        Parameters
        ----------
        name : str
            Name of the provider.
        required_credentials : Optional[List[str]], optional
            List of required credentials, by default None
        """
        self.name = name
        if required_credentials is None:
            self.required_credentials: List = []
        else:
            self.required_credentials = []
            for rq in required_credentials:
                self.required_credentials.append(f"{self.name.lower()}_{rq}")
