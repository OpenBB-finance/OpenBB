"""提供者的自定义异常。"""

from openbb_core.app.model.abstract.error import OpenBBError


class EmptyDataError(OpenBBError):
    """空数据引发的异常。"""

    def __init__(
        self, message: str = "未找到结果。请尝试调整查询参数。"
    ):
        """初始化异常。"""
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(OpenBBError):
    """未经授权的提供者请求响应引发的异常。"""

    def __init__(
        self,
        message: str | tuple[str] = (
            "未经授权的 <provider name> API 请求。"
            "请检查您的 <provider name> 凭据和订阅访问权限。",
        ),
        provider_name: str = "<provider name>",
    ):
        """初始化异常。"""
        if provider_name and provider_name != "<provider name>":
            msg = message
            if isinstance(msg, tuple):
                msg = msg[0].replace("<provider name>", provider_name)
            elif isinstance(msg, str):
                msg = msg.replace("<provider name>", provider_name)
            message = msg
        self.message = message
        super().__init__(str(self.message))
