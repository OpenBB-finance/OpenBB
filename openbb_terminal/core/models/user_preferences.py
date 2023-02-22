from pydantic.dataclasses import dataclass


@dataclass(config=dict(validate_assignment=True))
class PreferencesModel:
    """Data model for preferences."""

    # To be implemented
