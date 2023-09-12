"""The OpenBB Standardized QueryParams Model that holds the query input parameters."""
from typing import Dict

from pydantic import BaseModel, ConfigDict, alias_generators


class QueryParams(BaseModel):
    """The OpenBB Standardized QueryParams Model that holds the query input parameters."""

    __alias_dict__: Dict[str, str] = {}

    def __repr__(self):
        """Return the string representation of the QueryParams object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.model_dump().items()])})"

    model_config = ConfigDict(
        extra="allow", populate_by_name=True, alias_generator=alias_generators.to_snake
    )
