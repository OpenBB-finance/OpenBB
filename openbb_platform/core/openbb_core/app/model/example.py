from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class Example(BaseModel):
    """Example model."""

    description: Optional[str] = None
    parameters: Dict[str, Any]

    model_config = ConfigDict(validate_assignment=True)
