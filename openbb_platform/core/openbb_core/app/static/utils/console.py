"""控制台模块。"""

from openbb_core.env import Env


class Console:
    """构建器和 linter 使用的控制台。"""

    def __init__(self, verbose: bool):
        """初始化控制台。"""
        self.verbose = verbose

    def log(self, message: str, **kwargs):
        """控制台日志方法。"""
        if self.verbose or Env().DEBUG_MODE:
            print(message, **kwargs)  # noqa: T201
