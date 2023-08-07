from pydantic import ConfigDict, BaseModel


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"

    model_config = ConfigDict(extra="allow", populate_by_name=True)
