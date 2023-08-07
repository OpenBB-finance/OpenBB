from pydantic import ConfigDict, BaseModel


class QueryParams(BaseModel):
    """The OpenBB Standardized QueryParams Model that holds the query input parameters."""

    model_config = ConfigDict(populate_by_name=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"
