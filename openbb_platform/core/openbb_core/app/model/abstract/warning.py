"""警告模块。"""

from warnings import WarningMessage

from pydantic import BaseModel


class Warning_(BaseModel):
    """警告模型。"""

    category: str
    message: str


def cast_warning(w: WarningMessage) -> Warning_:
    """将警告转换为 pydantic 模型。"""
    return Warning_(
        category=w.category.__name__,
        message=str(w.message),
    )


class OpenBBWarning(Warning):
    """OpenBB 警告的基类。"""
