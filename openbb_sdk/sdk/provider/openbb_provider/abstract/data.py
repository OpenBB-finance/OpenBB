import re

from pydantic import BaseModel, Extra


def to_snake_case(string: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        return {to_snake_case(k): v for k, v in original_dict.items()}

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True
