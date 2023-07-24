from typing import Optional

from pydantic import BaseModel


class Error(BaseModel):
    message: str
    error_kind: Optional[str] = None
