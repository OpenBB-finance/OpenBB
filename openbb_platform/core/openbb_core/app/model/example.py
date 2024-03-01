from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class Example(BaseModel):
    """Example model."""

    scope: Literal["api", "python"] = "api"
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    code: Optional[List[str]] = None

    model_config = ConfigDict(validate_assignment=True)
