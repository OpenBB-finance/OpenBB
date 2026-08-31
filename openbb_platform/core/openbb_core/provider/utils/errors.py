"""Custom exceptions for the provider."""

from openbb_core.app.model.abstract.error import OpenBBError


class EmptyDataError(OpenBBError):
    """Exception raised for empty data."""

    def __init__(
        self, message: str = "No results found. Try adjusting the query parameters."
    ):
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


class MissingCredentialError(OpenBBError):
    """Exception raised when a required provider credential is not configured."""

    def __init__(
        self,
        provider: str,
        credential: str,
        message: str | None = None,
    ):
        """Initialize the exception.

        Parameters
        ----------
        provider : str
            Name of the provider, e.g. "eia".
        credential : str
            Name of the missing credential, e.g. "eia_api_key".
        message : str | None
            Optional human-readable message. Defaults to a standard message.
        """
        self.provider = provider
        self.credential = credential
        self.message = message or (
            f"Missing credential '{credential}' for provider '{provider}'. "
            "Refer to the documentation for setting provider credentials at "
            "https://docs.openbb.co/platform/settings/user_settings/api_keys."
        )
        super().__init__(self.message)


class UnauthorizedError(OpenBBError):
    """Exception raised for an unauthorized provider request response."""

    def __init__(
        self,
        message: str | tuple[str] = (
            "Unauthorized <provider name> API request."
            " Please check your <provider name> credentials and subscription access.",
        ),
        provider_name: str = "<provider name>",
    ):
        """Initialize the exception."""
        if provider_name and provider_name != "<provider name>":
            msg = message
            if isinstance(msg, tuple):
                msg = msg[0].replace("<provider name>", provider_name)
            elif isinstance(msg, str):
                msg = msg.replace("<provider name>", provider_name)
            message = msg
        self.message = message
        super().__init__(str(self.message))
