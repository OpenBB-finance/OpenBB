"""OpenBB 错误。"""


class OpenBBError(Exception):
    """OpenBB 错误。"""

    def __init__(self, original: str | Exception | None = None):
        """初始化 OpenBBError。"""
        self.original = original
        super().__init__(str(original))
