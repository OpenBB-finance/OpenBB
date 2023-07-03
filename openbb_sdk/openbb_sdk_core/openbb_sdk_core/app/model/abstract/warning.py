from warnings import WarningMessage

from pydantic import BaseModel


class Warning_(BaseModel):
    category: str
    message: str


def cast_warning(w: WarningMessage) -> Warning_:
    return Warning_(
        category=w.category.__name__,
        message=str(w.message),
    )


class OpenBBWarning(Warning):
    pass
