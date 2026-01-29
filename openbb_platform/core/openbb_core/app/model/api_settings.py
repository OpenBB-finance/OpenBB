"""FastAPI 配置设置模型。"""

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Cors(BaseModel):
    """FastAPI 配置的 Cors 模型。"""

    model_config = ConfigDict(frozen=True)

    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])


class Servers(BaseModel):
    """FastAPI 配置的 Servers 模型。"""

    model_config = ConfigDict(frozen=True)

    url: str = ""
    description: str = "本地 OpenBB 开发服务器"


class APISettings(BaseModel):
    """FastAPI 配置的设置模型。"""

    model_config = ConfigDict(frozen=True)

    version: str = "1"
    title: str = "OpenBB Platform API"
    description: str = "为每个人，在任何地方提供投资研究。"
    terms_of_service: str = "http://example.com/terms/"
    contact_name: str = "OpenBB Team"
    contact_url: str = "https://openbb.co"
    contact_email: str = "hello@openbb.co"
    license_name: str = "AGPLv3"
    license_url: str = "https://github.com/OpenBB-finance/OpenBB/blob/develop/LICENSE"
    servers: list[Servers] = Field(default_factory=lambda: [Servers()])
    cors: Cors = Field(default_factory=Cors)
    custom_headers: dict[str, str] | None = Field(
        default=None, description="自定义标头及其各自的默认值。"
    )

    @computed_field  # type: ignore[misc]
    @property
    def prefix(self) -> str:
        """返回 API 前缀。"""
        return f"/api/v{self.version}"

    def __repr__(self) -> str:
        """返回模型的字符串表示形式。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
