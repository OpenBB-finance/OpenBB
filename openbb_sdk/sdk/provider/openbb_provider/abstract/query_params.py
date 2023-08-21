"""The OpenBB Standardized QueryParams Model that holds the query input parameters."""
from pydantic import BaseModel

from openbb_provider.utils.helpers import to_snake_case


class QueryParams(BaseModel):
    """The OpenBB Standardized QueryParams Model that holds the query input parameters."""

    class Config:
        """Pydantic Config."""

        allow_population_by_field_name = True
        alias_generator = to_snake_case

    def __repr__(self):
        """Return the string representation of the QueryParams object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"
