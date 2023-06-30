from typing import Optional

from pydantic import BaseModel


class Credentials(BaseModel):
    fmp_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    benzinga_api_key: Optional[str] = None

    class Config:
        validate_assignment = True
