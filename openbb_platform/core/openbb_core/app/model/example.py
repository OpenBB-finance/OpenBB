from typing import Any, Dict, Optional, Literal

from pydantic import BaseModel, ConfigDict


class Example(BaseModel):
    """Example model."""

    scope: Literal[
        "required", "standard", "other"
    ]  # Required parameters, standard parameters, or other
    description: Optional[str] = None
    parameters: Dict[str, Any]

    model_config = ConfigDict(validate_assignment=True)
