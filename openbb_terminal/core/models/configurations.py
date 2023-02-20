from pydantic.dataclasses import dataclass


@dataclass(config=dict(validate_assignment=True))
class ConfigurationsModel:
    """Data model for configurations."""

    # To be implemented


default_configurations = ConfigurationsModel()  # type: ignore
