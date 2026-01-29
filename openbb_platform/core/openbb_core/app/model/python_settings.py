"""Python 配置设置模型。"""

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class PythonSettings(BaseModel):
    """Python 接口配置的设置模型。"""

    model_config = ConfigDict(extra="allow")

    docstring_sections: list[str] = Field(
        default_factory=lambda: ["description", "parameters", "returns", "examples"],
        description="要包含在自动生成文档字符串中的部分。",
    )
    docstring_max_length: PositiveInt | None = Field(
        default=None, description="自动生成文档字符串的最大长度。"
    )
    http: dict | None = Field(
        default_factory=dict,
        description="HTTP 设置涵盖内部实用函数发出的所有请求。"
        + " 该配置适用于 requests 和 aiohttp 库。"
        + "\n    "
        + """可用设置：
            - cafile: str - CA 证书文件的路径。
            - certfile: str - 客户端证书文件的路径。
            - keyfile: str - 客户端密钥文件的路径。
            - password: str - 客户端密钥文件的密码。# 仅限 aiohttp
            - verify_ssl: bool - 验证 SSL 证书。
            - fingerprint: str - SSL 指纹。# 仅限 aiohttp
            - proxy: str - 代理 URL。
            - proxy_auth: str | list - 代理身份验证。# 仅限 aiohttp
            - proxy_headers: dict - 代理头。# 仅限 aiohttp
            - timeout: int - 请求超时。
            - auth: str | list - 基本身份验证。
            - headers: dict - 请求头。
            - cookies: dict - 会话 Cookie 字典。

        提供的任何其他键都将被忽略，除非通过自定义代码显式实现。

        设置通过以下方式传递到 `requests.Session` 对象和 `aiohttp.ClientSession` 对象：
            - `openbb_core.provider.utils.helpers.make_request` - 同步
            - `openbb_core.provider.utils.helpers.amake_request` - 异步
            - `openbb_core.provider.utils.helpers.amake_requests` - 异步（多个请求）
            - 在 YFinance 和 Finviz 库实现中插入使用。

        通过以下方式返回应用了设置的会话对象：
            - `openbb_core.provider.utils.helpers.get_requests_session`
            - `openbb_core.provider.utils.helpers.get_async_requests_session`
        """,
    )
    uvicorn: dict | None = Field(
        default_factory=dict,
        description="Uvicorn 设置，涵盖使用以下入口点启动 FastAPI 时的所有设置："
        + "\n    "
        + """
            - 将 FastAPI 作为 Python 模块脚本运行。
              - python -m openbb_core.api.rest_api
            - 运行 `openbb-api` 命令。
                - openbb-api

        所有设置直接传递给 `uvicorn.run`，可以在 Uvicorn 文档中找到。
            - https://www.uvicorn.org/settings/

        提供给命令行的关键字参数将优先于此配置中的设置。
        """,
    )

    def __repr__(self) -> str:
        """返回模型的字符串表示形式。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
