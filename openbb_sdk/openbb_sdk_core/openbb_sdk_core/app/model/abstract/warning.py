from warnings import WarningMessage

from pydantic import BaseModel


class Warning_(BaseModel):
    message: str
    category: str


def cast_warning(w: WarningMessage) -> Warning_:
    return Warning_(
        message=str(w.message),
        category=w.category.__name__,
    )
