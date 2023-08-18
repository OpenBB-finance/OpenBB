from typing import Optional, Union

from pydantic import BaseModel


class Error(BaseModel):
    message: str
    error_kind: Optional[str] = None


class OpenBBError(Exception):
    """OpenBB Error."""

    def __init__(self, original: Optional[Union[str, Exception]] = None):
        self.original = original
        super().__init__(str(original))
