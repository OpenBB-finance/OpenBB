from pydantic import BaseModel, Extra


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.dict().items()])})"

    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True
