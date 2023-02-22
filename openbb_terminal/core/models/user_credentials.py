from pydantic.dataclasses import dataclass


@dataclass(config=dict(validate_assignment=True))
class CredentialsModel:
    """Data model for credentials."""

    # To be implemented
