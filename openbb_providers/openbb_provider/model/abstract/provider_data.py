# IMPORT STANDARD

# IMPORT THIRD-PARTY
from pydantic import BaseModel, Extra

# IMPORT INTERNAL


class ProviderData(BaseModel):
    """The Provider-specific data model."""

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True


class ProviderQueryParams(BaseModel):
    """The Provider-specific query parameter model."""

    def __post_init__(self):
        # check the fields that were received vs the fields that are allowed
        # if there are any fields that were received that are not allowed, raise an error
        allowed_fields = set(self.__fields__.keys())
        received_fields = set(self.__dict__.keys())
        if not received_fields.issubset(allowed_fields):
            raise ValueError(
                f"Received fields that are not allowed: {received_fields - allowed_fields}"
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"
