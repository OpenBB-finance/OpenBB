from typing import List, Any
from pydantic import BaseModel, Field

from openbb_core.provider.abstract.data import Data

from pydantic import BaseModel, Field


class GARCModel(BaseModel):
    prediction: List[Data]
    forecast_model: Any = Field(
        default=None,
        description="The model object.",
        json_schema_extra={"exclude_from_api": True},
    )
